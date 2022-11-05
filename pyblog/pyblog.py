from pathlib import Path
from pyblog.post import Post
from jinja2 import Environment, FileSystemLoader
import shutil


class Pyblog:
    TEMPLATE_DIR_NAME = 'templates'
    WEBSITE_DIR_NAME = 'public'
    POSTS_DIR_NAME = 'posts'

    def __init__(self, main_path: Path):
        self.main_path = main_path
        self.website_path = main_path / self.WEBSITE_DIR_NAME
        self.posts_path = main_path / self.POSTS_DIR_NAME
        self.template_path = main_path / self.TEMPLATE_DIR_NAME
        self.template_environment = Environment(loader=FileSystemLoader(self.template_path))

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
        (self.website_path / 'posts').mkdir()  # TODO: Temporary solution for now
        shutil.copytree(local_template_path, self.template_path)

    def is_pyblog(self) -> bool:
        """ Checks whether the current directory is a pyblog, i.e., it has the relevant paths"""
        if self.website_path.exists() and self.posts_path.exists() and self.template_path.exists():
            return True
        else:
            return False

    def add_post(self, post_path: Path):
        target_path = self.website_path / 'posts' / f'{post_path.stem}.html'  # TODO: magic string here!
        post_template = self.template_environment.get_template('post_page.html')
        with post_path.open() as file:
            raw_text = file.read()
        md_post = Post(raw_text)
        html_content = md_post.get_markdown_html()
        post_html = post_template.render(title=md_post.metadata['title'], content=html_content)
        target_path.write_text(post_html)
