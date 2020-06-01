import logging

from infra.log import init_logger

INDEX_PATTERN = '*'
MONTHS_AGO = 3

# 0 0 2 * * . $HOME/.profile; $(which python3) /home/ubuntu/open-distro-utils/drop-old-indices.py 2>&1

if __name__ == '__main__':
    init_logger()
    try:
        from infra._es import ESClient
        from infra._index import filter_older_than
        client = ESClient()
        all_indices = client.list_indices(INDEX_PATTERN)
        old_indices = filter_older_than(all_indices, MONTHS_AGO)
        for index in old_indices:
            client.delete_index(index)
    except Exception as e:
        logging.exception('Could not take snapshot')
        raise
