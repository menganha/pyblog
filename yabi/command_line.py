import argparse
import http.server
import os
import socketserver
import sys
from pathlib import Path

from yabi.blog import Blog
from yabi.post import Post

DEFAULT_TEST_PORT = 9090
DEFAULT_TEST_HOST = 'localhost'


def parse_cli_arguments():
    parser = argparse.ArgumentParser(prog='yabi', description='A static blog site generator')

    subparsers = parser.add_subparsers(title='subcommands', dest='command', description='valid subcommands', required=True)

    parser_init = subparsers.add_parser('init', help='Creates a new yabi blog website')
    parser_init.add_argument('path', help='Initializes all the relevant files for the website on the input path')

    parser_build = subparsers.add_parser('build', help='Builds the website')
    parser_build.add_argument('--force', help='Force a clean rebuild of the entire website', action='store_true')

    subparsers.add_parser('test', help='Creates a local server to check the blog locally')

    return parser.parse_args()


def init(path: Path):
    blog = Blog(path)
    blog.create()
    print(f'New yabi blog successfully created on {path.resolve()}!')


def build(blog: Blog, force: bool):
    blog.load_config()
    all_public_posts = []
    needs_rebuild = False

    if len(list(blog.markdown_post_paths())) == 0:
        print(f'Error: No markdown posts found under the path {blog.posts_path}')
        return 1

    blog.create_base_website()

    if blog.is_config_file_updated() or force:
        print(f'The config.json file has been modified. Rebuilding whole site...')
        force = True

    for path in blog.markdown_post_paths():
        target_path = blog.get_post_target_html_path(path)
        post = Post(path, target_path)
        all_public_posts.append(post)
        if post.is_public() and (post.is_dirty(target_path) or force):
            print(f'Building post {post.source_path}...')
            blog.build_post(post)
            if not needs_rebuild:
                needs_rebuild = True

    # Cleanup: If a post was deleted after it had been published, then we need to delete the corresponding html file.
    for target_path in blog.orphan_target_paths():
        print(f'Deleting orphan page: {target_path}')
        target_path.unlink()

    if force or needs_rebuild:
        all_public_posts.sort(key=lambda x: x.date, reverse=True)
        print(f'Building index...')
        blog.build_home_page(all_public_posts)
        print(f'Building tag pages...')
        blog.build_tag_page(all_public_posts)
        print(f'Building archive pages...')
        blog.build_archive_page(all_public_posts)
        print(f'Done!')
    else:
        print('No new posts found!')

    if force or needs_rebuild:
        blog.update_last_build_file()


def serve(filepath_to_serve: Path):
    os.chdir(filepath_to_serve)
    with socketserver.TCPServer((DEFAULT_TEST_HOST, DEFAULT_TEST_PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        try:
            print(f'Test server running on: http://{DEFAULT_TEST_HOST}:{DEFAULT_TEST_PORT}')
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Shutting Down Server')
            httpd.shutdown()
            httpd.server_close()


def execute():
    args = parse_cli_arguments()

    if args.command == 'init':
        init(Path(args.path))

    else:
        blog = Blog(Path('.'))
        if not blog.is_blog():
            print(f'Error: The current path "{blog.main_path}" does not contain a yabi blog')
            if not blog.posts_path.exists():
                print(f'Error: No "{blog.POSTS_DIR_NAME}" path found on {blog.main_path}')
            if not blog.data_path.exists():
                print(f'Error: No "{blog.DATA_DIR_NAME}" path found on {blog.main_path}')
            if not blog.config_path.exists():
                print(f'Error: No {blog.CONFIG_FILE_NAME} path found on {blog.main_path}')
            return 1

        if args.command == 'build':
            build(blog, args.force)

        elif args.command == 'test':
            serve(blog.website_path)


if __name__ == '__main__':
    sys.exit(execute())
