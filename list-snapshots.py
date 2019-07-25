import logging
from infra.log import init_logger

if __name__ == '__main__':
    init_logger()
    try:
        from infra.snapshot import SnapshotClient
        client = SnapshotClient()
        client.list_snapshots()
    except Exception as e:
        logging.exception('Could not list snapshots')
        raise
