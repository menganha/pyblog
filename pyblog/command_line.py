import argparse
from pathlib import Path

from pyblog.blog import Pyblog


def parse_cli_arguments():
    parser = argparse.ArgumentParser(prog='pyblog', description='A static blog site generator')

    subparsers = parser.add_subparsers(title='subcommands', dest='command', description='valid subcommands', required=True)

    parser_init = subparsers.add_parser('init', help='Creates a new pyblog website')
    parser_init.add_argument('path', help='Initializes all the relevant files for the website on the input path')

    subparsers.add_parser('build', help='Builds the website')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_cli_arguments()
    if args.command == 'init':
        pyblog = Pyblog(Path(args.path).expanduser())
        pyblog.create()
    elif args.command == 'build':
        pyblog = Pyblog(Path('.'))
        if not pyblog.is_pyblog():
            print('Error: The current path does not contain a pyblog')
        else:
            for post_file_path in pyblog.posts_path.rglob('*md'):
                print(f'Processing {post_file_path}')
                pyblog.add_post(post_file_path)
