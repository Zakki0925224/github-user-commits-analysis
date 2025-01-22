# github-user-commits-analysis

## Overview

This script analyzes the commit history of a GitHub user's repositories and generates a CSV file containing detailed information about each commit. It clones the user's repositories, extracts commit data, and saves it in a structured format.

## Usage

1. Ensure you have Python and Git installed on your system.
2. Install the required Python packages:
   ```bash
   pip install requests gitpython
   ```
3. Run the script with the desired GitHub username:
   ```bash
   python generate_csv.py <username> [author filter: <author1>,<author2>,...]
   ```

## CSV Explanation

The generated CSV file (`commits.csv`) contains the following columns:

- `repo_name`: The name of the repository.
- `sha_1_hash`: The SHA-1 hash of the commit.
- `author`: The author of the commit.
- `date`: The date and time when the commit was authored.
- `message`: The commit message.
- `filename`: The name of the file that was changed.
- `add_lines`: The number of lines added in the file.
- `del_lines`: The number of lines deleted in the file.
