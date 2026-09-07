import os
import requests
from collections import Counter

USERNAME = "prasadmanishdev08"
TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

API = "https://api.github.com"

os.makedirs("assets", exist_ok=True)


def github_get(url, params=None):
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


# =========================================================
# USER INFORMATION
# =========================================================

user = github_get(f"{API}/users/{USERNAME}")

followers = user.get("followers", 0)
following = user.get("following", 0)
public_repos = user.get("public_repos", 0)


# =========================================================
# REPOSITORY INFORMATION
# =========================================================

repos = github_get(
    f"{API}/users/{USERNAME}/repos",
    {
        "per_page": 100,
        "sort": "updated"
    }
)

total_stars = sum(
    repo.get("stargazers_count", 0)
    for repo in repos
)

total_forks = sum(
    repo.get("forks_count", 0)
    for repo in repos
)

languages = Counter()

for repo in repos:
    language = repo.get("language")

    if language:
        languages[language] += 1


# =========================================================
# CONTRIBUTION CALENDAR
# =========================================================

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    headers=HEADERS,
    json={
        "query": query,
        "variables": {
            "login": USERNAME
        }
    },
    timeout=30
)

response.raise_for_status()

data = response.json()

if "errors" in data:
    raise RuntimeError(data["errors"])

calendar = (
    data["data"]
    ["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)

total_contributions = calendar["totalContributions"]
weeks = calendar["weeks"]


# =========================================================
# GITHUB STATISTICS SVG
# =========================================================

stats_svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="850"
height="360"
viewBox="0 0 850 360">

<rect
width="850"
height="360"
rx="18"
fill="#0d1117"
stroke="#30363d"/>

<text
x="40"
y="55"
fill="#58a6ff"
font-family="Arial, sans-serif"
font-size="26"
font-weight="bold">
GitHub Statistics
</text>

<text
x="40"
y="85"
fill="#8b949e"
font-family="Arial, sans-serif"
font-size="15">
@{USERNAME}
</text>

<line
x1="40"
y1="110"
x2="810"
y2="110"
stroke="#30363d"/>


<text
x="60"
y="150"
fill="#8b949e"
font-family="Arial"
font-size="15">
Public Repositories
</text>

<text
x="60"
y="185"
fill="#f0f6fc"
font-family="Arial"
font-size="30"
font-weight="bold">
{public_repos}
</text>


<text
x="300"
y="150"
fill="#8b949e"
font-family="Arial"
font-size="15">
Followers
</text>

<text
x="300"
y="185"
fill="#f0f6fc"
font-family="Arial"
font-size="30"
font-weight="bold">
{followers}
</text>


<text
x="520"
y="150"
fill="#8b949e"
font-family="Arial"
font-size="15">
Following
</text>

<text
x="520"
y="185"
fill="#f0f6fc"
font-family="Arial"
font-size="30"
font-weight="bold">
{following}
</text>


<text
x="60"
y="235"
fill="#8b949e"
font-family="Arial"
font-size="15">
Total Stars
</text>

<text
x="60"
y="270"
fill="#f0f6fc"
font-family="Arial"
font-size="30"
font-weight="bold">
{total_stars}
</text>


<text
x="300"
y="235"
fill="#8b949e"
font-family="Arial"
font-size="15">
Total Forks
</text>

<text
x="300"
y="270"
fill="#f0f6fc"
font-family="Arial"
font-size="30"
font-weight="bold">
{total_forks}
</text>


<text
x="520"
y="235"
fill="#8b949e"
font-family="Arial"
font-size="15">
Contributions
</text>

<text
x="520"
y="270"
fill="#58a6ff"
font-family="Arial"
font-size="30"
font-weight="bold">
{total_contributions}
</text>


<text
x="40"
y="325"
fill="#6e7681"
font-family="Arial"
font-size="12">
Generated automatically by GitHub Actions
</text>

</svg>
"""


with open(
    "assets/github-stats.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(stats_svg)


# =========================================================
# CONTRIBUTION GRAPH SVG
# =========================================================

cell = 12
gap = 3

left = 40
top = 75

calendar_width = left + len(weeks) * (cell + gap) + 40
calendar_height = 180


def contribution_color(count):

    if count == 0:
        return "#161b22"

    if count <= 2:
        return "#0e4429"

    if count <= 5:
        return "#006d32"

    if count <= 9:
        return "#26a641"

    return "#39d353"


contribution_svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{calendar_width}"
height="{calendar_height}"
viewBox="0 0 {calendar_width} {calendar_height}">

<rect
width="100%"
height="100%"
rx="18"
fill="#0d1117"
stroke="#30363d"/>

<text
x="30"
y="35"
fill="#f0f6fc"
font-family="Arial"
font-size="20"
font-weight="bold">
Contribution Activity
</text>

<text
x="30"
y="55"
fill="#8b949e"
font-family="Arial"
font-size="12">
{total_contributions} contributions in the last year
</text>
"""


for week_index, week in enumerate(weeks):

    for day_index, day in enumerate(
        week["contributionDays"]
    ):

        count = day["contributionCount"]

        x = left + week_index * (cell + gap)
        y = top + day_index * (cell + gap)

        color = contribution_color(count)

        contribution_svg += f"""
<rect
x="{x}"
y="{y}"
width="{cell}"
height="{cell}"
rx="2"
fill="{color}">

<title>
{day["date"]}: {count} contributions
</title>

</rect>
"""


contribution_svg += """

</svg>
"""


with open(
    "assets/contributions.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(contribution_svg)


print("==========================================")
print("GitHub profile graphics generated!")
print("==========================================")
print(f"Username:       {USERNAME}")
print(f"Repositories:   {public_repos}")
print(f"Followers:      {followers}")
print(f"Following:      {following}")
print(f"Stars:          {total_stars}")
print(f"Forks:          {total_forks}")
print(f"Contributions:  {total_contributions}")
print("==========================================")
