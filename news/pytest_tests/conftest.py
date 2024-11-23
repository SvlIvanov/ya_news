from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News

COUNT_OBJECTS = settings.NEWS_COUNT_ON_HOME_PAGE + 1
NEWS_DETAIL_URL = 'news:detail'
NEWS_DELETE_URL = 'news:delete'
NEWS_EDIT_URL = 'news:edit'
HOME_URL = 'news:home'
LOGIN_URL = 'users:login'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Просто текст.',
    )
    return news


@pytest.fixture
def news_list():
    today = timezone.now()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(COUNT_OBJECTS)
    )


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий',
    )
    return comment


@pytest.fixture
def comments(author, news):
    today = timezone.now()
    comments = []
    for index in range(COUNT_OBJECTS):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"Текст {index}",
        )
        comment.created = today + timedelta(days=index)
        comment.save()
        comments.append(comment)


@pytest.fixture
def home_url():
    return reverse(HOME_URL)


@pytest.fixture
def comment_delete_url(comment):
    return reverse(NEWS_DELETE_URL, args=str(comment.pk))


@pytest.fixture
def news_detail_url(news):
    return reverse(NEWS_DETAIL_URL, args=str(news.pk))


@pytest.fixture
def comment_edit_url(comment):
    return reverse(NEWS_EDIT_URL, args=str(comment.pk))


@pytest.fixture
def login_url():
    return reverse(LOGIN_URL)
