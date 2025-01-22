import csv
import os
import requests
import sys
import git
from typing import List

REPOS_DIR = "bare_repos"
CSV_FILE = "commits.csv"


class CommitFileStat:
    def __init__(self, filename: str, add_lines: int, del_lines: int):
        self.filename = filename
        self.add_lines = add_lines
        self.del_lines = del_lines


class CommitInfo:
    def __init__(
        self,
        repo_name: str,
        sha_1_hash: str,
        author: str,
        date: str,
        message: str,
        file_stats: List[CommitFileStat],
    ):
        self.repo_name = repo_name
        self.sha_1_hash = sha_1_hash
        self.author = author
        self.date = date
        self.message = message
        self.file_stats = file_stats


def api_repos(username: str):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to fetch repos: {response.status_code} {response.text}"
        )


def download_bare_repos(username: str):
    user_repos_dir = os.path.join(REPOS_DIR, username)
    os.makedirs(user_repos_dir, exist_ok=True)

    repos = api_repos(username)
    for repo in repos:
        repo_name = repo["name"]
        repo_url = repo["clone_url"]
        repo_path = os.path.join(user_repos_dir, repo_name)
        if not os.path.exists(repo_path):
            print(f"Cloning {repo_url} into {repo_path}")
            git.Repo.clone_from(repo_url, repo_path, bare=True)
        else:
            print(f"Repository {repo_name} already exists, skipping.")


def git_commit_info(username: str, repo_name: str) -> List[CommitInfo]:
    repo_path = os.path.join(REPOS_DIR, username, repo_name)
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"Repository {repo_name} not found in {REPOS_DIR}")

    repo = git.Repo(repo_path)
    commits = []
    commit_info = []

    try:
        commits = list(repo.iter_commits())
    except Exception as e:
        print(f"Error processing repository {repo_name}: {e}")
        return []

    for commit in commits:
        sha_1_hash = commit.hexsha
        author = str(commit.author)
        date = commit.authored_datetime.isoformat()
        message = commit.message.strip()
        file_stats = [
            CommitFileStat(
                filename, stats.get("insertions", 0), stats.get("deletions", 0)
            )
            for filename, stats in commit.stats.files.items()
        ]
        commit_info.append(
            CommitInfo(repo_name, sha_1_hash, author, date, message, file_stats)
        )

    return commit_info


def generate_csv(username, author_filter: List[str] = []):
    commit_info_all_repos = []
    for repo_name in os.listdir(os.path.join(REPOS_DIR, username)):
        commit_info = git_commit_info(username, repo_name)
        commit_info_all_repos.extend(commit_info)

    with open(CSV_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "repo_name",
                "sha_1_hash",
                "author",
                "date",
                "message",
                "filename",
                "add_lines",
                "del_lines",
            ]
        )
        for commit_info in commit_info_all_repos:
            for file_stat in commit_info.file_stats:
                author = commit_info.author
                if author_filter and author not in author_filter:
                    continue

                writer.writerow(
                    [
                        commit_info.repo_name,
                        commit_info.sha_1_hash,
                        author,
                        commit_info.date,
                        commit_info.message,
                        file_stat.filename,
                        file_stat.add_lines,
                        file_stat.del_lines,
                    ]
                )

    print(f"Generated {CSV_FILE}!")

def main():
    args = sys.argv

    if len(args) not in [2, 3]:
        print("Usage: generate_csv.py <username> [author filter: <author1>,<author2>,...]")
        return

    username = args[1]
    author_filter =[]

    if len(args) == 3:
        author_filter = list(filter(lambda x: x != "", args[2].split(",")))

    print(f"username: {username}")
    print(f"author_filter: {author_filter}")

    download_bare_repos(username)
    generate_csv(username, author_filter)

if __name__ == "__main__":
    main()
