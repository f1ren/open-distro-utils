# * * * * * source /home/ubuntu/.bashrc; $(which python3) /home/ubuntu/open-distro-utils/take-snapshot.py >> ~/cron.log 2>&1
import sys

import click
import logging

from infra.consts import DEFAULT_ADMIN_CERT_PATH, DEFAULT_ADMIN_KEY_PATH
from infra.log import init_logger


@click.command()
@click.option('-c', '--admin-cert', default=DEFAULT_ADMIN_CERT_PATH, help='Admin certification path (e.g. {DEFAULT_ADMIN_CERT_PATH})')
@click.option('-k', '--admin-key', default=DEFAULT_ADMIN_KEY_PATH, help='Admin key path (e.g. {DEFAULT_ADMIN_KEY_PATH})')
@click.option('-d', '--first', default=None, help='First snapshot name')
@click.option('-l', '--last', default=None, help='Last snapshot name')
def main(admin_cert, admin_key, first, last):
    f"""
    Restore ES snapshots using ROOT_CA_CERT and ADMIN_KEY
    See https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/snapshot-restore/#security-plugin-considerations
    """
    from infra.snapshot import SnapshotClient

    client = SnapshotClient(admin_cert, admin_key)
    client.restore_multiple(first, last)


if __name__ == '__main__':
    init_logger('restore-snapshots')
    try:
        main()
    except Exception as e:
        logging.exception('Could not restore snapshots')
        sys.exit(1)
