#!/usr/bin/env python3

from os import environ, mkdir, chdir, getcwd
from os.path import basename
from jinja2 import Template
from subprocess import call


class MakeProject():

    def __init__(self):
        self.dp_base = environ['HOME'] + '/dp'
        self.projects_base = self.dp_base + '/pp'
        self.template_dir = self.dp_base + '/util/templates'
        self.params = {'project_name': basename(getcwd())}

    def get_param(self, param_name, prompt_text):
        self.params[param_name] = input(prompt_text + ': ')

    def get_params(self):
        self.get_param('project_id', 'Project ID, e.g. "5351bd1e5eca9"')
        self.get_param('title', 'Title, e.g. "Miss Fairfax of Virginia"')
        self.get_param('author', 'Author, e.g. "St. George Rathborne"')
        self.get_param('pub_year', 'Year published')
        self.get_param('source_images', 'URL to source images (empty if none)')
        self.get_param('forum_link', 'URL to forum thread')
        self.get_param('trello_url', 'URL to Trello board')
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


if __name__ == '__main__':
    project = MakeProject()
    project.get_params()
    project.create_directories()
    project.create_git_repository()

    project.process_template('Makefile')
    project.process_template('README.md')
    project.process_template('index.html')
    project.process_template('smooth-reading.txt')
    project.process_template('pp-gitignore', '.gitignore')

    project.utf8_conversion()
