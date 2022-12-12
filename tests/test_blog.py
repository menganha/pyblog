def test_create_blog(blog, blog_path):
    blog.create()

    expected_data_path = blog_path / 'data'
    expected_posts_path = blog_path / 'posts'

    assert blog_path.exists()
    assert expected_data_path.exists()
    assert expected_posts_path.exists()
    assert len(list(expected_data_path.iterdir())) == 1


def test_is_blog(blog):
    assert not blog.is_blog()
    blog.create()
    assert blog.is_blog()


def test_build_post(created_blog, post):
    created_blog.create_base_website()
    created_blog.build_post(post)
    target_path = created_blog.website_path / 'posts' / 'a_test_post.html'
    target_path.exists()


def test_build_home_page(created_blog, post):
    created_blog.create_base_website()
    created_blog.build_home_page([post])
    index_path = created_blog.website_path / 'index.html'
    assert index_path.exists()


def test_orphan_target_paths(created_blog):
    created_blog.create_base_website()
    deep_path = created_blog.posts_path / 'level_1' / 'level2'
    deep_path.mkdir(parents=True)
    base_path = created_blog.posts_path
    (deep_path / 'a_test_post_1.md').touch()
    (base_path / 'a_test_post_2.md').touch()

    (created_blog.website_posts_path / 'a_test_post_1.html').touch()
    (created_blog.website_posts_path / 'a_test_post_2.html').touch()
    (created_blog.website_posts_path / 'a_test_post_3.html').touch()

    orphan_paths = set(created_blog.orphan_target_paths())

    assert orphan_paths == {created_blog.website_posts_path / 'a_test_post_1.html', created_blog.website_posts_path / 'a_test_post_3.html'}
