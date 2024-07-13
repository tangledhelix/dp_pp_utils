#!/usr/bin/env python3

import json
import requests
import os
import sys

from jinja2 import Template
from subprocess import call

AUTH_CONFIG = "auth-config.json"

PGDP_URL = "https://www.pgdp.net"

GITHUB_REMOTE = "origin"
GITHUB_BRANCH = "main"

class MakeProject():

    def __init__(self):
        self.dp_base = f"{os.environ['HOME']}/dp"
        self.projects_base = f"{self.dp_base}/errata"
        self.template_dir = f"{self.dp_base}/util/templates"
        self.params = {}

        with open(f"{self.dp_base}/util/{AUTH_CONFIG}") as file:
            self.auth = json.loads(file.read())

    def get_param(self, param_name, prompt_text):
        param_answer = input(f"{prompt_text}: ")

        if param_name == "project_id":
            param_answer = param_answer.replace("projectID", "")

        self.params[param_name] = param_answer

    def get_params(self):
        self.get_param("project_name", 'Project name, e.g. "missfairfax"')
        self.project_dir = f"{self.projects_base}/{self.params['project_name']}"

        self.get_param("project_id", 'Project ID, e.g. "projectID5351bd1e5eca9" (OR LEAVE BLANK)')

        # If there's no DP project, get PG ebook number, etc. directly from input
        if not self.params["project_id"]:
            self.get_param("pg_ebook_number", 'PG eBook number, e.g. "10001"')
            self.get_param("title", "Title")
            self.get_param("author", "Author")

    def get_project_info(self):
        r = requests.get(
            f"{PGDP_URL}/api/v1/projects/projectID{self.params['project_id']}",
            headers={"X-Api-Key": self.auth["pgdp"]["api_key"]}
        )
        if r.status_code != 200:
            print("Error: unable to use PGDP REST API")
            sys.exit(1)

        j = r.json()

        self.params["title"] = j["title"]
        print(f"Title: {self.params['title']}")

        self.params["author"] = j["author"]
        print(f"Author: {self.params['author']}")

        self.params["pg_ebook_number"] = j["pg_ebook_number"]
        print(f"PG eBook number: {self.params['pg_ebook_number']}")

    def create_directories(self):
        os.mkdir(self.project_dir, mode=0o755)
        os.chdir(self.project_dir)
        print("Created directory structure")

    def create_git_repository(self):
        call(["git", "init", "-q"])
        call(["git", "add", "."])
        call(["git", "commit", "-q", "-m", "Initial project creation"])
        print(f"Git repository created")
        call(["git", "remote", "add", GITHUB_REMOTE, self.git_remote_url])
        call(["git", "push", "-u", GITHUB_REMOTE, GITHUB_BRANCH])
        print(f"Git repository pushed")

    def process_template(self, src_filename, dst_filename=None):
        if not dst_filename:
            dst_filename = src_filename
        with open(f"{self.template_dir}/{src_filename}") as file:
            template = Template(file.read(), autoescape=False)
        with open(f"{self.project_dir}/{dst_filename}", "w") as file:
            file.write(template.render(self.params))
        print(f"Created: {dst_filename}")

    def make_github_repo(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        payload = {
            "name": f"PG_errata_{self.params['project_name']}",
            "description": f"Project Gutenberg errata report for \"{self.params['title']}\" by {self.params['author']}",
            "private": False,
            "has_issues": False,
            "has_wiki": False,
            "has_downloads": False,
            "auto_init": False,
        }

        auth_data = (
            self.auth["github"]["username"],
            self.auth["github"]["password"],
        )

        r = requests.post("https://api.github.com/user/repos",
                          auth=auth_data, headers=headers,
                          data=json.dumps(payload))
        if r.status_code == 201:
            print("Created GitHub repository")
            json_response = json.loads(r.text)
            self.git_remote_url = json_response["ssh_url"]
        else:
            print(f"ERROR: GitHub response code {r.status_code} unexpected.")


if __name__ == "__main__":

    project = MakeProject()

    project.get_params()
    print(project.params["project_id"])
    if project.params["project_id"]:
        project.get_project_info()

    project.create_directories()
    project.make_github_repo()
    project.process_template("README-errata.md", "README.md")
    project.create_git_repository()

