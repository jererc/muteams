import argparse
import os

from svcutils.service import Config

from muteams.teams import Muteams


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default=os.getcwd())
    parser.add_argument('--headful', action='store_true')
    args = parser.parse_args()
    path = os.path.realpath(os.path.expanduser(args.path))
    config = Config(
        os.path.join(path, 'user_settings.py'),
        HEADLESS=not args.headful,
        TIMEOUT=60,
        LOOP_DELTA=10,
        RELOAD_MAX_ERRORS=20,
    )
    Muteams(config).run()


if __name__ == '__main__':
    main()
