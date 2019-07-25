import os

DEFAULT_ES_URL = os.environ.get('ES_URL', 'https://localhost:9200')
REPOSITORY_NAME = os.environ.get('ES_SNAPSHOT_REPOSITORY')
USER = os.environ.get('ES_SNAPSHOT_USER')
PASS = os.environ.get('ES_SNAPSHOT_PASS')
DEFAULT_ADMIN_CERT_PATH = os.environ.get('ES_ADMIN_CERT', 'admin-cert.pem')
DEFAULT_ADMIN_KEY_PATH = os.environ.get('ES_ADMIN_KEY', 'admin-secret.pem')
