import calendar
import datetime as dt
import json
import shutil
import sys
from collections.abc import Iterator
from importlib import resources
from pathlib import Path

from jinja2 import Environment, PackageLoader

from yabi.post import Post


class Blog:
    TEMPLATE_DIR_NAME = 'templates'
    STYLE_SHEET_DIR_NAME = 'style_sheets'
    WEBSITE_DIR_NAME = 'public'
    POSTS_DIR_NAME = 'posts'
    TAGS_DIR_NAME = 'tags'
    ARCHIVE_DIR_NAME = 'archive'
    DATA_DIR_NAME = 'data'
    POST_TEMPLATE = 'post.html'
    TAG_TEMPLATE = 'tag.html'
    ARCHIVE_TEMPLATE = 'archive.html'
    ALL_TAGS_TEMPLATE = 'all_tags.html'
    ALL_ARCHIVE_TEMPLATE = 'all_archive.html'
    INDEX_TEMPLATE = 'index.html'
    CSS_FILE_NAME = 'style.css'
    CONFIG_FILE_NAME = 'config.json'
    LAST_BUILD_FILE_NAME = '.yabi_last_build'
    HOME_MAX_POSTS = 10

    def __init__(self, main_path: Path):
        self.main_path = main_path.resolve().expanduser()

        self.website_path = main_path / self.WEBSITE_DIR_NAME
        self.website_posts_path = self.website_path / self.POSTS_DIR_NAME
        self.website_tags_path = self.website_path / self.TAGS_DIR_NAME
        self.website_archive_path = self.website_path / self.ARCHIVE_DIR_NAME

        self.posts_path = main_path / self.POSTS_DIR_NAME
        self.data_path = main_path / self.DATA_DIR_NAME
        self.templates_path = self.data_path / self.TEMPLATE_DIR_NAME
        self.style_sheets_path = self.data_path / self.STYLE_SHEET_DIR_NAME
        self.default_css_file_path = self.style_sheets_path / self.CSS_FILE_NAME
        self.last_build_file_path = self.main_path / self.LAST_BUILD_FILE_NAME

        self.template_environment = Environment(loader=PackageLoader('yabi'), trim_blocks=True, lstrip_blocks=True)
        self.template_environment.globals.update({'current_year': f'{dt.date.today().year}',
                                                  'website_path': self.website_path})
        self.config_path = main_path / self.CONFIG_FILE_NAME

    def create(self):
        if self.is_blog():
            print(f'Error! Input path {self.main_path.resolve()} seems to contain another yabi blog')
            sys.exit(1)
        elif not self.is_blog() and self.main_path.exists():
            print(f'Error! Input path {self.main_path.resolve()} already exists. Please choose a another path to create a yabi blog')
            sys.exit(1)

        self.main_path.mkdir(parents=True)
        self.posts_path.mkdir()
        self.data_path.mkdir()
        self.update_last_build_file()
        self._save_default_config()

    def load_config(self):
        """ Loads the config file and applies the globals to the environment """
        with self.config_path.open() as file:
            json_encoded = file.read()
        config = json.loads(json_encoded)
        self.template_environment.globals.update(config)

    def create_base_website(self):
        self.website_path.mkdir(exist_ok=True)
        self.website_posts_path.mkdir(exist_ok=True)
        self.website_tags_path.mkdir(exist_ok=True)
        self.website_archive_path.mkdir(exist_ok=True)
        shutil.copy(self.default_css_file_path, self.website_path)

    def update_last_build_file(self):
        """ Updates the modification time of the "last build" file which keeps track of the last build time"""
        self.last_build_file_path.touch(exist_ok=True)

    def is_config_file_updated(self) -> bool:
        if not self.last_build_file_path.exists():
            self.update_last_build_file()
            return True
        else:
            return self.config_path.stat().st_mtime > self.last_build_file_path.stat().st_mtime

    def is_blog(self) -> bool:
        """ Checks whether the current directory is a yabi blog, i.e., it has the relevant paths"""
        if self.posts_path.exists() and self.data_path.exists() and self.config_path.exists():
            return True
        else:
            return False

    def build_home_page(self, all_posts: list[Post]):
        index_template = self.template_environment.get_template(self.INDEX_TEMPLATE)
        pagination_base_path = self.website_path / 'index'
        for actual_index, previous_page, next_page, target_path, page_posts in self._iter_posts_pagination(all_posts, pagination_base_path):
            index_html = index_template.render(latest_posts=page_posts, index=actual_index,
                                               previous_page=previous_page, next_page=next_page)
            target_path.write_text(index_html)

    def build_tag_page(self, all_posts: list[Post]):
        all_tags = set([tag for post in all_posts for tag in post.tags])
        grouped_posts = [(tag, [post for post in all_posts if tag in post.tags]) for tag in all_tags]

        tag_template = self.template_environment.get_template(self.TAG_TEMPLATE)
        for tag, group in grouped_posts:
            pagination_base_path = self.website_tags_path / f'{tag}'
            for actual_index, previous_page, next_page, target_path, page_posts in self._iter_posts_pagination(group,
                                                                                                               pagination_base_path):
                tag_html = tag_template.render(tag=tag, latest_posts=page_posts, index=actual_index,
                                               previous_page=previous_page, next_page=next_page)
                target_path.write_text(tag_html)

        # Get font size increase depending on the amount of posts
        all_tags_with_sizes = [(tag, 100 + 0.5 * (len(posts))) for tag, posts in grouped_posts]

        all_tags_template = self.template_environment.get_template(self.ALL_TAGS_TEMPLATE)
        all_tags_html = all_tags_template.render(all_tags=all_tags_with_sizes)
        target_path = self.website_path / f'tags.html'
        target_path.write_text(all_tags_html)

    def build_archive_page(self, all_posts: list[Post]):
        all_months = list(set([(post.date.year, post.date.month) for post in all_posts]))
        all_months.sort(key=lambda x: x[0] * 10 - x[1], reverse=True)
        grouped_posts = {year: [] for year, _ in all_months}
        for year, month in all_months:
            month_tuple = (calendar.month_name[month],
                           [post for post in all_posts if (year == post.date.year and month == post.date.month)])
            grouped_posts[year].append(month_tuple)

        archive_template = self.template_environment.get_template(self.ARCHIVE_TEMPLATE)
        for year in grouped_posts:
            year_path = self.website_archive_path / f'{year}'
            year_path.mkdir(exist_ok=True)
            for month, group in grouped_posts[year]:
                pagination_base_path = year_path / f'{month.lower()}'
                for actual_index, previous_page, next_page, target_path, page_posts in self._iter_posts_pagination(group,
                                                                                                                   pagination_base_path):
                    tag_html = archive_template.render(month=month, year=year, latest_posts=page_posts, index=actual_index,
                                                       previous_page=previous_page, next_page=next_page)
                    target_path.write_text(tag_html)

        all_archive_template = self.template_environment.get_template(self.ALL_ARCHIVE_TEMPLATE)
        archive_html = all_archive_template.render(grouped_posts=grouped_posts)
        target_path = self.website_path / f'archive.html'
        target_path.write_text(archive_html)

    def markdown_post_paths(self) -> Iterator[Path]:
        return self.posts_path.rglob('*md')

    def orphan_target_paths(self) -> Iterator[Path]:
        """ Returns the html paths of the current build that do not have a corresponding markdown path """
        for target_path in self.website_posts_path.rglob('*.html'):
            expected_post_path = self.main_path / target_path.relative_to(self.website_path).with_suffix('.md')
            if not expected_post_path.exists():
                yield target_path

    def build_post(self, post: Post):
        post_template = self.template_environment.get_template(self.POST_TEMPLATE)
        html_content = post.get_content_in_html()
        html_page = post_template.render(post=post, content=html_content)
        post.target_path.parent.mkdir(exist_ok=True)
        post.target_path.write_text(html_page)

    def get_post_target_html_path(self, post_path: Path) -> Path:
        """ Target paths are named with the same name of the input markdown file name """
        return self.website_posts_path / post_path.parent.relative_to(self.posts_path) / f'{post_path.stem}.html'

    def _iter_posts_pagination(self, all_posts: list[Post], pagination_base_path: Path):
        if len(all_posts) <= self.HOME_MAX_POSTS:  # special case when the list of post is small enough
            actual_index = previous_page = next_page = None
            target_path = pagination_base_path.with_suffix('.html')
            yield actual_index, previous_page, next_page, target_path, all_posts
            return
        for idx, pos in enumerate(range(0, len(all_posts), self.HOME_MAX_POSTS)):
            page_posts = all_posts[pos:pos + self.HOME_MAX_POSTS]
            actual_index = idx + 1
            if idx == 0:
                target_path = pagination_base_path.with_suffix('.html')
                if len(all_posts) < self.HOME_MAX_POSTS:
                    actual_index = None
                    previous_page = None
                    next_page = None
                else:
                    pagination_base_path.mkdir(exist_ok=True)
                    previous_page = None
                    next_page = pagination_base_path / f'page_{actual_index + 1}.html'
            else:
                if idx == 1:
                    previous_page = pagination_base_path.with_suffix('.html')
                else:
                    previous_page = pagination_base_path / f'page_{actual_index - 1}.html'
                target_path = pagination_base_path / f'page_{actual_index}.html'
                # TODO: if the number of post is a multiple of HOME_MAX_POSTS then the below condition will be never satisfied
                if len(page_posts) < self.HOME_MAX_POSTS:
                    next_page = None
                else:
                    next_page = pagination_base_path / f'page_{actual_index + 1}.html'

            yield actual_index, previous_page, next_page, target_path, page_posts

    def _save_default_config(self):
        with resources.as_file(resources.files('yabi') / self.DATA_DIR_NAME) as data_directory:
            shutil.copytree(data_directory, self.data_path, dirs_exist_ok=True)

        for file in self.data_path.rglob('*'):  # refresh modification of all files to the current time
            file.touch()

        # TODO: think of adding a enum or something else for better control of all config variables
        config = {'website_name': self.main_path.resolve().name,
                  'website_author': '',
                  'website_description': '',
                  'website_keywords': '',
                  'website_root': '/'
                  }
        json_encoded = json.dumps(config)
        self.config_path.write_text(json_encoded)
