import argparse
import http.server
import socketserver
from pathlib import Path

from pyblog.blog import Blog


def parse_cli_arguments():
    parser = argparse.ArgumentParser(prog='pyblog', description='A static blog site generator')

    subparsers = parser.add_subparsers(title='subcommands', dest='command', description='valid subcommands', required=True)

    parser_init = subparsers.add_parser('init', help='Creates a new pyblog website')
    parser_init.add_argument('path', help='Initializes all the relevant files for the website on the input path')
    parser_init.add_argument('name', help='Name of the website')
    parser_init.add_argument('author', help='Author of the website')

    subparsers.add_parser('build', help='Builds the website')
    subparsers.add_parser('test', help='Creates a local server to check the blog locally')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_cli_arguments()
    if args.command == 'init':
        pyblog = Blog(Path(args.path).expanduser())
        pyblog.create(args.name, args.author)
        print(f'Pyblog "{args.name}" successfully created on {args.path}!')
    elif args.command == 'build':
        pyblog = Blog(Path('.'))
        if not pyblog.is_pyblog():
            print('Error: The current path does not contain a pyblog')
        else:
            pyblog.load_config()
            all_public_posts = pyblog.get_all_public_posts()
            latest_posts = all_public_posts[:pyblog.HOME_MAX_POSTS]  # Maybe handle this within the pyblog instance
            print(f'Building index...')
            pyblog.build_home_page(latest_posts)
            print(f'Building tag pages...')
            pyblog.build_tag_pages(all_public_posts)
            for post in all_public_posts:
                if post.is_dirty():
                    print(f'Processing post: {post.path}')
                    pyblog.build_post(post)
            print(f'Done!')
    elif args.command == 'test':
        pyblog = Blog(Path('.'))
        if not pyblog.is_pyblog():
            print('Error: The current path does not contain a pyblog')
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
