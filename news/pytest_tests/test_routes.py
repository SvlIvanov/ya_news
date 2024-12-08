from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
LOGIN_URL = lf('login_url')
DETAIL_URL = lf('news_detail_url')
HOME_URL = lf('home_url')
DELETE_URL = lf('comment_delete_url')
DETAIL_URL = lf('news_detail_url')
EDIT_URL = lf('comment_edit_url')
CLIENT = lf('client')
AUTHOR_CLIENT = lf('author_client')
NOT_AUTHOR_CLIENT = lf('not_author_client')

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('url', 'user_client', 'status'),
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
    ),
)
def test_pages_availability_for_user(user_client, url, status):
    response = user_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url',
    (
        EDIT_URL,
        DELETE_URL,
    ),
)
def test_redirects(client, url, login_url):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
