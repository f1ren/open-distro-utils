import sys

import re

from infra.log import info

DUPLICATE_PATTERN = 'index and alias names need to be unique, but the following duplicates were found \[(.*?) \(alias of \[(.*?)\]\)]'
N_RESTORE_ATTEMPTS = 20

ERRORS = [
    (DUPLICATE_PATTERN, 'duplicate index or alias')
]

SKIP_INDICES = [
    '.opendistro_security',
    '*kibana*',
    'restored-*',
    'security-auditlog-*',
]

ALL_INDICES = ['.kibana*', 'transcript-*', 'security-*', 'security-auditlog-*', '.tasks']


def _parse_error(error_msg):
    for pattern, reason in ERRORS:
        re_result = re.findall(pattern, error_msg)
        if re_result:
            return re_result[0][0], reason


class RestoreStrategy:
    def __init__(self, snapshot_client):
        self._c = snapshot_client
        self._skip_all = False
        self._skip_indices = SKIP_INDICES

    def _should_skip(self, response):
        index_name, reason = _parse_error(response['error']['reason'])
        print(f'{reason}: {index_name}')
        if self._skip_all:
            return True
        user_input = ''
        while user_input not in ('y', 'n', 'a'):
            user_input = input('Skip? (y/n/a): ')
            if user_input == 'y':
                self._skip_indices.append(index_name)
                return True
            if user_input == 'n':
                return False
            if user_input == 'a':
                self._skip_all = True

    def run(self, snapshot, repository):
        info(f'Restoring snapshot {snapshot}')
        c = self._c
        skip_indices = self._skip_indices
        indices = ','.join([f'-{index}' for index in skip_indices])

        for i in range(N_RESTORE_ATTEMPTS):
            response = c.send_restore(
                snapshot,
                repository=repository,
                payload={
                    # If a snapshot contains global state, you must exclude it when performing the restore
                    # (source: https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/snapshot-restore/#security-plugin-considerations)
                    "include_global_state": False,
                    "indices": indices,
                    # "rename_pattern": "(.+)",
                    # "rename_replacement": "restored-$1"
                },
            )

            if 'error' in response:
                if self._should_skip(response):
                    continue

                sys.exit(1)

            # OMG that's slow
            c.close_indices(response['snapshot']['indices'])

            break
        info(f'Restored snapshot {snapshot}')


class IndicesLock:
    def __init__(self, snapshot_client):
        self._c = snapshot_client

    def __enter__(self):
        self._c.close_indices()

    def __exit__(self, exception_type, exception_value, traceback):
        self._c.open_indices()
