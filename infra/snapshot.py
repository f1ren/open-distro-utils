import os

from datetime import datetime
import requests
from enum import Enum
from requests.auth import HTTPBasicAuth

from infra.consts import USER, PASS, DEFAULT_ES_URL, REPOSITORY_NAME
from infra.log import debug


class HttpAction(Enum):
    GET = requests.get
    PUT = requests.put
    POST = requests.post
    DELETE = requests.delete


def expand_user_and_check_exists(file_path=None):
    if file_path is None:
        return None

    expanded = os.path.expanduser(file_path)
    if not os.path.isfile(expanded):
        raise FileNotFoundError(f'Could not find {file_path} at {expanded}')

    debug(f'Using {file_path}')

    return expanded


class SnapshotClient:
    def __init__(self, cert=None, key=None):
        self._cert = expand_user_and_check_exists(cert)
        self._key = expand_user_and_check_exists(key)
        self._auth = HTTPBasicAuth(USER, PASS)
        self._base_url = f'{DEFAULT_ES_URL}/_snapshot/'

    @property
    def cert_and_key(self):
        if self._cert is not None:
            if self._key is not None:
                return self._cert, self._key
            return self._cert

    def _send(self, url, action_type=HttpAction.GET, wait=False, **kwargs):
        full_url = self._base_url + url
        params = {}
        if wait:
            params['wait_for_completion'] = 'true'
        response = action_type(
            full_url,
            auth=self._auth,
            verify=False,
            cert=self.cert_and_key,
            params=params,
            **kwargs
        ).json()
        debug({
            'request': {
                'full_url': full_url,
                'params': params
            },
            'response': response
        })

        if 'error' in response:
            raise ValueError(response['error'])

        return response

    def take_snapshot(self, name=None):
        if name is None:
            name = datetime.now().strftime("%Y-%m-%d-%H-%M")
        debug(f'Taking snapshot {name}')
        response = self._send(
            f'{REPOSITORY_NAME}/{name}',
            action_type=HttpAction.PUT,
            wait=True
        )
        debug_str = f'Done snapshot {response["snapshot"]["snapshot"]}'
        debug_str += ', indices ' + ','.join(response['snapshot']['indices'])
        debug_str += ', failures [' + ','.join(response['snapshot']['failures']) + ']'
        debug(debug_str)
        return response

    def list_snapshots(self, repository=REPOSITORY_NAME):
        snapshots = self._send(f'{repository}/_all')['snapshots']
        snapshot_names = [s['snapshot'] for s in snapshots]
        if len(snapshot_names) == 0:
            debug('No snapshots found')
        else:
            debug(f'Found {len(snapshot_names)} snapshots: ' + ', '.join(snapshot_names[:10]) + (' ...' if len(snapshot_names) > 10 else ''))
        return snapshot_names

    def restore(self, snapshot, repository=REPOSITORY_NAME):
        debug(f'Restoring snapshot {snapshot}')
        response = self._send(
            f'{repository}/{snapshot}/_restore',
            action_type=HttpAction.POST,
            wait=True
        )
        debug(f'Restored snapshot {snapshot}')
        return response

    def _do_on_multiple(self, action, first=None, last=None):
        all_snapshots = self.list_snapshots()
        for snapshot in all_snapshots:
            if first is not None and first > snapshot or last is not None and last < snapshot:
                debug(f'Skipping {snapshot}')
                continue
            action(snapshot)

    def restore_multiple(self, first=None, last=None):
        self._do_on_multiple(self.restore, first, last)

    def delete(self, snapshot, repository=REPOSITORY_NAME):
        debug(f'Deleting {snapshot}')
        response = self._send(
            f'{repository}/{snapshot}',
            action_type=HttpAction.DELETE
        )
        debug(f'Done deleting {snapshot}')
        return response

    def delete_multiple(self, first=None, last=None):
        self._do_on_multiple(self.delete, first=first, last=last)
