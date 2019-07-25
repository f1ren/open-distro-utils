import sys

import click
import logging

from infra.log import init_logger


@click.command(help='Delete all snapshots up to LAST_SNAPSHOT_TO_DELETE')
@click.argument('last-snapshot-to-delete')
def main(last_snapshot_to_delete):
    from infra.snapshot import SnapshotClient

    client = SnapshotClient()
    client.delete_multiple('', last_snapshot_to_delete)


if __name__ == '__main__':
    init_logger()
    try:
        main()
    except Exception as e:
        logging.exception('Could not delete snapshots')
        sys.exit(1)
