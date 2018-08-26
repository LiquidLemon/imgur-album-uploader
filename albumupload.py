#!/usr/bin/env python3
import os
import sys
import requests
import base64
import json
from pathlib import Path
from time import sleep
from typing import Any, Dict


class ImgurAPIError(Exception):
    def __init__(self, data):
        self.data = data

class ImgurClient:
    MASHAPE_API_ROOT = 'https://imgur-apiv3.p.mashape.com/3/'
    IMGUR_API_ROOT = 'https://api.imgur.com/3/'

    def __init__(self, client_id: str, access_token: str = None,
                 mashape_key: str = None) -> None:
        s = requests.Session()
        s.headers.update({
            'Authorization': f'Client-ID {CLIENT_ID}',
            'User-agent':  f'Album uploader 0.1',
        })

        if access_token:
            s.headers.update({ 'Authorization': f'Bearer {access_token}' })

        if mashape_key:
            s.headers.update({ 'X-Mashape-Key': MASHAPE_KEY })
            self.api_root = self.MASHAPE_API_ROOT
        else:
            self.api_root = self.IMGUR_API_ROOT

        self.session = s

    def upload_image(self, path, album):
        data = base64.encodebytes(path.read_bytes())
        return self._post('image', {
            'image': data, 'album': album, 'type': 'base64'
        })

    def upload_album(self, directory):
        try:
            album = self._post('album')
            album_id = album['data']['id']

            dir_path = Path(directory)
            files = os.listdir(dir_path)
            files.sort()

            for name in files:
                path = dir_path.joinpath(name)
                with path.open('rb') as image:
                    data = { 'album': album_id, 'type': 'binary' }
                    files = { 'image': image }
                    image = self._post('image', data=data, files=files)
                print(f'uploaded {path}')
        except ImgurAPIError as e:
            print('Unexpected error:')
            print(e.data.error)
            sys.exit(1)

    def _get(self, endpoint, **kwargs):
        return self._request('get', endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request('post', endpoint, **kwargs)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        response = self.session.request(
            method.upper(), self.api_root + endpoint, **kwargs
        )

        body = json.loads(response.text)
        if not body['success']:
            raise ImgurAPIError(body['data'])

        return body


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('specify a directory to upload')
        sys.exit(1)

    from secrets import *

    client = ImgurClient(CLIENT_ID, ACCESS_TOKEN, MASHAPE_KEY)
    client.upload_album(sys.argv[1])
