import requests
from bs4 import BeautifulSoup
import os
import argparse
import sys

def get_trending_repos():
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Error fetching trending: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        repos = []
        # Each repo is in an <article class="Box-row">
        for article in soup.find_all('article', class_='Box-row'):
            h2 = article.find('h2', class_='h3')
            if h2:
                a = h2.find('a')
                if a:
                    repo_full_name = a['href'].strip('/')
                    repos.append(repo_full_name)
        return repos
    except Exception as e:
        print(f"An error occurred while fetching trending repos: {e}")
        return []

def fork_repo(repo_full_name, token, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Forking {repo_full_name}...")
        return True

    print(f"Forking {repo_full_name}...")
    url = f"https://api.github.com/repos/{repo_full_name}/forks"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.post(url, headers=headers, timeout=30)
        if response.status_code in [202, 201, 200]:
            print(f"Successfully started fork of {repo_full_name}")
            return True
        else:
            print(f"Failed to fork {repo_full_name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"An error occurred while forking {repo_full_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Fork trending GitHub repositories.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without actual forking.")
    parser.add_argument("--count", type=int, default=3, help="Number of trending repos to fork.")
    args = parser.parse_args()

    token = os.getenv("GH_PAT")
    if not token and not args.dry_run:
        print("Error: GH_PAT environment variable is not set.")
        sys.exit(1)

    trending = get_trending_repos()
    if not trending:
        print("No trending repositories found.")
        sys.exit(0)

    to_fork = trending[:args.count]
    print(f"Found trending repos: {', '.join(to_fork)}")

    for repo in to_fork:
        fork_repo(repo, token, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
