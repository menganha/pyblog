import datetime as dt
import json
import shutil
import sys
from collections.abc import Iterator
from importlib import resources
from pathlib import Path

from jinja2 import Environment, PackageLoader

from pyblog.post import Post


class Blog:
    TEMPLATE_DIR_NAME = 'templates'
    STYLE_SHEET_DIR_NAME = 'style_sheets'
    WEBSITE_DIR_NAME = 'public'
    POSTS_DIR_NAME = 'posts'
    TAGS_DIR_NAME = 'tags'
    DATA_DIR_NAME = 'data'
    POST_TEMPLATE = 'post.html'
    TAG_TEMPLATE = 'tag.html'
    ALL_TAGS_TEMPLATE = 'all_tags.html'
    INDEX_TEMPLATE = 'index.html'
    CSS_FILE_NAME = 'style.css'
    CONFIG_FILE_NAME = 'config.json'
    LAST_MODIFIED_FILE_NAME = '.pyblog.modified'
    HOME_MAX_POSTS = 10

    def __init__(self, main_path: Path):
        self.main_path = main_path

        self.website_path = main_path / self.WEBSITE_DIR_NAME
        self.website_posts_path = self.website_path / self.POSTS_DIR_NAME
        self.website_tags_path = self.website_path / self.TAGS_DIR_NAME

        self.posts_path = main_path / self.POSTS_DIR_NAME
        self.data_path = main_path / self.DATA_DIR_NAME
        self.templates_path = self.data_path / self.TEMPLATE_DIR_NAME
        self.style_sheets_path = self.data_path / self.STYLE_SHEET_DIR_NAME
        self.default_css_file_path = self.style_sheets_path / self.CSS_FILE_NAME
        self.last_modified_file_path = self.main_path / self.LAST_MODIFIED_FILE_NAME

        self.template_environment = Environment(loader=PackageLoader('pyblog'), trim_blocks=True, lstrip_blocks=True)
        self.template_environment.globals.update({'current_year': f'{dt.date.today().year}',
                                                  'website_path': self.website_path})
        self.config_path = main_path / self.CONFIG_FILE_NAME

    def create(self):
        if self.is_pyblog():
            print(f'Error! Input path {self.main_path.resolve()} seems to contain another pyblog')
            sys.exit(1)
        elif not self.is_pyblog() and self.main_path.exists():
            print(f'Error! Input path {self.main_path.resolve()} already exists. Please choose a another path to create a pyblog')
            sys.exit(1)

        self.main_path.mkdir(parents=True)
        self.website_path.mkdir()
        self.posts_path.mkdir()
        self.website_posts_path.mkdir()
        self.website_tags_path.mkdir()
        self.last_modified_file_path.touch()
        self.save_default_config()

    def load_config(self):
        """ Loads the config file and applies the globals to the environment """
        with self.config_path.open() as file:
            json_encoded = file.read()
        config = json.loads(json_encoded)
        self.template_environment.globals.update(config)

    def save_default_config(self):
        with resources.as_file(resources.files('pyblog') / self.DATA_DIR_NAME) as data_directory:
            shutil.copytree(data_directory, self.data_path, dirs_exist_ok=True)

        # TODO: think of adding a enum or something else for better control of all config variables
        config = {'website_name': self.main_path.resolve().name,
                  'website_author': '',
                  'website_description': '',
                  'website_keywords': ''}
        json_encoded = json.dumps(config)
        self.config_path.write_text(json_encoded)

    def is_pyblog(self) -> bool:
        """ Checks whether the current directory is a pyblog, i.e., it has the relevant paths"""
        if self.website_path.exists() and self.posts_path.exists() and self.data_path.exists() and self.config_path.exists():
            return True
        else:
            return False

    def build_home_page(self, posts: list[Post]):
        index_template = self.template_environment.get_template(self.INDEX_TEMPLATE)
        index_html = index_template.render(latest_posts=posts)
        target_path = self.website_path / 'index.html'
        target_path.write_text(index_html)

    def build_tag_pages(self, all_posts: list[Post]):
        all_tags = set([tag for post in all_posts for tag in post.tags])
        grouped_posts = [(tag, [post for post in all_posts if tag in post.tags]) for tag in all_tags]

        tag_template = self.template_environment.get_template(self.TAG_TEMPLATE)
        for tag, group in grouped_posts:
            tag_html = tag_template.render(tag=tag, latest_posts=group[:self.HOME_MAX_POSTS])
            target_path = self.website_tags_path / f'{tag}.html'
            target_path.write_text(tag_html)

        all_tags_template = self.template_environment.get_template(self.ALL_TAGS_TEMPLATE)
        all_tags_html = all_tags_template.render(all_tags=all_tags)
        target_path = self.website_path / f'tags.html'
        target_path.write_text(all_tags_html)

    def markdown_post_paths(self) -> Iterator[Path]:
        return self.posts_path.rglob('*md')

    def orphan_target_paths(self) -> Iterator[Path]:
        """ Returns the html paths of the current build that do not have a corresponding markdown path """
        for target_path in self.website_posts_path.rglob('*.html'):
            if not list(self.posts_path.rglob(f'{target_path.stem}.md')):
                yield target_path

    def build_post(self, post: Post):
        post_template = self.template_environment.get_template(self.POST_TEMPLATE)
        html_content = post.get_content_in_html()
        html_page = post_template.render(post=post, content=html_content)
        post.target_path.write_text(html_page)

    def get_post_target_html_path(self, post_path: Path) -> Path:
        """ Target paths are named with the same name of the input markdown file name """
        return self.website_posts_path / post_path.parent.relative_to(self.posts_path) / f'{post_path.stem}.html'
