import json
import os

from datetime import datetime
import requests
from enum import Enum
from requests.auth import HTTPBasicAuth

from infra.consts import USER, PASS, DEFAULT_ES_URL, REPOSITORY_NAME
from infra.log import info, log_request

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from infra.restore_strategy import RestoreStrategy, IndicesLock, ALL_INDICES

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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

    info(f'Using {file_path}')

    return expanded


class ESClient:
    def __init__(self, cert=None, key=None):
        self._cert = expand_user_and_check_exists(cert)
        self._key = expand_user_and_check_exists(key)
        assert None not in (USER, PASS)
        self._auth = HTTPBasicAuth(USER, PASS)
        self._base_url = f'{DEFAULT_ES_URL}/'

    @property
    def cert_and_key(self):
        if self._cert is not None:
            if self._key is not None:
                return self._cert, self._key
            return self._cert

    def _send(
            self,
            url,
            action_type=HttpAction.GET,
            wait=False,
            params=None,
            payload=None,
            raise_on_error=True,
            **kwargs):
        full_url = self._base_url + url
        headers = {}
        if params is None:
            params = {}
        if wait:
            params['wait_for_completion'] = 'true'
        if payload is not None:
            payload = json.dumps(payload)
            headers['Content-type'] = 'application/json'
        response = action_type(
            full_url,
            auth=self._auth,
            verify=False,
            cert=self.cert_and_key,
            params=params,
            data=payload,
            headers=headers,
            **kwargs
        )

        response_text = None
        response_dict = {}
        if response.status_code == 401:
            response_text = response.text
        else:
            response_dict = response.json()

        log_request({
            'request': {
                'full_url': full_url,
                'params': params,
                'payload': payload
            },
            'response': response_text if response_text is not None else response_dict
        })

        if raise_on_error:
            if 'error' in response_dict:
                raise ValueError(f"{response_dict['error']['type']}: {response_dict['error']['reason']}")

            if response.status_code != 200:
                raise ValueError(response_text)

        return response_dict

    def index_state(self):
        return self._send(
            '_cluster/state/metadata'
        )


class SnapshotClient(ESClient):
    def __init__(self):
        super().__init__()
        self._restore_strategy = RestoreStrategy(self)

    def take_snapshot(self, name=None):
        if name is None:
            name = datetime.now().strftime("%Y-%m-%d-%H-%M")
        info(f'Taking snapshot {name}')
        response = self._send(
            f'_snapshot/{REPOSITORY_NAME}/{name}',
            action_type=HttpAction.PUT,
            wait=True
        )
        debug_str = f'Done snapshot {response["snapshot"]["snapshot"]}'
        debug_str += ', indices ' + ','.join(response['snapshot']['indices'])
        debug_str += ', failures [' + ','.join(response['snapshot']['failures']) + ']'
        info(debug_str)
        return response

    def list_snapshots(self, repository=REPOSITORY_NAME):
        info('Listing snapshots')
        snapshots = self._send(f'_snapshot/{repository}/_all')['snapshots']
        snapshot_names = [s['snapshot'] for s in snapshots]
        if len(snapshot_names) == 0:
            info('No snapshots found')
        else:
            info(f'Found {len(snapshot_names)} snapshots: ' + ', '.join(snapshot_names[:3]) + (
                ' ...' if len(snapshot_names) > 3 else ''))
        return snapshot_names

    def restore(self, snapshot, repository=REPOSITORY_NAME):
        strategy = self._restore_strategy
        strategy.run(snapshot, repository)

    def send_restore(self, snapshot, repository=REPOSITORY_NAME, payload=None):
        response = self._send(
            f'_snapshot/{repository}/{snapshot}/_restore',
            action_type=HttpAction.POST,
            wait=True,
            payload=payload,
            raise_on_error=False
        )
        return response

    def _do_on_multiple(self, action, first=None, last=None):
        all_snapshots = self.list_snapshots()
        for snapshot in all_snapshots:
            if first is not None and first > snapshot or last is not None and last < snapshot:
                info(f'Skipping {snapshot}')
                continue
            action(snapshot)

    def restore_multiple(self, first=None, last=None):
        with IndicesLock(self):
            self._do_on_multiple(self.restore, first, last)

    def close_indices(self, indices=None):
        info('Close all indices')
        response = self._send(
            f'{",".join(ALL_INDICES)}/_close',
            action_type=HttpAction.POST,
        )
        info('Done close all indices')

    def open_indices(self):
        info('Open all indices')
        self._send(
            f'{",".join(ALL_INDICES)}/_open',
            action_type=HttpAction.POST,
        )
        info('Done open all indices')

    def delete(self, snapshot, repository=REPOSITORY_NAME):
        info(f'Deleting {snapshot}')
        response = self._send(
            f'_snapshot/{repository}/{snapshot}',
            action_type=HttpAction.DELETE
        )
        info(f'Done deleting {snapshot}')
        return response

    def delete_multiple(self, first=None, last=None):
        self._do_on_multiple(self.delete, first=first, last=last)

    def create_repo(self, s3_bucket_name, repository=REPOSITORY_NAME):
        return self._send(
            f'_snapshot/{repository}',
            action_type=HttpAction.PUT,
            payload={
                "type": "s3",
                "settings": {
                    "bucket": s3_bucket_name,
                    "base_path": repository
                }
            }
        )


if __name__ == '__main__':
    print(SnapshotClient().index_state())
