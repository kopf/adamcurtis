#!/usr/bin/env python
import argparse
import codecs
import re
import os
import subprocess
import shutil
import sys
from distutils.spawn import find_executable

from bs4 import BeautifulSoup, Tag
import requests

VID_TEMPLATE = """<video width="{width}" height="{height}" controls>
    <source src="{source}" type="video/mp4">
    Your browser does not support the video tag.
</video>"""
WIDTH = 614
HEIGHT = 345
VERBOSE = False
CMD = 'perl get_iplayer --force --pid={pid} --file-prefix={pid}'


def check_dependencies():
    for exe in ['rtmpdump', 'perl']:
        if not find_executable(exe):
            raise RuntimeError(exe)
    if not os.path.exists('./get_iplayer'):
        raise RuntimeError('get_iplayer')
    # Make sure get_iplayer has been initialised
    if not os.path.exists(os.path.join(os.path.expanduser('~'), '.get_iplayer')):
        print 'Initialising get_iplayer...'
        subprocess.Popen(['perl', './get_iplayer'], stdout=subprocess.PIPE).wait()


def writable_dir(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except Exception:
            raise argparse.ArgumentTypeError(
                "Failed creating directory {0}".format(path))
    elif not os.path.isdir(path):
        raise argparse.ArgumentTypeError("{0} is not a directory".format(path))
    if os.access(path, os.W_OK):
        return path
    else:
        raise argparse.ArgumentTypeError("Cannot write to {0}".format(path))


def download(pid):
    p = subprocess.Popen(
        CMD.format(pid=pid).split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.wait()
    return p.stdout.read()


def main(url, output_dir):
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    title = u' - '.join(soup.title.text.split(u' - ')[2:])
    output_dir = os.path.join(output_dir, title)
    media_dir = os.path.join(output_dir, 'media')
    os.makedirs(media_dir)
    vid_identifiers = re.findall(
        '\"container\"\:\"(.{19})\"\,\"pid\"\:\"([a-z0-9]{8})\"', html)
    vid_identifiers = {k: v for k, v in vid_identifiers}
    post = soup.find('article', {'itemprop': 'blogPost'})
    vid_containers = post.findAll('div', {'class': 'smp'})
    for i, container in enumerate(vid_containers):
        pid = vid_identifiers['#{0}'.format(container['id'])]
        print 'Downloading video {0} of {1}...'.format(i+1, len(vid_containers))
        stdout = download(pid)
        filename = '{0}.mp4'.format(pid)
        if VERBOSE or not os.path.exists(filename):
            print stdout
            if not os.path.exists(filename):
                sys.exit(-1)
        shutil.move(filename, os.path.join(media_dir, filename))

        vid_html = VID_TEMPLATE.format(
            width=WIDTH, height=HEIGHT, source='media/{0}.mp4'.format(pid))
        vid = BeautifulSoup(vid_html).video
        container.replace_with(vid)

    print 'Downloading images...'
    for i, img in enumerate(post.findAll('img')):
        resp = requests.get(img['src'], stream=True)
        filename = 'image_{0}.jpg'.format(i)
        img['src'] = 'media/{0}'.format(filename)
        with open(os.path.join(media_dir, filename), 'wb') as f:
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)
    for script in post.findAll('script'):
        script.extract()
    post.find('div', {'class': 'cf'}).extract() # remove social media crap
    for filename in os.listdir('assets'):
        shutil.copy(os.path.join('assets', filename), output_dir)
    with codecs.open(os.path.join(output_dir, 'blogpost.html'), 'w', 'utf8') as f:
        f.write('<html><head><title>')
        f.write(unicode(title).encode('ascii', 'ignore'))
        f.write('</title><link rel="stylesheet" type="text/css" href="default.css">')
        f.write('</head><body>')
        f.write(unicode(post).encode('ascii', 'xmlcharrefreplace'))
        f.write('</body></html>')


if __name__ == '__main__':
    try:
        check_dependencies()
    except RuntimeError as e:
        print ('Dependency "{0}" not found! Please install first.'
               ' See the README for more help.').format(e)
        sys.exit(-1)
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="blog post URL")
    parser.add_argument(
        "location", help=("output directory. A subdirectory for each blogpost"
                          " will be made in this directory."),
        type=writable_dir)
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    VERBOSE = args.verbose
    main(args.url, args.location)
