#!/usr/bin/env python3

import json
import requests
import os
import sys
import re
from os.path import basename
from jinja2 import Template
from subprocess import call
from trello import TrelloClient
from zipfile import ZipFile

AUTH_CONFIG = "auth-config.json"
TRELLO_TEMPLATE = "TEMPLATE: PP workflow"

PGDP_URL = "https://www.pgdp.net"


class MakeProject():

    def __init__(self):
        self.dp_base = os.environ["HOME"] + "/dp"
        self.projects_base = self.dp_base + "/pp"
        self.template_dir = self.dp_base + "/util/templates"
        self.params = {}

        self.trello_template = TRELLO_TEMPLATE

        with open(self.dp_base + "/util/" + AUTH_CONFIG) as file:
            self.auth = json.loads(file.read())

    def get_param(self, param_name, prompt_text):
        self.params[param_name] = input(prompt_text + ": ")

    def get_params(self):
        self.get_param("project_name", 'Project name, e.g. "missfairfax"')
        self.get_param("project_id", 'Project ID, e.g. "5351bd1e5eca9"')
        self.project_dir = "{}/{}".format(
            self.projects_base, self.params["project_name"])
        self.params["kindlegen_dir"] = self.dp_base + "/kindlegen"

    def pgdp_login(self):
        payload = {
            "destination": "/c/",
            "userNM": self.auth["pgdp"]["username"],
            "userPW": self.auth["pgdp"]["password"],
        }

        r = requests.post(PGDP_URL + "/c/accounts/login.php", data=payload)
        if r.status_code != 200:
            print("Error: unable to log into DP site")
            sys.exit(1)

        self.dp_cookie = r.headers["Set-Cookie"].split(";")[0]

    def scrape_project_info(self):
        r = requests.post(
            "{0}/c/project.php?id=projectID{1}".format(
                PGDP_URL,
                self.params["project_id"]
            ),
            headers={"Cookie": self.dp_cookie}
        )
        if r.status_code != 200:
            print("Error: unable to retrieve DP project info")
            sys.exit(1)

        html_doc = re.sub(r"\n", "", r.text)

        self.params["title"] = re.sub(
            r'.*<td[^>]+><b>Title</b></td><td[^>]+>([^<]+)</td>.*',
            r"\1",
            html_doc
        )

        self.params["author"] = re.sub(
            r'.*<td[^>]+><b>Author</b></td><td[^>]+>([^<]+)</td>.*',
            r"\1",
            html_doc
        )

        self.params["forum_link"] = re.sub(
            r".*<td[^>]+><b>Forum</b></td><td[^>]+><a href='([^']+)'>.*",
            r"\1",
            html_doc
        )

    def create_directories(self):
        os.mkdir(self.project_dir, mode=0o755)
        os.chdir(self.project_dir)
        os.mkdir("images", mode=0o755)
        os.mkdir("illustrations", mode=0o755)
        os.mkdir("pngs", mode=0o755)

    def create_git_repository(self):
        call(["git", "init"])
        call(["git", "add", "."])
        call(["git", "commit", "-m", "Initial import from DP"])
        call(["git", "remote", "add", "origin", self.git_remote_url])
        call(["git", "push", "-u", "origin", "master"])

    def process_template(self, src_filename, dst_filename=None):
        if not dst_filename:
            dst_filename = src_filename
        with open(self.template_dir + "/" + src_filename) as file:
            template = Template(file.read())
        with open(self.project_dir + "/" + dst_filename, "w") as file:
            file.write(template.render(self.params))

    def utf8_conversion(self):
        project_id = self.params["project_id"]
        project_name = self.params["project_name"]
        project_dir = self.project_dir

        input_file = "{}/projectID{}.txt".format(project_dir, project_id)
        output_file = "{}/{}-utf8.txt".format(project_dir, project_name)

        with open(input_file, encoding="latin-1") as file:
            contents = file.read()

        with open(output_file, "w", encoding="utf-8") as file:
            file.write("[** UTF8 preservation hack: Phœnix]\n")
            file.write(contents)

    def make_github_repo(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        payload = {
            "name": "DP_{}".format(self.params["project_name"]),
            "description": 'DP PP project "{}" ID {}'.format(
                self.params["title"], self.params["project_id"],
            ),
            "private": True,
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
            print("ERROR: GitHub response code {} unexpected.".format(
                r.status_code
            ))

    def make_gitlab_repo(self):
        headers = {
            "Content-Type": "application/json",
            "PRIVATE-TOKEN": self.auth["gitlab"],
        }

        payload = {
            "name": "DP_{}".format(self.params["project_name"]),
            "description": 'DP PP project "{}" ID {}'.format(
                self.params["title"], self.params["project_id"],
            ),
            "visibility": "private",
            "issues_enabled": False,
            "merge_requests_enabled": False,
            "jobs_enabled": False,
            "wiki_enabled": False,
            "snippets_enabled": False,
            "container_registry_enabled": False,
            "shared_runners_enabled": False,
            "lfs_enabled": False,
            "request_access_enabled": False,
        }

        r = requests.post("https://gitlab.com/api/v4/projects",
                          headers=headers,
                          data=json.dumps(payload))
        if r.status_code == 201:
            print("Created Gitlab repository")
            json_response = json.loads(r.text)
            self.git_remote_url = json_response["ssh_url_to_repo"]
        else:
            print("ERROR: Gitlab response code {} unexpected.".format(
                r.status_code
            ))

    def make_online_repo(self):
        if self.auth["git_site"] == "github":
            project.make_github_repo()
        elif self.auth["git_site"] == "gitlab":
            project.make_gitlab_repo()

    def make_trello_board(self):
        client = TrelloClient(
            api_key=self.auth["trello"]["api_key"],
            api_secret=self.auth["trello"]["api_secret"],
            token=self.auth["trello"]["token"],
            token_secret=self.auth["trello"]["token_secret"],
        )

        boards = client.list_boards()
        template = None

        for board in boards:
            if board.name == self.trello_template:
                template = board

        new_board = client.add_board(
            "DP: " + self.params["title"],
            source_board=template,
            permission_level="private"
        )
        self.params["trello_url"] = new_board.url
        print("Created Trello board - " + new_board.url)

    def download_text(self):
        print("Downloading text from DP ...", end="", flush=True)
        zipfile = "projectID{}.zip".format(self.params["project_id"])
        url = "{0}/projects/projectID{1}/projectID{1}.zip"
        r = requests.get(url.format(PGDP_URL, self.params["project_id"]),
                         headers={"Cookie": self.dp_cookie})
        with open(zipfile, "wb") as file:
            file.write(r.content)
        self.unzip_file(zipfile, self.project_dir)
        print(" done.")

    def download_images(self):
        print("Downloading images from DP ...", end="", flush=True)
        zipfile = "projectID{}images.zip".format(self.params["project_id"])
        url = "{0}/c/tools/download_images.php?projectid=projectID{1}"
        r = requests.get(url.format(PGDP_URL, self.params["project_id"]),
                         headers={"Cookie": self.dp_cookie})
        with open(zipfile, "wb") as file:
            file.write(r.content)
        self.unzip_file(zipfile, self.project_dir + "/pngs")
        print(" done.")

    def unzip_file(self, filename, path):
        with ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(path)
        os.remove(filename)


if __name__ == "__main__":
    project = MakeProject()
    project.get_params()
    project.pgdp_login()
    project.scrape_project_info()
    project.create_directories()
    project.download_text()
    project.download_images()

    project.utf8_conversion()

    project.make_online_repo()
    project.make_trello_board()

    project.process_template("Makefile")
    project.process_template("README.md")
    project.process_template("pp-gitignore", ".gitignore")

    project.create_git_repository()
