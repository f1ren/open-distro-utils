# * * * * * source /home/ubuntu/.bashrc; $(which python3) /home/ubuntu/open-distro-utils/take-snapshot.py >> ~/cron.log 2>&1
import logging

from infra.log import init_logger

init_logger('snapshots.log', level=logging.DEBUG)

try:
    from infra.snapshot import SnapshotClient
    client = SnapshotClient()
    client.take_snapshot()
except Exception as e:
    logging.exception('Could not take snapshot')
    raise
