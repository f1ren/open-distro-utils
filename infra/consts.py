import os

DEFAULT_ES_URL = 'https://localhost:9200'
REPOSITORY_NAME = os.environ.get('ES_SNAPSHOT_REPOSITORY')
USER = os.environ.get('ES_SNAPSHOT_USER')
PASS = os.environ.get('ES_SNAPSHOT_PASS')
