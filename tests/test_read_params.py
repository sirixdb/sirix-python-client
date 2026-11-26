from pysirix.resource import Resource


def test_pagination_cursor_is_sent_as_start_node_key():
    params = Resource._build_read_params(
        None, None, None, top_level_limit=10, top_level_skip_last_node=5
    )

    assert params["startNodeKey"] == 5
    assert params["nextTopLevelNodes"] == 10
    assert "lastTopLevelNodeKey" not in params


def test_pagination_cursor_omitted_when_unset():
    params = Resource._build_read_params(None, None, None, top_level_limit=10)

    assert "startNodeKey" not in params
    assert "lastTopLevelNodeKey" not in params
