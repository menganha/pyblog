from pathlib import Path

from yabi import command_line as cli


def test_init(mocker):
    mocked_blog = mocker.patch('yabi.command_line.Blog')
    mocked_blog_create = mocked_blog.return_value.create

    test_path = Path('/one/two/path')
    cli.init(test_path)
    mocked_blog.assert_called_with(test_path)
    mocked_blog_create.assert_called()


def test_build_no_posts(created_blog, mocker):
    mock_load_config = mocker.patch.object(created_blog, 'load_config')
    mock_copy = mocker.patch('shutil.copy')
    mock_build_post = mocker.patch.object(created_blog, 'build_post')
    mock_build_home_page = mocker.patch.object(created_blog, 'build_home_page')
    mock_build_tag_page = mocker.patch.object(created_blog, 'build_tag_page')
    mock_update_last_build_file = mocker.patch.object(created_blog, 'update_last_build_file')

    cli.build(created_blog, force=False)

    mock_load_config.assert_called_once()
    mock_copy.assert_not_called()
    mock_update_last_build_file.assert_not_called()
    mock_build_post.assert_not_called()
    mock_build_home_page.assert_not_called()
    mock_build_tag_page.assert_not_called()


def test_build_change_config_files(created_blog, mocker, post_not_dirty):
    mocker.patch.object(created_blog, 'load_config')
    mock_copy = mocker.patch('shutil.copy')
    mock_build_post = mocker.patch.object(created_blog, 'build_post')
    mock_build_home_page = mocker.patch.object(created_blog, 'build_home_page')
    mock_build_tag_page = mocker.patch.object(created_blog, 'build_tag_page')
    mock_update_last_build_file = mocker.patch.object(created_blog, 'update_last_build_file')

    # modify style sheets and config files
    created_blog.style_sheets_path.touch(exist_ok=True)
    created_blog.config_path.touch(exist_ok=True)

    cli.build(created_blog, force=False)

    mock_copy.assert_called_with(created_blog.default_css_file_path, created_blog.website_path)
    mock_update_last_build_file.assert_called_once()
    assert len(mock_build_post.call_args_list) == 1
    assert mock_build_post.call_args_list[0].args[0] == post_not_dirty
    mock_build_home_page.assert_called_once()
    mock_build_tag_page.assert_called_once()


def test_build_with_posts(created_blog, mocker, post, draft_post, post_not_dirty, orphaned_target):
    mocker.patch.object(created_blog, 'load_config')
    mock_copy_tree = mocker.patch('shutil.copy')
    mock_build_post = mocker.patch.object(created_blog, 'build_post')
    mock_build_home_page = mocker.patch.object(created_blog, 'build_home_page')
    mock_build_tag_page = mocker.patch.object(created_blog, 'build_tag_page')
    mock_update_last_build_file = mocker.patch.object(created_blog, 'update_last_build_file')
    mocker.patch.object(created_blog, 'is_config_file_updated', return_value=False)

    assert orphaned_target.exists()

    cli.build(created_blog, force=False)

    mock_copy_tree.assert_called_with(created_blog.default_css_file_path, created_blog.website_path)
    mock_update_last_build_file.assert_called_once()
    mock_build_home_page.assert_called_once()
    mock_build_tag_page.assert_called_once()

    assert not orphaned_target.exists()
    assert len(mock_build_post.call_args_list) == 1
    assert mock_build_post.call_args_list[0].args[0] == post


def test_serve(mocker, tmp_path):
    mocked_httpd_serve_forever = mocker.patch('socketserver.TCPServer.serve_forever')
    mocked_chdir = mocker.patch('os.chdir')

    cli.serve(tmp_path)

    mocked_chdir.assert_called_with(tmp_path)
    mocked_httpd_serve_forever.assert_called_once()
