#!/usr/bin/env python3
import os
import sys
import requests
import base64
import json
from pathlib import Path
from time import sleep
from typing import String

from secrets import *

MASHAPE_API_ROOT = 'https://imgur-apiv3.p.mashape.com/3/'
IMGUR_API_ROOT = 'https://api.imgur.com/3/'

class ImgurClient:
    def __init__(self, client_id: String, access_token: String = None,
                 mashape_key: String = None) -> None:
        s = requests.Session()
        s.headers.update({
            'Authorization': f'Client-ID {CLIENT_ID}',
            'User-agent':  f'Album uploader 0.1',
        })

        if access_token:
            s.headers.update({ 'Authorization': f'Bearer {access_token}' })

        if mashape_key:
            s.headers.update({ 'X-Mashape-Key': MASHAPE_KEY })
            self.api_root = MASHAPE_API_ROOT
        else:
            self.api_root = IMGUR_API_ROOT

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

    client = ImgurClient(CLIENT_ID, ACCESS_TOKEN, MASHAPE_KEY)
    client.upload_album(sys.argv[1])
