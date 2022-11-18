import argparse
import http.server
import shutil
import socketserver
from pathlib import Path

from pyblog.blog import Blog


def parse_cli_arguments():
    parser = argparse.ArgumentParser(prog='pyblog', description='A static blog site generator')

    subparsers = parser.add_subparsers(title='subcommands', dest='command', description='valid subcommands', required=True)

    parser_init = subparsers.add_parser('init', help='Creates a new pyblog website')
    parser_init.add_argument('path', help='Initializes all the relevant files for the website on the input path')
    parser_init.add_argument('--name', help='Name of the website')  # ! remove them
    parser_init.add_argument('--author', help='Author of the website')

    parser_build = subparsers.add_parser('build', help='Builds the website')
    parser_build.add_argument('--force', help='Force a clean rebuild of the entire website', action='store_true')
    subparsers.add_parser('test', help='Creates a local server to check the blog locally')
    return parser.parse_args()


def execute():
    args = parse_cli_arguments()

    if args.command == 'init':

        pyblog = Blog(Path(args.path).expanduser())
        pyblog.create(args.name, args.author)
        print(f' New Pyblog successfully created on {args.path}!')

    elif args.command == 'build':

        pyblog = Blog(Path('.'))
        if not pyblog.is_pyblog():
            print('Error: The current path does not contain a pyblog')
            return 1
        else:
            pyblog.load_config()
            shutil.copy(pyblog.css_file_path, pyblog.website_path)
            all_public_posts = pyblog.get_all_public_posts()
            # TODO:! Implemente smarter rebuild. if source is dirty or has been deleted. If no post is rebuild then do not rebuild the aggregate pages.
            #   Also rebuild if the templates have changed
            needs_rebuild = False
            for post in all_public_posts:
                if post.is_dirty() or args.force:
                    print(f'Processing post: {post.path}')
                    pyblog.build_post(post)
                    if not needs_rebuild:
                        needs_rebuild = True
            if needs_rebuild:
                latest_posts = all_public_posts[:pyblog.HOME_MAX_POSTS]  # Maybe handle this within the pyblog instance
                print(f'Building index...')
                pyblog.build_home_page(latest_posts)
                print(f'Building tag pages...')
                pyblog.build_tag_pages(all_public_posts)
            print(f'Done!')

    elif args.command == 'test':

        pyblog = Blog(Path('.'))
        if not pyblog.is_pyblog():
            print('Error: The current path does not contain a pyblog')
            return 1
        else:
            import functools

            PORT = 9090
            ADDRESS = 'localhost'
            Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=pyblog.website_path)
            with socketserver.TCPServer((ADDRESS, PORT), Handler) as httpd:
                print(f'Test server running on: http://{ADDRESS}:{PORT}')
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    httpd.server_close()


if __name__ == '__main__':
    execute()
