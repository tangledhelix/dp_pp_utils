
This is a set of tools / templates that I use in the course of post-processing
work for [Distributed Proofreaders](http://www.pgdp.net).

Other PP'ers are welcome to use anything here, but please note that this stuff
is very tailored to my specific workflow, and I change that on a whim.

To use, first you need Python 3.

```
pyvenv venv
source venv/bin/activate
pip install -r requirements.txt
```

And create a `auth-config.json` file with your Github username and password and
your Trello API data. Use `auth-config.json.sample` as a guide for the format;
it's a straightforward JSON file.
