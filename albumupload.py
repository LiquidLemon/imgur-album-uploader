#!/usr/bin/env python3
import os
import sys
import requests
import base64
from ptpython.repl import embed
import json
from pathlib import Path
from time import sleep

from secrets import *

API_ROOT = 'https://imgur-apiv3.p.mashape.com/3/'

class Client:
    def __init__(self):
        s = requests.Session()
        s.headers.update({
            'X-Mashape-Key': MASHAPE_KEY,
            'Authorization': f'Client-ID {CLIENT_ID}',
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'User-agent':  f'Album uploader 0.1',
        })
        self.session = s

    def post_album(self, **kwargs):
        return self._post('album', kwargs)

    def upload_image(self, path, album):
        data = base64.encodebytes(path.read_bytes())
        return self._post('image', {
            'image': data, 'album': album, 'type': 'base64'
        })

    def upload_album(self, directory):
        files = os.listdir(directory)
        files.sort()
        album = self.post_album()
        if not album['success']:
            print('failed creating album')
            sys.exit(1)
        album_id = album['data']['id']

        for name in files:
            path = Path(directory).joinpath(name)
            r = self.upload_image(path, album=album_id)
            if not r['success']:
                print(f'failed uploading {path}')
                sys.exit(1)
            print(f'uploaded {path}')

    def _get(self, url):
        result = self.session.get(API_ROOT + url)
        return json.loads(result.text)

    def _post(self, url, data):
        result = self.session.post(API_ROOT + url, data=data)
        return json.loads(result.text)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('specify a directory to upload')
        sys.exit(1)

    client = Client()
    client.upload_album(sys.argv[1])
