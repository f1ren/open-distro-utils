import sys

from infra.consts import USER, PASS


def validate_env_vars():
    if None in (USER, PASS):
        print('Could not find ES_ADMIN_USER and ES_ADMIN_PASS env vars')
        sys.exit(1)
    else:
        print(f'username: {USER}')
