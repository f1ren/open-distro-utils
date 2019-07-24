# * * * * * source /home/ubuntu/.bashrc; $(which python3) /home/ubuntu/open-distro-utils/take-snapshot.py >> ~/cron.log 2>&1
from infra.snapshot import SnapshotClient

client = SnapshotClient()
client.take_snapshot()
