#!/usr/bin/env python
import re
import sys

from bs4 import BeautifulSoup
import requests

VID_TEMPLATE = """<video width="{width}" height="{height}" controls>
    <source src="{source}" type="video/mp4">
    Your browser does not support the video tag.
</video>"""
WIDTH=614
HEIGHT=345

def main(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    vid_containers = re.findall(
        '\"container\"\:\"(.{19})\"\,\"pid\"\:\"([a-z0-9]{8})\"', html)
    vid_containers = {k: v for k, v in vid_containers}
    post = soup.find('article', {'itemprop': 'blogPost'})
    for container in post.findAll('div', {'class': 'smp'}):
        vid_html = VID_TEMPLATE.format(width=WIDTH, height=HEIGHT,
                                       source=vid_containers['#%s' % container['id']])
        vid = BeautifulSoup(vid_html).body.video
        container.replace_with(vid)
    for script in post.findAll('script'):
        script.extract()
    post.find('div', {'class': 'cf'}).extract() # remove social media crap
    with open('output.html', 'w') as f:
        f.write(post.prettify('utf-8'))

if __name__ == '__main__':
    main(sys.argv[-1])
