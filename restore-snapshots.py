# * * * * * source /home/ubuntu/.bashrc; $(which python3) /home/ubuntu/open-distro-utils/take-snapshot.py >> ~/cron.log 2>&1
import click
import logging
from infra.log import init_logger


@click.command(help='Restore ES snapshots using ROOT_CA_CERT and ADMIN_KEY')
@click.argument('root-ca-cert')
@click.argument('admin-key')
@click.option('-d', '--first', default=None, help='First snapshot name')
@click.option('-l', '--last', default=None, help='Last snapshot name')
def main(cert, key, first, last):
    from infra.snapshot import SnapshotClient

    client = SnapshotClient(cert, key)
    client.restore_multiple(first, last)


if __name__ == '__main__':
    init_logger('restore-snapshots')
    try:
        main()
    except Exception as e:
        logging.exception('Could not restore snapshots')
        raise
