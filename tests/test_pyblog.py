import textwrap

import pytest

from pyblog.blog import Blog
from pyblog.post import Post


@pytest.fixture()
def blog_path(tmp_path):
    return tmp_path / 'test_blog'


@pytest.fixture()
def pyblog(blog_path):
    return Blog(blog_path)


@pytest.fixture()
def post(pyblog) -> Post:
    post_text = textwrap.dedent(
        """
        draft: no
        date: 2022-12-11
        
        # a title
        
        A paragraph 
        """).strip()
    pyblog.create()
    post_path = pyblog.posts_path / 'a_test_post.md'
    target_path = pyblog.website_path / 'posts' / 'a_test_post.html'
    post_path.write_text(post_text)
    return Post(post_path, target_path)


def test_create_pyblog(pyblog, blog_path):
    pyblog.create()

    expected_data_path = blog_path / 'data'
    expected_website_path = blog_path / 'public'
    expected_posts_path = blog_path / 'posts'

    assert blog_path.exists()
    assert expected_data_path.exists()
    assert expected_website_path.exists()
    assert expected_posts_path.exists()
    assert len(list(expected_data_path.iterdir())) == 1


def test_is_pyblog(pyblog):
    assert not pyblog.is_pyblog()
    pyblog.create()
    assert pyblog.is_pyblog()


def test_build_post(pyblog, post):
    pyblog.build_post(post)
    target_path = pyblog.website_path / 'posts' / 'a_test_post.html'
    target_path.exists()


def test_build_home_page(pyblog, post):
    pyblog.build_home_page([post])
    index_path = pyblog.website_path / 'index.html'
    assert index_path.exists()


def test_orphan_target_paths(pyblog):
    pyblog.create()

    deep_path = pyblog.posts_path / 'level_1' / 'level2'
    deep_path.mkdir(parents=True)
    base_path = pyblog.posts_path
    (deep_path / 'a_test_post_1.md').touch()
    (base_path / 'a_test_post_2.md').touch()

    (pyblog.website_posts_path / 'a_test_post_1.html').touch()
    (pyblog.website_posts_path / 'a_test_post_2.html').touch()
    (pyblog.website_posts_path / 'a_test_post_3.html').touch()

    orphan_paths = list(pyblog.orphan_target_paths())

    assert orphan_paths == [pyblog.website_posts_path / 'a_test_post_3.html']
