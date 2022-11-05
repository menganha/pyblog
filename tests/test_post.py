import pytest
from textwrap import dedent
from pyblog.post import Post


@pytest.fixture()
def valid_text() -> str:
    return dedent("""
    draft: yes
    tags: [lifestyle]
    # My first post
    
    This is my firs valid post. If there's a text that seems like a tag within the post
    
    definition: not a tag
    
    it shouldn't be considered as such.
    """)


@pytest.fixture()
def invalid_text_1() -> str:
    return dedent("""
    
    This is my first invalid post.
    """)


@pytest.fixture()
def invalid_text_2() -> str:
    return dedent("""
    a_label: yes
    
    # Title
    
    draft: yes
    """)


@pytest.fixture()
def invalid_text_3() -> str:
    return dedent("""
    draft: yes
   
    some other irrelevant text 
    # Title
    """)


def test_parse_metadata(valid_text):
    metadata = Post.parse_metadata(valid_text)
    expected_dict = {'draft': 'yes', 'tags': ['lifestyle'], 'title': 'My first post'}
    assert metadata == expected_dict


def test_parse_markdown(valid_text):
    md_post = Post(valid_text)
    expected_markdown = dedent("""
    This is my firs valid post. If there's a text that seems like a tag within the post

    definition: not a tag

    it shouldn't be considered as such.
    """).strip()
    assert md_post.markdown == expected_markdown


def test_invalid_initializer_1(invalid_text_1):
    with pytest.raises(ValueError):
        Post(invalid_text_1)


def test_invalid_initializer_2(invalid_text_2):
    with pytest.raises(ValueError):
        Post(invalid_text_2)


def test_invalid_initializer_3(invalid_text_3):
    with pytest.raises(ValueError):
        Post(invalid_text_3)
