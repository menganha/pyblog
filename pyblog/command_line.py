import argparse
import http.server
import shutil
import socketserver
import sys
from pathlib import Path

from pyblog.blog import Blog
from pyblog.post import Post

DEFAULT_TEST_PORT = 9090
DEFAULT_TEST_HOST = 'localhost'


def parse_cli_arguments():
    parser = argparse.ArgumentParser(prog='pyblog', description='A static blog site generator')

    subparsers = parser.add_subparsers(title='subcommands', dest='command', description='valid subcommands', required=True)

    parser_init = subparsers.add_parser('init', help='Creates a new pyblog website')
    parser_init.add_argument('path', help='Initializes all the relevant files for the website on the input path')

    parser_build = subparsers.add_parser('build', help='Builds the website')
    parser_build.add_argument('--force', help='Force a clean rebuild of the entire website', action='store_true')

    subparsers.add_parser('test', help='Creates a local server to check the blog locally')

    return parser.parse_args()


def init(path: Path):
    pyblog = Blog(path.expanduser())
    pyblog.create()
    print(f' New Pyblog successfully created on {path}!')


def build(force: bool):
    pyblog = Blog(Path('.'))
    if not pyblog.is_pyblog():
        print('Error: The current path does not contain a pyblog')
        return 1
    else:
        pyblog.load_config()
        shutil.copy(pyblog.css_file_path, pyblog.website_path)
        all_public_posts = []
        needs_rebuild = False
        for path in pyblog.markdown_post_paths():
            target_path = pyblog.get_post_target_html_path(path)
            post = Post(path, target_path)
            all_public_posts.append(post)
            if post.is_public() and (post.is_dirty(target_path) or force):
                print(f'Processing post: {post.path}')
                pyblog.build_post(post)
                if not needs_rebuild:
                    needs_rebuild = True

        all_public_posts.sort(key=lambda x: x.date, reverse=True)

        # Cleanup: If a post was deleted after it had been published, then we need to delete the corresponding html file.
        for target_path in pyblog.orphan_target_paths():
            target_path.unlink()

        if needs_rebuild:
            latest_posts = all_public_posts[:pyblog.HOME_MAX_POSTS]  # Maybe handle this within the pyblog instance
            print(f'Building index...')
            pyblog.build_home_page(latest_posts)
            print(f'Building tag pages...')
            pyblog.build_tag_pages(all_public_posts)
        print(f'Done!')


def serve():
    pyblog = Blog(Path('.'))
    if not pyblog.is_pyblog():
        print('Error: The current path does not contain a pyblog')
        return 1
    else:
        import functools
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=pyblog.website_path)
        with socketserver.TCPServer((DEFAULT_TEST_HOST, DEFAULT_TEST_PORT), handler) as httpd:
            print(f'Test server running on: http://{DEFAULT_TEST_HOST}:{DEFAULT_TEST_PORT}')
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.server_close()


def execute():
    args = parse_cli_arguments()

    if args.command == 'init':
        init(args.path)

    elif args.command == 'build':
        build(args.force)

    elif args.command == 'test':
        serve()


if __name__ == '__main__':
    sys.exit(execute())
