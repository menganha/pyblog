import datetime as dt
from pathlib import Path
from textwrap import dedent

import pytest

from pyblog.post import Post


@pytest.fixture()
def valid_text_path(tmp_path) -> Path:
    text = dedent("""
    draft: yes
    tags: [lifestyle, manana]
    another_label: another_value
    date: 2022-12-11
    
    # My first post
    
    This is my firs valid post. If there's a text that seems like a tag within the post
    
    definition: not a tag
    
    it shouldn't be considered as such.
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_1(tmp_path) -> Path:
    text = dedent("""
    
    This is my first invalid post.
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_2(tmp_path) -> Path:
    text = dedent("""
    a_label: yes
    
    # Title
    
    draft: yes
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_3(tmp_path) -> Path:
    text = dedent("""
    draft: yes
   
    some other irrelevant text 
    # Title
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_4(tmp_path) -> Path:
    text = dedent("""
    source_path: some_path
   
    some other irrelevant text 
    # Title
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def dummy_target_path(tmp_path) -> Path:
    return tmp_path / 'dummy_target.html'


def test_parse_metadata(valid_text_path, dummy_target_path):
    post = Post(valid_text_path, dummy_target_path)
    expected_dict = {'draft': 'yes', 'tags': ['lifestyle', 'manana'], 'another_label': 'another_value', 'title': 'My first post',
                     'date': dt.date(2022, 12, 11)}
    assert post._metadata == expected_dict


def test_parse_markdown(valid_text_path, dummy_target_path):
    post = Post(valid_text_path, dummy_target_path)
    expected_html = dedent("""
    <p>This is my firs valid post. If there's a text that seems like a tag within the post</p>
    <p>definition: not a tag</p>
    <p>it shouldn't be considered as such.</p>
    """).strip()
    assert post.get_html() == expected_html


def test_invalid_initializer_1(invalid_text_path_1, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_1, dummy_target_path)


def test_invalid_initializer_2(invalid_text_path_2, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_2, dummy_target_path)


def test_invalid_initializer_3(invalid_text_path_3, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_3, dummy_target_path)


def test_invalid_initializer_4(invalid_text_path_3, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_3, dummy_target_path)
