#!/usr/bin/env python3

import json
import requests
import os
from os.path import basename
from jinja2 import Template
from subprocess import call
from trello import TrelloClient
from zipfile import ZipFile

AUTH_CONFIG = 'auth-config.json'
TRELLO_TEMPLATE = 'TEMPLATE: PP workflow'

PREVIEW_HOST = 'dp.tangledhelix.com'
PREVIEW_PATH = 'sites/' + PREVIEW_HOST + '/projects/'


class MakeProject():

    def __init__(self):
        self.dp_base = os.environ['HOME'] + '/dp'
        self.projects_base = self.dp_base + '/pp'
        self.template_dir = self.dp_base + '/util/templates'
        self.params = {}

        self.trello_template = TRELLO_TEMPLATE
        self.preview_host = PREVIEW_HOST
        self.preview_path = PREVIEW_PATH

        with open(self.dp_base + '/util/' + AUTH_CONFIG) as file:
            self.auth = json.loads(file.read())

    def get_param(self, param_name, prompt_text):
        self.params[param_name] = input(prompt_text + ': ')

    def get_params(self):
        self.get_param('project_name', 'Project name, e.g. "missfairfax"')
        self.get_param('project_id', 'Project ID, e.g. "5351bd1e5eca9"')
        self.get_param('title', 'Title, e.g. "Miss Fairfax of Virginia"')
        self.get_param('author', 'Author, e.g. "St. George Rathborne"')
        self.get_param('pub_year', 'Year published')
        self.get_param('source_images', 'URL to source images (empty if none)')
        self.get_param('forum_link', 'URL to forum thread')
        self.project_dir = '{}/{}'.format(
            self.projects_base, self.params['project_name'])
        self.params['kindlegen_dir'] = self.dp_base + '/kindlegen'

    def create_directories(self):
        os.mkdir(self.project_dir, mode=0o755)
        os.chdir(self.project_dir)
        os.mkdir('images', mode=0o755)
        os.mkdir('illustrations', mode=0o755)
        os.mkdir('pngs', mode=0o755)

    def create_git_repository(self):
        call(['git', 'init'])
        call(['git', 'remote', 'add', 'origin', self.github_remote_url])

    def process_template(self, src_filename, dst_filename=None):
        if not dst_filename:
            dst_filename = src_filename
        with open(self.template_dir + '/' + src_filename) as file:
            template = Template(file.read())
        with open(self.project_dir + '/' + dst_filename, 'w') as file:
            file.write(template.render(self.params))

    def utf8_conversion(self):
        project_id = self.params['project_id']
        project_name = self.params['project_name']
        project_dir = self.project_dir

        input_file = '{}/projectID{}.txt'.format(project_dir, project_id)
        output_file = '{}/{}-utf8.txt'.format(project_dir, project_name)

        with open(input_file, encoding='latin-1') as file:
            contents = file.read()

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('[** UTF8 preservation hack: Phœnix]\n')
            file.write(contents)

    def make_github_repo(self):
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }

        payload = {
            'name': 'DP_{}'.format(self.params['project_name']),
            'description': 'DP PP project "{}" ID {}'.format(
                self.params['title'], self.params['project_id'],
            ),
            'private': False,
            'has_issues': False,
            'has_wiki': False,
            'has_downloads': False,
            'auto_init': False,
        }

        auth_data = (
            self.auth['github']['username'],
            self.auth['github']['password'],
        )

        r = requests.post('https://api.github.com/user/repos',
                          auth=auth_data, headers=headers,
                          data=json.dumps(payload))
        if r.status_code == 201:
            print('Created GitHub repository')
            json_response = json.loads(r.text)
            self.github_remote_url = json_response['ssh_url']
        else:
            print('ERROR: GitHub response code {} unexpected.'.format(
                r.status_code
            ))

    def make_trello_board(self):
        client = TrelloClient(
            api_key=self.auth['trello']['api_key'],
            api_secret=self.auth['trello']['api_secret'],
            token=self.auth['trello']['token'],
            token_secret=self.auth['trello']['token_secret'],
        )

        boards = client.list_boards()
        template = None

        for board in boards:
            if board.name == self.trello_template:
                template = board

        new_board = client.add_board(
            'New test board',
            source_board=template,
            permission_level='public'
        )
        self.params['trello_url'] = new_board.url
        print('Created Trello board - ' + new_board.url)

    def make_preview_dir(self):
        call(['ssh', self.preview_host,
              'mkdir ' + self.preview_path + self.params['project_name']])

    def download_text(self):
        print('Downloading text from DP ...', end='', flush=True)
        zipfile = 'projectID{}.zip'.format(self.params['project_id'])
        url = 'http://www.pgdp.net/projects/projectID{0}/projectID{0}.zip'
        r = requests.get(url.format(self.params['project_id']))
        with open(zipfile, 'wb') as file:
            file.write(r.content)
        self.unzip_file(zipfile, self.project_dir)
        print(' done.')

    def unzip_file(self, filename, path):
        with ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(path)
        os.remove(filename)


if __name__ == '__main__':
    project = MakeProject()
    project.get_params()
    project.create_directories()
    project.download_text()

    project.utf8_conversion()
    project.make_github_repo()
    project.make_trello_board()
    project.create_git_repository()

    project.process_template('Makefile')
    project.process_template('README.md')
    project.process_template('index.html')
    project.process_template('smooth-reading.txt')
    project.process_template('pp-gitignore', '.gitignore')
    project.make_preview_dir()
