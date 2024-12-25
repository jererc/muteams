import argparse
import os

from svcutils.service import Config

from muteams.teams import Muteams


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default=os.getcwd())
    args = parser.parse_args()
    path = os.path.realpath(os.path.expanduser(args.path))
    config = Config(
        os.path.join(path, 'user_settings.py'),
        TIMEOUT=60,
        LOOP_DELTA=30,
    )
    Muteams(config).run()


if __name__ == '__main__':
    main()
