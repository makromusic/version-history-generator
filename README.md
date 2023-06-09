# README

This is the README file for the makromusic Mobile Frontend GitHub Projects Version History Generator.

## Introduction

The Makromusic Mobile Frontend GitHub Projects Version History Generator is a Python script that generates a version history for all GitHub projects associated with a particular user or organization. The script is designed to be easy to use and can be customized to meet your specific needs.

## Installation

Before using the script, you need to install Python and the necessary dependencies. To do this, follow these steps:

1. Install Python: You can download Python from the official website https://www.python.org/downloads/.

2. Clone the repository: Clone the repository to your local machine by running the following command in your terminal or command prompt:

```bash
git clone https://github.com/makromusic/version-history-generator.git
```

3. Install dependencies: Install the required dependencies by running the following command in the root directory of the cloned repository:

```bash
pip install -r requirements.txt
```

4. Create .env file: Create an .env file in the root directory of the cloned repository with the following content:

```
# Github Credentials
GITHUB_USERNAME=<your_github_username>
GITHUB_PASSWORD=<your_github_password>
# Project View URL
GITHUB_VIEW_URL=<project_view_url>
# Markdown Settings
MARKDOWN_FILENAME=<markdown_filename>
MARKDOWN_TITLE=<markdown_title>
# Put the section names you want to appear with a comma
# between them. The order is not important.
# Possible values are: "state,status,labels,title,link"
MARKDOWN_FORMAT="state,labels,title,link"
```

Replace <your_github_username> with your GitHub username and <your_github_password> with a password. The URL of the project view that you want to retrieve issues from is referred to as <your_project_view>.

Usage
To generate a version history, run the following command in the root directory of the cloned repository:

```bash
python version-history-generator.py
```

Conclusion
That's it! Now you can easily generate a version history for all GitHub projects associated with a particular user or organization. If you encounter any issues or have any questions, please feel free to open an issue on the GitHub repository.
