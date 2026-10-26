"""Generates assets/stats.svg and assets/streak.svg from the GitHub GraphQL API.
Usage:  GITHUB_TOKEN=... GH_USER=Hitesh754 python3 scripts/generate_stats.py
        python3 scripts/generate_stats.py --placeholder   (no network, placeholder cards)
"""
import datetime as dt
import html
import json
import os
import sys
import time
import urllib.error
import urllib.request

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
PANEL, BORDER, GREEN, TEXT, MUTED, BLUE = "#0d1526", "#1c2740", "#34f5b0", "#e6edf7", "#8a97b2", "#7aa2ff"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def gql(token, query, retries=3, backoff_factor=2):
    """Execute a GitHub GraphQL query with retry logic and detailed error reporting.
    Never prints or leaks the token.
    """
    url = "https://api.github.com/graphql"
    payload = json.dumps({"query": query}).encode("utf-8")
    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "profile-stats",
    }
    req = urllib.request.Request(url, data=payload, headers=headers)

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
            if "errors" in data and not data.get("data"):
                error_msgs = "; ".join(e.get("message", "Unknown error") for e in data["errors"])
                sys.stderr.write(f"GitHub GraphQL error: {error_msgs}\n")
                sys.exit(1)
            elif "errors" in data:
                error_msgs = "; ".join(e.get("message", "Unknown error") for e in data["errors"])
                sys.stderr.write(f"Warning: GraphQL returned partial errors: {error_msgs}\n")
            return data["data"]
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {e.code} ({e.reason}): {body}"
            # Retry on transient server errors or rate limiting
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                sleep_time = backoff_factor ** attempt
                sys.stderr.write(f"API attempt {attempt} failed ({e.code}). Retrying in {sleep_time}s...\n")
                time.sleep(sleep_time)
                continue
            sys.stderr.write(f"GitHub API HTTP error {last_error}\n")
            sys.exit(1)
        except urllib.error.URLError as e:
            last_error = f"Connection error: {e.reason}"
            if attempt < retries:
                sleep_time = backoff_factor ** attempt
                sys.stderr.write(f"Network attempt {attempt} failed ({e.reason}). Retrying in {sleep_time}s...\n")
                time.sleep(sleep_time)
                continue
            sys.stderr.write(f"GitHub API network failure: {last_error}\n")
            sys.exit(1)

    sys.stderr.write(f"GitHub API query failed after {retries} retries: {last_error}\n")
    sys.exit(1)


def fetch(token, user):
    """Fetch user profile metadata, public repository stars, and contribution calendar across years."""
    # Step 1: Fetch user metadata, contribution years, issues, PRs, and initial repositories
    base_query = f'''{{
        user(login: "{user}") {{
            name
            contributionsCollection {{
                contributionYears
            }}
            pullRequests {{
                totalCount
            }}
            issues {{
                totalCount
            }}
            repositories(ownerAffiliations: [OWNER], privacy: PUBLIC, first: 100) {{
                totalCount
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    stargazerCount
                }}
            }}
        }}
    }}'''

    base_data = gql(token, base_query)
    user_info = base_data.get("user")
    if not user_info:
        sys.stderr.write(f"Error: User '{user}' was not found via GitHub API.\n")
        sys.exit(1)

    repos_conn = user_info.get("repositories", {})
    stars = sum(n.get("stargazerCount", 0) for n in repos_conn.get("nodes", []))
    total_repos = repos_conn.get("totalCount", 0)

    # Paginate repositories if user has more than 100 public repositories
    page_info = repos_conn.get("pageInfo", {})
    while page_info.get("hasNextPage"):
        cursor = page_info.get("endCursor")
        page_query = f'''{{
            user(login: "{user}") {{
                repositories(ownerAffiliations: [OWNER], privacy: PUBLIC, first: 100, after: "{cursor}") {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        stargazerCount
                    }}
                }}
            }}
        }}'''
        page_data = gql(token, page_query)
        p_repos = page_data.get("user", {}).get("repositories", {})
        stars += sum(n.get("stargazerCount", 0) for n in p_repos.get("nodes", []))
        page_info = p_repos.get("pageInfo", {})

    # Step 2: Fetch contributions year by year
    years = user_info.get("contributionsCollection", {}).get("contributionYears", [])
    now = dt.datetime.now(dt.timezone.utc)
    if not years:
        years = [now.year]

    days = {}
    commits = 0
    for y in years:
        from_str = f"{y}-01-01T00:00:00Z"
        to_str = f"{y}-12-31T23:59:59Z"
        year_query = f'''{{
            user(login: "{user}") {{
                contributionsCollection(from: "{from_str}", to: "{to_str}") {{
                    totalCommitContributions
                    contributionCalendar {{
                        weeks {{
                            contributionDays {{
                                date
                                contributionCount
                            }}
                        }}
                    }}
                }}
            }}
        }}'''
        year_data = gql(token, year_query)
        col = year_data.get("user", {}).get("contributionsCollection")
        if col:
            commits += col.get("totalCommitContributions", 0)
            cal = col.get("contributionCalendar", {})
            for wk in cal.get("weeks", []):
                for d in wk.get("contributionDays", []):
                    days[d["date"]] = d.get("contributionCount", 0)

    return {
        "name": user_info.get("name") or user,
        "stars": stars,
        "commits": commits,
        "prs": user_info.get("pullRequests", {}).get("totalCount", 0),
        "issues": user_info.get("issues", {}).get("totalCount", 0),
        "repos": total_repos,
        "days": days,
    }


