from datetime import datetime
import requests
from enum import Enum
from pandas import json
from requests.auth import HTTPBasicAuth

from infra.consts import USER, PASS, DEFAULT_ES_URL, REPOSITORY_NAME
from infra.log import debug


def print_json(d):
    debug(json.dumps(d, indent=2))


class HttpAction(Enum):
    GET = requests.get
    PUT = requests.put
    POST = requests.post


class SnapshotClient:
    def __init__(self):
        self._auth = HTTPBasicAuth(USER, PASS)
        self._base_url = f'{DEFAULT_ES_URL}/_snapshot/'

    def _send(self, url, action_type=HttpAction.GET):
        full_url = f'{self._base_url}/{url}'
        response = action_type.value(
            full_url,
            auth=self._auth,
            verify=False
        ).json()

        if 'error' in response:
            print_json(response)
            raise ValueError(response['error'])

        return response

    def take_snapshot(self, name=None):
        if name is None:
            name = datetime.now().strftime("%Y-%m-%d %H")

        return self._send(f'{REPOSITORY_NAME}/{name}', action_type=HttpAction.PUT)

    def list_snapshots(self, repository=REPOSITORY_NAME):
        snapshots = self._send(f'{repository}/_all')
        debug(f'Found {len(snapshots)} snapshots')
        return snapshots

    def restore(self, snapshot, repository=REPOSITORY_NAME):
        return self._send(f'{repository}/{snapshot}/_restore', action_type=HttpAction.POST)

    def restore_all_snapshots(self, repository=REPOSITORY_NAME):
        for snapshot in self.list_snapshots(repository):
            debug(f'Restoring snapshot {snapshot}')
            self.restore(snapshot)
