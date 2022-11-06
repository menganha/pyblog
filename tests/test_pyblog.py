import textwrap

import pytest

from pyblog.blog import Blog


@pytest.fixture()
def blog_path(tmp_path):
    return tmp_path / 'test_blog'


@pytest.fixture()
def pyblog(blog_path):
    return Blog(blog_path)


@pytest.fixture()
def post_path(tmp_path):
    post_path = tmp_path / 'a_test_post.md'
    post = textwrap.dedent(
        """
        draft: no
        
        # a title
        
        A paragraph 
        """).strip()
    post_path.write_text(post)
    return post_path


def test_create_pyblog(pyblog, blog_path):
    pyblog.create()

    expected_template_path = blog_path / 'templates'
    expected_website_path = blog_path / 'public'
    expected_posts_path = blog_path / 'posts'

    assert blog_path.exists()
    assert expected_template_path.exists()
    assert expected_website_path.exists()
    assert expected_posts_path.exists()
    assert len(list(expected_template_path.iterdir())) == 1


def test_add_post(pyblog, post_path):
    pyblog.create()
    pyblog.add_post(post_path)
    target_path = pyblog.website_path / 'posts' / 'a_test_post.html'
    target_path.exists()
