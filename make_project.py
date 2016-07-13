#!/usr/bin/env python3

from os import environ, mkdir, chdir
from jinja2 import Template
from subprocess import call

dp_base = environ['HOME'] + '/dp'
projects_base = dp_base + '/pp'
template_dir = dp_base + '/util/templates'

project_name = input('Project name, e.g. "missfairfax": ')
project_id = input('Project ID, e.g. "5351bd1e5eca9": ')
title = input('Title, e.g. "Miss Fairfax of Virginia": ')
author = input('Author, e.g. "St. George Rathborne": ')
pub_year = input('Year published: ')
source_images = input('URL to source images (empty if none): ')
forum_link = input('URL to forum thread: ')

template_args = {
    'project_name': project_name,
    'project_id': project_id,
    'title': title,
    'author': author,
    'pub_year': pub_year,
    'source_images': source_images,
    'forum_link': forum_link,
}

project_dir = '{}/{}'.format(projects_base, project_name).lower()
mkdir(project_dir, mode=0o755)
chdir(project_dir)

mkdir('images', mode=0o755)
mkdir('pngs', mode=0o755)

call(['git', 'init'])

with open(template_dir + '/Makefile') as file:
    template = Template(file.read())

with open(project_dir + '/Makefile', 'w') as file:
    file.write(template.render(template_args))

with open(template_dir + '/README.md') as file:
    template = Template(file.read())

with open(project_dir + '/README.md', 'w') as file:
    file.write(template.render(template_args))

with open(template_dir + '/index.html') as file:
    template = Template(file.read())

with open(project_dir + '/index.html', 'w') as file:
    file.write(template.render(template_args))