def streaks(days):
    """Calculate total contributions, current active streak, and longest streak."""
    today = dt.datetime.now(dt.timezone.utc).date()
    dates = sorted(dt.date.fromisoformat(d) for d in days if dt.date.fromisoformat(d) <= today)
    total = sum(days.get(d.isoformat(), 0) for d in dates)
    longest = run = 0
    prev = None
    for d in dates:
        cnt = days.get(d.isoformat(), 0)
        if cnt > 0:
            run = run + 1 if prev and (d - prev).days == 1 and days.get(prev.isoformat(), 0) > 0 else 1
            if run > longest:
                longest = run
        else:
            run = 0
        prev = d

    cur, d = 0, today
    if days.get(d.isoformat(), 0) == 0:
        d -= dt.timedelta(days=1)  # today may not be finished yet
    while days.get(d.isoformat(), 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)

    return total, cur, longest


def grade(s):
    """Calculate rank grade (S, A+, A, B+, B, C) and progress fraction."""
    try:
        score = (float(s["commits"]) * 0.25 +
                 float(s["prs"]) * 2.0 +
                 float(s["issues"]) * 1.0 +
                 float(s["stars"]) * 1.5 +
                 float(s["repos"]) * 0.5)
    except (ValueError, TypeError, KeyError):
        return "-", 0.0

    for limit, g in [(400, "S"), (200, "A+"), (100, "A"), (50, "B+"), (25, "B")]:
        if score >= limit:
            return g, min(score / 400.0, 1.0)
    return "C", max(score / 400.0, 0.05)


def card_open(w, h, label):
    safe_label = html.escape(label)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{safe_label}">'
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>'
    )


def stats_svg(s):
    """Render the stats SVG card."""
    g, frac = grade(s)
    circ = 2 * 3.14159265 * 40
    rows = [
        ("Total Stars", s["stars"]),
        ("Total Commits", s["commits"]),
        ("Total PRs", s["prs"]),
        ("Total Issues", s["issues"]),
        ("Public Repos", s["repos"]),
    ]
    safe_name = html.escape(str(s["name"]))
    out = card_open(490, 220, "GitHub stats")
    out += f'<text x="28" y="44" font-family="{FONT}" font-size="20" font-weight="700" fill="{GREEN}">{safe_name}\'s GitHub Stats</text>'
    for i, (k, v) in enumerate(rows):
        y = 82 + i * 28
        out += (
            f'<circle cx="34" cy="{y-5}" r="4" fill="{BLUE}"/>'
            f'<text x="50" y="{y}" font-family="{FONT}" font-size="15" fill="{TEXT}">{k}:</text>'
            f'<text x="230" y="{y}" font-family="{FONT}" font-size="15" font-weight="700" fill="{TEXT}">{html.escape(str(v))}</text>'
        )
    dash_val = f"{circ * frac:.1f}" if frac > 0 else "0"
    out += (
        f'<g transform="translate(385,122)"><circle r="40" fill="none" stroke="{BORDER}" stroke-width="8"/>'
        f'<circle r="40" fill="none" stroke="{GREEN}" stroke-width="8" stroke-linecap="round" '
        f'stroke-dasharray="{dash_val} {circ:.1f}" transform="rotate(-90)"/>'
        f'<text y="9" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="700" fill="{TEXT}">{g}</text></g>'
        f'<text x="385" y="190" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">rank</text></svg>'
    )
    return out


def streak_svg(total, cur, longest):
    """Render the contribution streak SVG card."""
    out = card_open(490, 220, "Contribution streak")
    cols = [
        (95, total, "Total Contributions", TEXT),
        (245, cur, "Current Streak", GREEN),
        (395, longest, "Longest Streak", TEXT),
    ]
    out += f'<line x1="170" y1="50" x2="170" y2="170" stroke="{BORDER}"/><line x1="320" y1="50" x2="320" y2="170" stroke="{BORDER}"/>'
    for x, v, label, color in cols:
        safe_v = html.escape(str(v))
        if label == "Current Streak":
            out += f'<circle cx="{x}" cy="100" r="42" fill="none" stroke="{GREEN}" stroke-width="5"/>'
        out += (
            f'<text x="{x}" y="{108 if label == "Current Streak" else 105}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="700" fill="{color}">{safe_v}</text>'
            f'<text x="{x}" y="{170 if label == "Current Streak" else 150}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED if label != "Current Streak" else GREEN}">{label}</text>'
        )
    out += f'<text x="245" y="205" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">days in a row</text></svg>'
    return out


def main():
    if "--placeholder" in sys.argv:
        # Generate placeholder cards without network calls (useful for offline / UI layout checks)
        s = {"name": "Hitesh Choudhary", "stars": "-", "commits": "-", "prs": "-", "issues": "-", "repos": "-"}
        stats = stats_svg(s)
        streak = streak_svg("-", "-", "-")
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.stderr.write("Error: GITHUB_TOKEN environment variable is not set.\n")
            sys.exit(1)
        user = os.environ.get("GH_USER", "Hitesh754")
        s = fetch(token, user)
        total, cur, longest = streaks(s["days"])
        stats, streak = stats_svg(s), streak_svg(total, cur, longest)

    os.makedirs(ASSETS, exist_ok=True)
    stats_path = os.path.join(ASSETS, "stats.svg")
    streak_path = os.path.join(ASSETS, "streak.svg")

    with open(stats_path, "w", encoding="utf-8") as f:
        f.write(stats)
    with open(streak_path, "w", encoding="utf-8") as f:
        f.write(streak)
    print("wrote stats.svg and streak.svg")


if __name__ == "__main__":
    main()
