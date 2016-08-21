#!/usr/bin/env python3

import json
import requests
from os import environ, mkdir, chdir, getcwd
from os.path import basename
from jinja2 import Template
from subprocess import call
from trello import TrelloClient

AUTH_CONFIG = 'auth-config.json'
TRELLO_TEMPLATE = 'TEMPLATE: PP workflow'


class MakeProject():

    def __init__(self):
        self.dp_base = environ['HOME'] + '/dp'
        self.projects_base = self.dp_base + '/pp'
        self.template_dir = self.dp_base + '/util/templates'
        self.params = {'project_name': basename(getcwd())}
        self.trello_template = TRELLO_TEMPLATE

        with open(self.dp_base + '/util/' + AUTH_CONFIG) as file:
            self.auth = json.loads(file.read())

    def get_param(self, param_name, prompt_text):
        self.params[param_name] = input(prompt_text + ': ')

    def get_params(self):
        self.get_param('project_id', 'Project ID, e.g. "5351bd1e5eca9"')
        self.get_param('title', 'Title, e.g. "Miss Fairfax of Virginia"')
        self.get_param('author', 'Author, e.g. "St. George Rathborne"')
        self.get_param('pub_year', 'Year published')
        self.get_param('source_images', 'URL to source images (empty if none)')
        self.get_param('forum_link', 'URL to forum thread')
        self.project_dir = '{}/{}'.format(
            self.projects_base, self.params['project_name']).lower()
        self.params['kindlegen_dir'] = self.dp_base + '/kindlegen'

    def create_directories(self):
        chdir(self.project_dir)
        mkdir('images', mode=0o755)
        mkdir('illustrations', mode=0o755)
        mkdir('pngs', mode=0o755)

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
        project_name = self.params['project_name'].lower()
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
            'name': 'DP_{}'.format(self.params['project_name'].lower()),
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

if __name__ == '__main__':
    project = MakeProject()
    project.get_params()
    project.create_directories()

    project.utf8_conversion()
    project.make_github_repo()
    project.make_trello_board()
    project.create_git_repository()

    project.process_template('Makefile')
    project.process_template('README.md')
    project.process_template('index.html')
    project.process_template('smooth-reading.txt')
    project.process_template('pp-gitignore', '.gitignore')
