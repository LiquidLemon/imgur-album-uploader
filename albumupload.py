#!/usr/bin/env python3
import os
import sys
import requests
import base64
import json
import argparse
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

    def upload_album(self, directory, album_id=None):
        if not album_id:
            try:
                album = self._post('album')
            except ImgurAPIError as e:
                print('Unexpected error while creating album:')
                print(e.error)
                sys.exit(1)
            album_id = album['id']

        dir_path = Path(directory)
        files = os.listdir(dir_path)
        files.sort()
        n = len(files)

        for i, name in enumerate(files, 1):
            path = dir_path.joinpath(name)
            print('\033[K', end='') # clear line
            print(f'Uploading {path} ({i}/{n})', end='\r')
            try:
                self.upload_image(path, album=album_id)
            except ImgurAPIError as e:
                print(f"Unexpected error encountered while uploading '{path}':")
                print(e.error)
                sys.exit(1)
        print()
        print(f"Uploading '{dir_path}' complete")
        print(f'See it at https://imgur.com/a/{album_id}')

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

def load_env(keys):
    env = {}

    secrets_path = Path('secrets.env')
    if secrets_path.is_file():
        with secrets_path.open('r') as secrets:
            for line in secrets:
                key, value = line.strip().split('=')
                env[key] = value

    for key in keys:
        value = os.getenv(key)
        if value or not key in env:
            env[key] = value

    return env

def main():
    parser = argparse.ArgumentParser(
        description='Upload collections of images to imgur'
    )

    parser.add_argument('directory', help='a directory of images to upload')
    parser.add_argument('-a', '--album',
                        help='an album to upload to')

    args = parser.parse_args()
    env = load_env(['CLIENT_ID', 'ACCESS_TOKEN', 'MASHAPE_KEY'])

    client = ImgurClient(env['CLIENT_ID'], env['ACCESS_TOKEN'],
                         env['MASHAPE_KEY'])

    album_id = args.album.lstrip('https://imgur.com/a/')
    client.upload_album(args.directory, album_id)

if __name__ == '__main__':
    main()
