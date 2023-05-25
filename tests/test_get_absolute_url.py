import pytest

pytestmark = [
    pytest.mark.django_db,
]


def test_get_absolute_url_location(published_location):
    expected_result = "/locations/1/"
    actual_result = published_location.get_absolute_url()

    assert actual_result == expected_result


def test_get_absolute_url_category(published_category):
    expected_result = f"/category/{published_category.slug}/"
    actual_result = published_category.get_absolute_url()

    assert actual_result == expected_result


def test_get_absolute_url_post(published_post):
    expected_result = "/posts/1/"
    actual_result = published_post.get_absolute_url()

    assert actual_result == expected_result
