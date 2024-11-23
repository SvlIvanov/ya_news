from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Просто текст.'}

pytestmark = pytest.mark.django_db


def test_anonymous_cant_create_comment(client,
                                       news_detail_url,
                                       login_url
                                       ):
    comment_count = Comment.objects.count()
    response = client.post(news_detail_url, data=FORM_DATA)
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comment_count


def test_user_can_create_comment(
        author_client,
        author,
        news_detail_url,
        news,
):
    Comment.objects.all().delete()
    response = author_client.post(news_detail_url, data=FORM_DATA)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news.pk == news.pk


def test_user_cant_use_bad_words(admin_client, news_detail_url):
    comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Плохой текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(news_detail_url, data=bad_words_data)
    assert Comment.objects.count() == comments_count
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
        author_client,
        news_detail_url,
        comment_delete_url,
):
    url_to_comments = f'{news_detail_url}#comments'
    comments_count_last = Comment.objects.count()
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count_last - 1


def test_author_can_edit_comment(
        author_client,
        comment,
        news_detail_url,
        comment_edit_url,
        news,
        author,
):
    url_to_comments = f'{news_detail_url}#comments'
    response = author_client.post(comment_edit_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == FORM_DATA['text']
    assert comment_from_db.news == news
    assert comment_from_db.author == author


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        comment,
        comment_edit_url,
        news,
        author,
):
    response = admin_client.post(comment_edit_url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment_from_db.news == news
    assert comment_from_db.author == author


def test_user_cant_delete_comment_of_another_user(
        admin_client,
        comment_delete_url,
):
    comments_count_last = Comment.objects.count()
    response = admin_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_last
