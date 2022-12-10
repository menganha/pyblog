import datetime as dt
from inspect import cleandoc
from pathlib import Path

import pytest

from yabi.post import Post


@pytest.fixture()
def valid_text_path(tmp_path) -> Path:
    text = cleandoc("""
    draft: yes
    tags: [lifestyle, manana]
    another_label: another_value
       weird_label: sola   
    paco  :   perfume
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
def valid_text_no_date_path(tmp_path) -> Path:
    text = cleandoc("""
    draft: yes

    # My no date post
    
    This post does not have a date but it should!

    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_1(tmp_path) -> Path:
    text = cleandoc("""
    
    This is my first invalid post.
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_2(tmp_path) -> Path:
    text = cleandoc("""
    a_label: yes
    
    # Title
    
    draft: yes
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_3(tmp_path) -> Path:
    text = cleandoc("""
    draft: yes
   
    some other irrelevant text 
    # Title
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_4(tmp_path) -> Path:
    text = cleandoc("""
    source_path: some_path
   
    some other irrelevant text 
    # Title
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def invalid_text_path_5(tmp_path) -> Path:
    text = cleandoc("""
    draft: no

    ##  A second level header title
    
    no no no
    """)
    post_path = tmp_path / 'post.md'
    post_path.write_text(text)
    return post_path


@pytest.fixture()
def dummy_target_path(tmp_path) -> Path:
    return tmp_path / 'dummy_target.html'


def test_parse_metadata(valid_text_path, dummy_target_path):
    post = Post(valid_text_path, dummy_target_path)
    expected_dict = {'draft': 'yes', 'tags': ['lifestyle', 'manana'], 'another_label': 'another_value',
                     'title': 'My first post', 'paco': 'perfume', 'weird_label': 'sola', 'date': dt.date(2022, 12, 11)}
    assert post._metadata == expected_dict


def test_parse_markdown(valid_text_path, dummy_target_path):
    post = Post(valid_text_path, dummy_target_path)
    expected_html = cleandoc("""
    <p>This is my firs valid post. If there's a text that seems like a tag within the post</p>
    <p>definition: not a tag</p>
    <p>it shouldn't be considered as such.</p>
    """).strip()
    assert post.get_content_in_html() == expected_html


def test_add_date_to_file(valid_text_no_date_path, dummy_target_path):
    post = Post(valid_text_no_date_path, dummy_target_path)
    todays_date = dt.date.today()
    expected_post_file_content = cleandoc(f"""
    date: {todays_date.isoformat()}
    draft: yes

    # My no date post
    
    This post does not have a date but it should!
    
    """)
    assert post._metadata['date'] == todays_date
    with post.source_path.open() as file:
        post_file_content = file.read()
    assert expected_post_file_content == post_file_content


def test_invalid_initializer_1(invalid_text_path_1, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_1, dummy_target_path)


def test_invalid_initializer_2(invalid_text_path_2, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_2, dummy_target_path)


def test_invalid_initializer_3(invalid_text_path_3, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_3, dummy_target_path)


def test_invalid_initializer_4(invalid_text_path_4, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_4, dummy_target_path)


def test_invalid_initializer_5(invalid_text_path_5, dummy_target_path):
    with pytest.raises(ValueError):
        Post(invalid_text_path_5, dummy_target_path)

def test_equality(valid_text_path, dummy_target_path, tmp_path):
    post = Post(valid_text_path, dummy_target_path)
    post_another_instance = Post(valid_text_path, dummy_target_path)
    post_different_dummy_target_path = Post(valid_text_path, tmp_path / 'another_dummy_target.html')
    assert post != post_different_dummy_target_path
    assert post == post_another_instance
