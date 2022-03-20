#!/usr/bin/env python3

import json
import requests
import os
import sys
import re
import shutil

from os.path import basename
from jinja2 import Template
from subprocess import call
from trello import TrelloClient
from zipfile import ZipFile

AUTH_CONFIG = "auth-config.json"

PGDP_URL = "https://www.pgdp.net"

GITHUB_REMOTE = "origin"
GITHUB_BRANCH = "main"

# Set true to assume we'll use ppgen; false otherwise (i.e. guiguts)
PPGEN = True

if PPGEN:
    TRELLO_TEMPLATE = "TEMPLATE: PPgen workflow"
else:
    TRELLO_TEMPLATE = "TEMPLATE: PP workflow"

class MakeProject():

    def __init__(self):
        self.dp_base = f"{os.environ['HOME']}/dp"
        self.projects_base = f"{self.dp_base}/pp"
        self.template_dir = f"{self.dp_base}/util/templates"
        self.params = {}

        self.trello_template = TRELLO_TEMPLATE

        with open(f"{self.dp_base}/util/{AUTH_CONFIG}") as file:
            self.auth = json.loads(file.read())

    def get_param(self, param_name, prompt_text):
        param_answer = input(f"{prompt_text}: ")

        if param_name == "project_id":
            param_answer = param_answer.replace("projectID", "")

        self.params[param_name] = param_answer

    def get_params(self):
        self.get_param("project_name", 'Project name, e.g. "missfairfax"')
        self.get_param("project_id", 'Project ID, e.g. "projectID5351bd1e5eca9"')
        self.project_dir = f"{self.projects_base}/{self.params['project_name']}"
        #self.params["kindlegen_dir"] = self.dp_base + "/kindlegen"

    def pgdp_login(self):
        payload = {
            "destination": "/c/",
            "userNM": self.auth["pgdp"]["username"],
            "userPW": self.auth["pgdp"]["password"],
        }

        r = requests.post(f"{PGDP_URL}/c/accounts/login.php", data=payload)
        if r.status_code != 200:
            print("Error: unable to log into DP site")
            sys.exit(1)

        print(f"Logged into PGDP site as {self.auth['pgdp']['username']}.")
        self.dp_cookie = r.headers["Set-Cookie"].split(";")[0]

    def scrape_project_info(self):
        r = requests.post(
            f"{PGDP_URL}/c/project.php?id=projectID{self.params['project_id']}",
            headers={"Cookie": self.dp_cookie}
        )
        if r.status_code != 200:
            print("Error: unable to retrieve DP project info")
            sys.exit(1)

        html_doc = re.sub(r"\n", "", r.text)

        self.params["title"] = re.sub(
            #
            # This version broke on cavalry. Changing " to <, see if it works
            # r'.*<td[^>]+><b>Title</b></td><td[^>]+>([^"]+)</td>.*',
            #
            # This version broke on irishjournal, the site updated
            # to use th instead of tr... updating to match site.
            #r'.*<td[^>]+><b>Title</b></td><td[^>]+>([^<]+)</td>.*',
            #
            r'.*<th\s+class=["\']label["\']>Title</th>\s*<td[^>]+>([^<]+)</td>.*',
            r"\1",
            html_doc
        )
        print(f"Title: {self.params['title']}")

        self.params["author"] = re.sub(
            # This version broke on irishjournal, the site updated
            # to use th instead of tr... updating to match site.
            #r'.*<td[^>]+><b>Author</b></td><td[^>]+>([^<]+)</td>.*',
            #
            r'.*<th\s+class=["\']label["\']>Author</th>\s*<td[^>]+>([^<]+)</td>.*',
            r"\1",
            html_doc
        )
        print(f"Author: {self.params['author']}")

        #<tr><th class='label'>Forum</th><td colspan='4'><a href='https://www.pgdp.net/phpBB3/viewtopic.php?t=63502'>Discuss this project</a> (19 replies)</td></tr>

        self.params["forum_link"] = re.sub(
            # This version broke on irishjournal, the site updated
            # to use th instead of tr... updating to match site.
            #r".*<td[^>]+><b>Forum</b></td><td[^>]+><a href='([^']+)'>.*",
            #<a href='([^']+)'>
            #
            r".*<th\s+class=.label.>Forum</th>\s*<td[^>]+>\s*<a href='([^']+)'.*",
            r"\1",
            html_doc
        )
        print(f"Forum: {self.params['forum_link']}")

    def create_directories(self):
        os.mkdir(self.project_dir, mode=0o755)
        os.chdir(self.project_dir)
        os.mkdir("images", mode=0o755)
        os.mkdir("illustrations", mode=0o755)
        os.mkdir("pngs", mode=0o755)
        print("Created directory structure")

    def create_git_repository(self):
        call(["git", "init", "-q"])
        call(["git", "add", "."])
        call(["git", "commit", "-q", "-m", "Initial import from DP"])
        print(f"Git repository created")
        call(["git", "remote", "add", GITHUB_REMOTE, self.git_remote_url])
        call(["git", "push", "-q", "-u", GITHUB_REMOTE, GITHUB_BRANCH])
        print(f"Git repository pushed")

    def process_template(self, src_filename, dst_filename=None):
        if not dst_filename:
            dst_filename = src_filename
        with open(f"{self.template_dir}/{src_filename}") as file:
            template = Template(file.read())
        with open(f"{self.project_dir}/{dst_filename}", "w") as file:
            file.write(template.render(self.params))
        print(f"Created: {dst_filename}")

    def copy_text_file(self):
        project_id = self.params["project_id"]
        project_name = self.params["project_name"]
        project_dir = self.project_dir

        input_file = f"{project_dir}/projectID{project_id}.txt"
        if PPGEN:
            output_file = f"{project_dir}/{project_name}-src.txt"
        else:
            output_file = f"{project_dir}/{project_name}-utf8.txt"

        shutil.copyfile(input_file, output_file)

    def make_github_repo(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        payload = {
            "name": f"DP_{self.params['project_name']}",
            "description": f"DP PP project \"{self.params['title']}\" ID {self.params['project_id']}",
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
            self.git_remote_url = json_response["clone_url"].replace(
                "github.com",
                self.auth["github"]["username"] + "@github.com"
            )
        else:
            print(f"ERROR: GitHub response code {r.status_code} unexpected.")

    def make_gitlab_repo(self):
        headers = {
            "Content-Type": "application/json",
            "PRIVATE-TOKEN": self.auth["gitlab"],
        }

        payload = {
            "name": f"DP_{self.params['project_name']}",
            "description": f"DP PP project \"{self.params['title']}\" ID {self.params['project_id']}",
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
            print(f"ERROR: Gitlab response code {r.status_code} unexpected.")
            print(r.text)

    def make_online_repo(self):
        if self.auth["git_site"] == "github":
            self.make_github_repo()
        elif self.auth["git_site"] == "gitlab":
            self.make_gitlab_repo()

    def make_trello_board(self):
        client = TrelloClient(
            api_key=self.auth["trello"]["api_key"],
            api_secret=self.auth["trello"]["api_secret"],
            token=self.auth["trello"]["token"],
            token_secret=self.auth["trello"]["token_secret"],
        )

        template = None
        for board in client.list_boards():
            if board.name == self.trello_template:
                template = board
                break

        new_board = client.add_board(
            f"DP: {self.params['title']}",
            source_board=template,
            permission_level="public"
        )

        for _list in new_board.list_lists():
            if _list.name.startswith("Notes"):
                for _card in _list.list_cards():
                    if _card.name == "Project info":
                        info_card = _card
                        break
                break
        new_description = info_card.desc.replace(
            "{{PROJECT_NAME}}", self.params["project_name"]
        ).replace(
            "{{PROJECT_ID}}", self.params["project_id"]
        )
        
        info_card.set_description(new_description)

        self.params["trello_url"] = new_board.url
        print(f"Created Trello board - {new_board.url}")

    def download_text(self):
        print("Downloading text from DP ...", end="", flush=True)
        zipfile = f"projectID{self.params['project_id']}.zip"
        url = f"{PGDP_URL}/projects/projectID{self.params['project_id']}/projectID{self.params['project_id']}.zip"
        r = requests.get(url, headers={"Cookie": self.dp_cookie})
        with open(zipfile, "wb") as file:
            file.write(r.content)
        self.unzip_file(zipfile, self.project_dir)
        print(" done.")

    def download_images(self):
        print("Downloading images from DP ...", end="", flush=True)
        zipfile = f"projectID{self.params['project_id']}images.zip"
        url = f"{PGDP_URL}/c/tools/download_images.php?projectid=projectID{self.params['project_id']}"
        r = requests.get(url, headers={"Cookie": self.dp_cookie})
        with open(zipfile, "wb") as file:
            file.write(r.content)
        self.unzip_file(zipfile, f"{self.project_dir}/pngs")
        print(" done.")

    def unzip_file(self, filename, path):
        with ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(path)
        os.remove(filename)


if __name__ == "__main__":

    # By default, create remote resources like Trello & GitHub.
    CREATE_REMOTE = True

    # Process arguments, if any
    if len(sys.argv) >= 2:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print(f"Usage: {sys.argv[0]} [<option(s)>]")
            print("    -h, --help: print this help")
            print("    -l, --local: only create local resources (for debug)")
            sys.exit(1)
        elif sys.argv[1] == "-l" or sys.argv[1] == "--local":
            CREATE_REMOTE = False

    project = MakeProject()
    project.get_params()
    project.pgdp_login()
    project.scrape_project_info()
    project.create_directories()
    project.download_text()
    project.download_images()

    # Make a copy of the text to work on
    project.copy_text_file()

    if CREATE_REMOTE:
        project.make_online_repo()
        project.make_trello_board()

    project.process_template("Makefile")
    project.process_template("README.md")
    project.process_template("pp-gitignore", ".gitignore")

    if CREATE_REMOTE:
        # This is only done if remote, because it will try to push.
        project.create_git_repository()
