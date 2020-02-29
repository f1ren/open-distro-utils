import logging

from infra._index import filter_older_than
from infra.log import init_logger

INDEX_PATTERN = 'transcript-*'
MONTHS_AGO = 3

if __name__ == '__main__':
    init_logger()
    try:
        from infra._snapshot import ESClient
        client = ESClient()
        all_indices = client.list_indices(INDEX_PATTERN)
        old_indices = filter_older_than(all_indices, MONTHS_AGO)
        for index in old_indices:
            client.delete_index(index)
    except Exception as e:
        logging.exception('Could not take snapshot')
        raise
