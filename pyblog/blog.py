import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pyblog.post import Post


class Pyblog:
    TEMPLATE_DIR_NAME = 'templates'
    WEBSITE_DIR_NAME = 'public'
    POSTS_DIR_NAME = 'posts'
    HOME_MAX_POSTS = 10
    POST_TEMPLATE = 'post.html'
    INDEX_TEMPLATE = 'index.html'

    def __init__(self, main_path: Path):
        # TODO: Maybe have a separate module for template operations?
        self.name = main_path.name
        self.main_path = main_path
        self.website_path = main_path / self.WEBSITE_DIR_NAME
        self.website_posts_path = self.website_path / self.POSTS_DIR_NAME  # TODO: Temporary solution for now. We might organize it them them differently
        self.posts_path = main_path / self.POSTS_DIR_NAME
        self.template_path = main_path / self.TEMPLATE_DIR_NAME
        self.template_environment = Environment(loader=FileSystemLoader(self.template_path), trim_blocks=True)
        self.template_environment.globals.update({'website_name': self.name})

    def create(self):
        if self.is_pyblog():
            print(f'Error: Input path {self.main_path} seems to contain another pyblog')
            return 1
        elif not self.is_pyblog() and self.main_path.exists():
            print(f'Error: Input path {self.main_path} already exists. Please choose a another path to create a pyblog')
            return

        local_template_path = Path(__file__).parent.parent / self.TEMPLATE_DIR_NAME

        self.main_path.mkdir(parents=True)
        self.website_path.mkdir()
        self.posts_path.mkdir()
        self.website_posts_path.mkdir()
        shutil.copytree(local_template_path, self.template_path)
        print(f'Pyblog created successfully on {self.main_path}!')

    def is_pyblog(self) -> bool:
        """ Checks whether the current directory is a pyblog, i.e., it has the relevant paths"""
        if self.website_path.exists() and self.posts_path.exists() and self.template_path.exists():
            return True
        else:
            return False

    def build_home_page(self):
        public_posts = self.get_all_public_posts()
        public_posts.sort(key=lambda x: x[1].metadata['date'])
        latest_posts = [{'path': str(self._get_target_html_path(post_path, self.website_posts_path).relative_to(self.website_path)),
                         'title': post.metadata['title'],
                         'date': post.metadata['date']} for (post_path, post) in public_posts[:self.HOME_MAX_POSTS]]
        index_template = self.template_environment.get_template(self.INDEX_TEMPLATE)
        index_html = index_template.render(latest_posts=latest_posts)
        target_path = self.website_path / 'index.html'
        target_path.write_text(index_html)

    @staticmethod
    def _get_target_html_path(input_path: Path, website_base_path: Path) -> Path:
        return website_base_path / f'{input_path.stem}.html'

    def get_all_public_posts(self) -> list[Post]:
        all_posts = []
        for post_path in self.posts_path.rglob('*md'):
            print(f'Processing {post_path}')
            with post_path.open() as file:
                raw_text = file.read()
            post = Post(raw_text)
            if post.metadata['draft'] != 'yes':
                all_posts.append((post_path, post))
        return all_posts

    def add_post(self, post_path: Path):
        target_path = self._get_target_html_path(post_path, self.website_posts_path)
        post_template = self.template_environment.get_template(self.POST_TEMPLATE)
        with post_path.open() as file:
            raw_text = file.read()
        md_post = Post(raw_text)
        html_content = md_post.get_markdown_html()
        post_html = post_template.render(title=md_post.metadata['title'], content=html_content)
        target_path.write_text(post_html)
