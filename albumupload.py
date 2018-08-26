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
    def __init__(self, response):
        self.error = response['data']['error']
        self.status = response['status']

class ImgurClient:
    MASHAPE_API_ROOT = 'https://imgur-apiv3.p.mashape.com/3/'
    IMGUR_API_ROOT = 'https://api.imgur.com/3/'

    def __init__(self, client_id: str, access_token: str = None,
                 mashape_key: str = None) -> None:
        s = requests.Session()
        s.headers.update({
            'Authorization': f'Client-ID {client_id}',
            'User-agent':  f'Album uploader 0.1',
        })

        if access_token:
            s.headers.update({ 'Authorization': f'Bearer {access_token}' })

        if mashape_key:
            s.headers.update({ 'X-Mashape-Key': mashape_key })
            self.api_root = self.MASHAPE_API_ROOT
        else:
            self.api_root = self.IMGUR_API_ROOT

        self.session = s

    def upload_album(self, directory):
        album = None
        try:
            album = self._post('album')
        except ImgurAPIError as e:
            print('Unexpected error:')
            print(e.data['error'])
            sys.exit(1)

        album_id = album['id']

        dir_path = Path(directory)
        files = os.listdir(dir_path)
        files.sort()
        n = len(files)

        for i, name in enumerate(files):
            path = dir_path.joinpath(name)
            print('\033K', end='')
            print(f'Uploading {path} ({i+1}/{n})', end='\r')
            try:
                self.upload_image(path, album=album_id)
            except ImgurAPIError as e:
                print(f"Unexpected error encountered while uploading '{path}':")
                print(e.data['error'])
                sys.exit(1)
        print(f"Uploading '{dir_path}' complete")
        print(f'See it at {album["link"]}')

    def upload_image(self, path, **kwargs):
        data = kwargs
        data['type'] = 'binary'

        with path.open('rb') as image:
            files = { 'image': image }
            return self._post('image', data=data, files=files)

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
            raise ImgurAPIError(body)

        return body['data']


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('specify a directory to upload')
        sys.exit(1)

    from secrets import *

    client = ImgurClient(CLIENT_ID, ACCESS_TOKEN, MASHAPE_KEY)
    client.upload_album(sys.argv[1])
