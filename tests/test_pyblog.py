import pytest
from pyblog import pyblog


def test_create_pyblog(tmp_path):
    test_path = tmp_path / 'test'
    pyblog.create_pyblog(test_path)

    expected_template_path = test_path / 'templates'
    expected_website_path = test_path / 'public'
    expected_posts_path = test_path / 'posts'

    assert test_path.exists()
    assert expected_template_path.exists()
    assert expected_website_path.exists()
    assert expected_posts_path.exists()
    assert len(list(expected_template_path.iterdir())) == 1

