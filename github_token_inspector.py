import argparse
import json
import os
import sys
import time
import requests

API_URL = "https://api.github.com/user"

def split_scopes(s):
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]

def main():
    p = argparse.ArgumentParser(prog="github_token_inspector")
    p.add_argument("--token", help="GitHub API token (or set GITHUB_TOKEN)")
    p.add_argument("--timeout", type=float, default=10.0)
    args = p.parse_args()

    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        out = {"valid": False, "error": {"message": "Missing token. Provide --token or set GITHUB_TOKEN."}}
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(2)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-token-inspector",
    }

    t0 = time.time()
    try:
        r = requests.get(API_URL, headers=headers, timeout=args.timeout)
    except requests.exceptions.Timeout:
        out = {"valid": False, "error": {"message": "Request timed out"}}
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        out = {"valid": False, "error": {"message": "Network error", "detail": str(e)}}
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(1)

    ms = int((time.time() - t0) * 1000)

    scopes = split_scopes(r.headers.get("X-OAuth-Scopes"))
    accepted_scopes = split_scopes(r.headers.get("X-Accepted-OAuth-Scopes"))

    rate = {
        "limit": r.headers.get("X-RateLimit-Limit"),
        "remaining": r.headers.get("X-RateLimit-Remaining"),
        "reset": r.headers.get("X-RateLimit-Reset"),
        "resource": r.headers.get("X-RateLimit-Resource"),
    }

    base = {
        "ok": r.ok,
        "status": r.status_code,
        "endpoint": "/user",
        "response_time_ms": ms,
        "scopes": scopes,
        "accepted_scopes_for_endpoint": accepted_scopes,
        "rate_limit": rate,
    }

    if r.status_code == 200:
        data = r.json()
        user = {
            "login": data.get("login"),
            "id": data.get("id"),
            "type": data.get("type"),
            "name": data.get("name"),
            "company": data.get("company"),
            "blog": data.get("blog"),
            "location": data.get("location"),
            "email": data.get("email"),
            "public_repos": data.get("public_repos"),
            "followers": data.get("followers"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }
        out = {"valid": True, "user": user, "meta": base}
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(0)

    try:
        err = r.json()
    except ValueError:
        err = {"message": r.text.strip() if r.text else "Unknown error"}

    out = {"valid": False, "error": {"message": err.get("message"), "status": r.status_code}, "meta": {"endpoint": "/user"}}
    print(json.dumps(out, ensure_ascii=False))

    if r.status_code in (401, 403):
        sys.exit(3)
    sys.exit(1)

if __name__ == "__main__":
    main()
