#!/usr/bin/env python
import argparse
import codecs
import re
import os
import subprocess
import shutil
import sys

from bs4 import BeautifulSoup, Tag
import requests

VID_TEMPLATE = """<video width="{width}" height="{height}" controls>
    <source src="{source}" type="video/mp4">
    Your browser does not support the video tag.
</video>"""
WIDTH=614
HEIGHT=345


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
    cmd = 'perl get_iplayer --force --pid={pid} --file-prefix={pid}'.format(
        pid=pid)
    p = subprocess.Popen(
        cmd.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.wait()


def main(url, output_dir):
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    title = u' - '.join(soup.title.text.split(u' - ')[2:])
    output_dir = os.path.join(output_dir, title)
    os.mkdir(output_dir)
    vid_identifiers = re.findall(
        '\"container\"\:\"(.{19})\"\,\"pid\"\:\"([a-z0-9]{8})\"', html)
    vid_identifiers = {k: v for k, v in vid_identifiers}
    post = soup.find('article', {'itemprop': 'blogPost'})
    vid_containers = post.findAll('div', {'class': 'smp'})
    for i, container in enumerate(vid_containers):
        pid = vid_identifiers['#{0}'.format(container['id'])]
        print 'Downloading video {0} of {1}...'.format(i+1, len(vid_containers)+1)
        download(pid)
        filename = '{0}.mp4'.format(pid)
        shutil.move(filename, os.path.join(output_dir, filename))

        vid_html = VID_TEMPLATE.format(
            width=WIDTH, height=HEIGHT, source='{}.mp4'.format(pid))
        vid = BeautifulSoup(vid_html).video
        container.replace_with(vid)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="blog post URL")
    parser.add_argument(
        "location", help=("output directory. A subdirectory for each blogpost"
                          " will be made in this directory."),
        type=writable_dir)
    args = parser.parse_args()
    main(args.url, args.location)
