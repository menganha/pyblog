from pathlib import Path
import shutil

TEMPLATE_DIR_NAME = 'templates'
WEBSITE_DIR_NAME = 'public'
POSTS_DIR_NAME = 'posts'


def create_pyblog(main_path: Path):
    if main_path.exists():
        print(f'Input path {main_path} already exists. Please choose a new path')
        return

    local_template_path = Path(__file__).parent.parent / TEMPLATE_DIR_NAME
    website_path = main_path / WEBSITE_DIR_NAME
    posts_path = main_path / POSTS_DIR_NAME
    template_path = main_path / TEMPLATE_DIR_NAME

    main_path.mkdir(parents=True)
    website_path.mkdir()
    posts_path.mkdir()
    shutil.copytree(local_template_path, template_path)


if __name__ == '__main__':
    import os

    print(Path(__file__).parent.parent / TEMPLATE_DIR_NAME)
    print(os.path.abspath(__file__))
