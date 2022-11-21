import argparse
import functools
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


def build(blog: Blog, force: bool):
    blog.load_config()
    shutil.copy(blog.css_file_path, blog.website_path)
    all_public_posts = []
    needs_rebuild = False
    for path in blog.markdown_post_paths():
        target_path = blog.get_post_target_html_path(path)
        post = Post(path, target_path)
        all_public_posts.append(post)
        if post.is_public() and (post.is_dirty(target_path) or force):
            print(f'Building post {post.path}...')
            blog.build_post(post)
            if not needs_rebuild:
                needs_rebuild = True

    all_public_posts.sort(key=lambda x: x.date, reverse=True)

    # Cleanup: If a post was deleted after it had been published, then we need to delete the corresponding html file.
    for target_path in blog.orphan_target_paths():
        target_path.unlink()

    if needs_rebuild:
        latest_posts = all_public_posts[:blog.HOME_MAX_POSTS]  # Maybe handle this within the blog instance
        print(f'Building index...')
        blog.build_home_page(latest_posts)
        print(f'Building tag pages...')
        blog.build_tag_pages(all_public_posts)
    print(f'Done!')


def serve(blog: Blog):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=blog.website_path)
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

    else:
        pyblog = Blog(Path('.'))
        if not pyblog.is_pyblog():
            print('Error: The current path does not contain a pyblog')
            return 1

        if args.command == 'build':
            build(pyblog, args.force)

        elif args.command == 'test':
            serve(pyblog)


if __name__ == '__main__':
    sys.exit(execute())
