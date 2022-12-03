import textwrap
from pathlib import Path

import pytest

from pyblog.blog import Blog
from pyblog.post import Post


@pytest.fixture()
def blog_path(tmp_path) -> Path:
    return tmp_path / 'test_blog'


@pytest.fixture()
def blog(blog_path) -> Blog:
    return Blog(blog_path)


@pytest.fixture()
def created_blog(blog) -> Blog:
    blog.create()
    return blog


@pytest.fixture()
def post(created_blog) -> Post:
    post_text = textwrap.dedent(
        """
        draft: no
        date: 2022-12-11
        
        # a title
        
        A paragraph 
        """).strip()
    post_path = created_blog.posts_path / 'a_test_post.md'
    target_path = created_blog.website_path / 'posts' / 'a_test_post.html'
    post_path.write_text(post_text)
    return Post(post_path, target_path)


@pytest.fixture()
def post_not_dirty(created_blog):
    post_text = textwrap.dedent(
        """
        draft: no
        date: 2022-12-09
        
        # a title
        
        A paragraph 
        """).strip()
    post_path = created_blog.posts_path / 'a_test_post_not_dirty.md'
    target_path = created_blog.website_path / 'posts' / 'a_test_post_not_dirty.html'
    post_path.write_text(post_text)
    target_path.touch(exist_ok=True)
    return Post(post_path, target_path)


@pytest.fixture()
def orphaned_target(created_blog):
    orphaned_target = created_blog.website_path / 'posts' / 'an_orphaned_post.html'
    orphaned_target.touch(exist_ok=True)
    return orphaned_target


@pytest.fixture()
def draft_post(created_blog) -> Post:
    post_text = textwrap.dedent(
        """
        draft: yes
        date: 2022-12-12
        
        # a title of a draft post
        
        A paragraph 
        """).strip()
    post_path = created_blog.posts_path / 'a_draft_test_post.md'
    target_path = created_blog.website_path / 'posts' / 'a_draft_test_post.html'
    post_path.write_text(post_text)
    return Post(post_path, target_path)
