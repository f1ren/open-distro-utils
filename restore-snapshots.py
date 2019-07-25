# * * * * * source /home/ubuntu/.bashrc; $(which python3) /home/ubuntu/open-distro-utils/take-snapshot.py >> ~/cron.log 2>&1
import click
import logging
from infra.log import init_logger


@click.command(help='Restore ES snapshots')
@click.option('-d', '--first', default=None, help='First snapshot name')
@click.option('-l', '--last', default=None, help='Last snapshot name')
def main(first, last):
    from infra.snapshot import SnapshotClient

    client = SnapshotClient()
    client.restore_multiple(first, last)


if __name__ == '__main__':
    init_logger('restore-snapshots')
    try:
        main()
    except Exception as e:
        logging.exception('Could not restore snapshots')
        raise
