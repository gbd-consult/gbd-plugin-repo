"""Doc generator CLI tool"""

import json
import os
import sys

SELF_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, SELF_DIR + '/vendor')

import dog

USAGE = """
python3 doc.py build   - generate docs
python3 doc.py server  - start the dev server
"""


def main():
    os.chdir(SELF_DIR)
    with open('options.json', encoding='utf8') as fp:
        opts = json.load(fp)
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''

    if cmd == 'build':
        dog.build_html(opts)
        return 0

    if cmd == 'server':
        dog.start_server(opts)
        return 0

    print(USAGE)
    return 1


if __name__ == '__main__':
    sys.exit(main())
