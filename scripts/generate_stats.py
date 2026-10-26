"""Generates assets/stats.svg and assets/streak.svg from the GitHub GraphQL API.
Usage:  GITHUB_TOKEN=... GH_USER=Hitesh754 python3 scripts/generate_stats.py
        python3 scripts/generate_stats.py --placeholder   (no network, empty cards)
"""
import datetime as dt
import json
import os
import sys
import urllib.request

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
PANEL, BORDER, GREEN, TEXT, MUTED, BLUE = "#0d1526", "#1c2740", "#34f5b0", "#e6edf7", "#8a97b2", "#7aa2ff"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def gql(token, query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]


def fetch(token, user):
    base = gql(token, f'''{{ user(login:"{user}") {{
        name
        contributionsCollection {{ contributionYears }}
        pullRequests {{ totalCount }}
        issues {{ totalCount }}
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{ totalCount nodes {{ stargazerCount }} }}
    }} }}''')["user"]
    years = base["contributionsCollection"]["contributionYears"]
    parts = "".join(
        f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", to:"{y}-12-31T23:59:59Z") {{'
        f'totalCommitContributions contributionCalendar {{ weeks {{ contributionDays {{ date contributionCount }} }} }} }} '
        for y in years
    )
    per_year = gql(token, f'{{ user(login:"{user}") {{ {parts} }} }}')["user"]
    days, commits = {}, 0
    for y in years:
        c = per_year[f"y{y}"]
        commits += c["totalCommitContributions"]
        for wk in c["contributionCalendar"]["weeks"]:
            for d in wk["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    stars = sum(n["stargazerCount"] for n in base["repositories"]["nodes"])
    return {
        "name": base["name"] or user,
        "stars": stars,
        "commits": commits,
        "prs": base["pullRequests"]["totalCount"],
        "issues": base["issues"]["totalCount"],
        "repos": base["repositories"]["totalCount"],
        "days": days,
    }


def streaks(days):
    today = dt.date.today()
    dates = sorted(dt.date.fromisoformat(d) for d in days if dt.date.fromisoformat(d) <= today)
    total = sum(days.values())
    longest = run = 0
    prev = None
    best_end = None
    for d in dates:
        if days[d.isoformat()] > 0:
            run = run + 1 if prev and (d - prev).days == 1 and days[prev.isoformat()] > 0 else 1
            if run > longest:
                longest, best_end = run, d
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
    score = s["commits"] * 0.25 + s["prs"] * 2 + s["issues"] * 1 + s["stars"] * 1.5 + s["repos"] * 0.5
    for limit, g in [(400, "S"), (200, "A+"), (100, "A"), (50, "B+"), (25, "B")]:
        if score >= limit:
            return g, min(score / 400, 1)
    return "C", max(score / 400, 0.05)


def card_open(w, h, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>')


def stats_svg(s):
    g, frac = grade(s)
    circ = 2 * 3.14159 * 40
    rows = [("Total Stars", s["stars"]), ("Total Commits", s["commits"]), ("Total PRs", s["prs"]),
            ("Total Issues", s["issues"]), ("Public Repos", s["repos"])]
    out = card_open(490, 220, "GitHub stats")
    out += f'<text x="28" y="44" font-family="{FONT}" font-size="20" font-weight="700" fill="{GREEN}">{s["name"]}\'s GitHub Stats</text>'
    for i, (k, v) in enumerate(rows):
        y = 82 + i * 28
        out += (f'<circle cx="34" cy="{y-5}" r="4" fill="{BLUE}"/>'
                f'<text x="50" y="{y}" font-family="{FONT}" font-size="15" fill="{TEXT}">{k}:</text>'
                f'<text x="230" y="{y}" font-family="{FONT}" font-size="15" font-weight="700" fill="{TEXT}">{v}</text>')
    out += (f'<g transform="translate(385,122)"><circle r="40" fill="none" stroke="{BORDER}" stroke-width="8"/>'
            f'<circle r="40" fill="none" stroke="{GREEN}" stroke-width="8" stroke-linecap="round" '
            f'stroke-dasharray="{circ*frac:.1f} {circ:.1f}" transform="rotate(-90)"/>'
            f'<text y="9" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="700" fill="{TEXT}">{g}</text></g>'
            f'<text x="385" y="190" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">rank</text></svg>')
    return out


def streak_svg(total, cur, longest):
    out = card_open(490, 220, "Contribution streak")
    cols = [(95, total, "Total Contributions", TEXT), (245, cur, "Current Streak", GREEN), (395, longest, "Longest Streak", TEXT)]
    out += f'<line x1="170" y1="50" x2="170" y2="170" stroke="{BORDER}"/><line x1="320" y1="50" x2="320" y2="170" stroke="{BORDER}"/>'
    for x, v, label, color in cols:
        if label == "Current Streak":
            out += f'<circle cx="{x}" cy="100" r="42" fill="none" stroke="{GREEN}" stroke-width="5"/>'
        out += (f'<text x="{x}" y="{108 if label=="Current Streak" else 105}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="700" fill="{color}">{v}</text>'
                f'<text x="{x}" y="{170 if label=="Current Streak" else 150}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED if label!="Current Streak" else GREEN}">{label}</text>')
    out += f'<text x="245" y="205" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">days in a row</text></svg>'
    return out


def main():
    if "--placeholder" in sys.argv:
        s = {"name": "Hitesh Choudhary", "stars": "-", "commits": "-", "prs": "-", "issues": "-", "repos": "-"}
        circ = 0
        stats = stats_svg({"name": s["name"], "stars": 0, "commits": 0, "prs": 0, "issues": 0, "repos": 0})
        for k in ("stars", "commits", "prs", "issues", "repos"):
            pass
        streak = streak_svg("-", "-", "-")
    else:
        s = fetch(os.environ["GITHUB_TOKEN"], os.environ.get("GH_USER", "Hitesh754"))
        total, cur, longest = streaks(s["days"])
        stats, streak = stats_svg(s), streak_svg(total, cur, longest)
    os.makedirs(ASSETS, exist_ok=True)
    open(os.path.join(ASSETS, "stats.svg"), "w").write(stats)
    open(os.path.join(ASSETS, "streak.svg"), "w").write(streak)
    print("wrote stats.svg and streak.svg")


if __name__ == "__main__":
    main()
