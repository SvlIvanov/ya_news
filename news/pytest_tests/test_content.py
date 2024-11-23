import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, news_list, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert 'news_list' in response.context
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, comments, news_detail_url):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news_object = response.context['news']
    all_comments = news_object.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_comments = sorted(all_dates)
    assert all_dates == sorted_comments


@pytest.mark.parametrize(
    'parametrized_client, form_in_page',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_form_availability_for_different_users(
        news_detail_url, parametrized_client, form_in_page
):
    response = parametrized_client.get(news_detail_url)
    assert ('form' in response.context) is form_in_page


def test_pages_contains_form(author_client, comment_edit_url):
    response = author_client.get(comment_edit_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
