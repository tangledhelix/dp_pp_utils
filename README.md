
This is a set of tools / templates that I use in the course of post-processing
work for [Distributed Proofreaders](http://www.pgdp.net).

Other PP'ers are welcome to use anything here, but please note that this stuff
is very tailored to my specific workflow, and I change that on a whim.

To use, first you need Python 3.

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

And create an `auth-config.json` file with your GitHub credentials and DP site
password. Use `auth-config.json.sample` as a guide for the format; it's a
straightforward JSON file.

`make_project.py` will set up a project in `~/dp/pp/{project}`, create a GitHub
project, download the text and images from the DP site, and unzip them.

`make_errata_project.py` will create a simple errata project for creating an
errata report for Project Gutenberg.
