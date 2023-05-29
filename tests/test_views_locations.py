from http import HTTPStatus

from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.test import RequestFactory
import pytest
from pytest import fixture
from pytest_django.asserts import assertTemplateUsed

from conftest import N_PER_PAGE, get_get_response_safely

pytestmark = [
    pytest.mark.django_db,
]


@pytest.mark.parametrize(
    "view_class, namespace, args, expected_template_name",
    [
        ("LocationListView", "blog:location_list", None, "blog/location_list.html"),
        ("LocationDetailView", "blog:location_detail", (1,), "blog/location_detail.html"),
        ("LocationCreateView", "blog:location_add", None, "blog/location_form.html"),
        ("LocationUpdateView", "blog:location_change", (1,), "blog/location_form.html"),
        ("LocationDeleteView", "blog:location_delete", (1,), "blog/location_confirm_delete.html"),
    ]
)
def test_location_views_template_name(
        user_client, published_location,
        view_class, namespace, args, expected_template_name
):
    url = reverse(namespace, args=args)
    response = get_get_response_safely(user_client, url)

    assertTemplateUsed(
        response, expected_template_name,
        msg_prefix=(
            f"Убедитесь, что что в файле `blog/view.py` в классе `{view_class}` "
            "используется шаблон согласно заданию"
        )
    )


@fixture
def location_list_view():
    try:
        from blog import views as blog_view
    except Exception as e:
        raise AssertionError(
            'Убедитесь, что в файле `blog/view.py` нет ошибок. '
            'При импорте `view.py` возникла ошибка:\n'
            f'{type(e).__name__}: {e}'
        )

    view_name = "LocationListView"
    assert hasattr(blog_view, view_name), (
        f'Убедитесь, что в файле `blog/view.py` объявлен класс `{view_name}`.'
    )

    assert issubclass(blog_view.LocationListView, ListView), (
        f'Убедитесь, что в файле `blog/view.py` класс `{view_name}` является наследником класса `ListView`.'
    )

    return blog_view.LocationListView()


def test_paginate_by_attr(location_list_view):
    assert location_list_view.paginate_by == N_PER_PAGE, (
        f'Убедитесь, что в файле `blog/view.py` в классе `LocationListView` '
        f'определен атрибут для пагинации согласно заданию.'
    )


def test_queryset_with_published_locations(location_list_view, published_locations):
    url = reverse("blog:location_list")
    request = RequestFactory().get(url)

    location_list_view.setup(request)
    queryset = location_list_view.get_queryset()

    assert list(queryset) == published_locations, (
        "Убедитесь, что к списку локаций применена фильтрации и в нем содержатся только опубликованные локации."
    )


@fixture
def location_detail_view():
    try:
        from blog import views as blog_view
    except Exception as e:
        raise AssertionError(
            'Убедитесь, что в файле `blog/view.py` нет ошибок. '
            'При импорте `view.py` возникла ошибка:\n'
            f'{type(e).__name__}: {e}'
        )

    view_name = "LocationDetailView"
    assert hasattr(blog_view, view_name), (
        f'Убедитесь, что в файле `blog/view.py` объявлен класс `{view_name}`.'
    )

    assert issubclass(blog_view.LocationListView, DetailView), (
        f'Убедитесь, что в файле `blog/view.py` класс `{view_name}` является наследником класса `DetailView`.'
    )

    return blog_view.LocationDetailView()


def test_location_detail_view_object(user_client, published_location):
    url = reverse("blog:location_detail", args=(published_location.pk,))
    response = get_get_response_safely(user_client, url)

    context_object_name = "object"
    assert context_object_name in response.context_data, (
        "Убедитесь, что в файле `blog/view.py` в классе `LocationDetailView`"
        " объект локации передается в контекст с ключом по умолчанию. "
    )
    object_ = response.context_data[context_object_name]
    assert object_ == published_location, (
        "Убедитесь, что в файле `blog/view.py` в классе `LocationDetailView`"
        " объект локации является экземпляром модели `Location`."
    )


@fixture
def location_create_view():
    try:
        from blog import views as blog_view
    except Exception as e:
        raise AssertionError(
            'Убедитесь, что в файле `blog/view.py` нет ошибок. '
            'При импорте `view.py` возникла ошибка:\n'
            f'{type(e).__name__}: {e}'
        )

    view_name = "LocationCreateView"
    assert hasattr(blog_view, view_name), (
        f'Убедитесь, что в файле `blog/view.py` объявлен класс `{view_name}`.'
    )

    assert issubclass(blog_view.LocationCreateView, CreateView), (
        f'Убедитесь, что в файле `blog/view.py` класс `{view_name}` является наследником класса `CreateView`.'
    )

    return blog_view.LocationCreateView()


def test_location_create_view_object(user_client, location_create_view):
    expected_fields = ('name',)
    actual_fields = location_create_view.fields

    if actual_fields == '__all__':
        raise AssertionError(
            "В файле `blog/view.py` в классе `LocationCreateView` "
            "при создании объекта не должны использоваться все поля модели. "
            "Проверьте перечень полей согласно заданию."
        )

    assert len(actual_fields) == len(expected_fields), (
        "В файле `blog/view.py` в классе `LocationCreateView` "
        "при создании объекта указаны все нужные поля или среди них не попали лишние."
    )

    for expected_field in expected_fields:
        assert expected_field in actual_fields, (
            f"В файле `blog/view.py` в классе `LocationCreateView` должно быть указано поле `{expected_field}`."
        )

    url = reverse("blog:location_add")
    response = user_client.post(url, data={"name": "test_name"}, follow=True)
    assert response.status_code == HTTPStatus.OK, (
        f'Убедитесь, что добавление новой локации отработало без ошибок.'
    )

    expected_template_name = "blog/location_detail.html"
    actual_template_name = response.template_name[0]

    assert actual_template_name == expected_template_name, (
        "Убедитесь, что после добавления новой локации пользователь "
        "перенаправлен на страницу с отображением нового созданного объекта."
    )


@fixture
def location_update_view():
    try:
        from blog import views as blog_view
    except Exception as e:
        raise AssertionError(
            'Убедитесь, что в файле `blog/view.py` нет ошибок. '
            'При импорте `view.py` возникла ошибка:\n'
            f'{type(e).__name__}: {e}'
        )

    view_name = "LocationUpdateView"
    assert hasattr(blog_view, view_name), (
        f'Убедитесь, что в файле `blog/view.py` объявлен класс `{view_name}`.'
    )

    assert issubclass(blog_view.LocationUpdateView, UpdateView), (
        f'Убедитесь, что в файле `blog/view.py` класс `{view_name}` является наследником класса `UpdateView`.'
    )

    return blog_view.LocationUpdateView()


def test_location_update_view_object(user_client, location_update_view, published_location):
    expected_fields = ('name',)
    actual_fields = location_update_view.fields

    if actual_fields == '__all__':
        raise AssertionError(
            "В файле `blog/view.py` в классе `LocationUpdateView` "
            "при обновлении объекта не должны использоваться все поля модели. "
            "Проверьте перечень полей согласно заданию."
        )

    assert len(actual_fields) == len(expected_fields), (
        "В файле `blog/view.py` в классе `LocationUpdateView` "
        "при обновлении объекта указаны все нужные поля или среди них не попали лишние."
    )

    for expected_field in expected_fields:
        assert expected_field in actual_fields, (
            f"В файле `blog/view.py` в классе `LocationUpdateView` должно быть указано поле `{expected_field}`."
        )

    url = reverse("blog:location_change", args=(published_location.pk,))
    response = user_client.post(url, data={"name": "new_test_name"}, follow=True)
    assert response.status_code == HTTPStatus.OK, (
        f'Убедитесь, что обновлении существующей локации отработало без ошибок.'
    )

    expected_template_name = "blog/location_detail.html"
    actual_template_name = response.template_name[0]

    assert actual_template_name == expected_template_name, (
        "Убедитесь, что после обновления локации пользователь "
        "перенаправлен на страницу с отображением обновленного объекта."
    )


@fixture
def location_delete_view():
    try:
        from blog import views as blog_view
    except Exception as e:
        raise AssertionError(
            'Убедитесь, что в файле `blog/view.py` нет ошибок. '
            'При импорте `view.py` возникла ошибка:\n'
            f'{type(e).__name__}: {e}'
        )

    view_name = "LocationDeleteView"
    assert hasattr(blog_view, view_name), (
        f'Убедитесь, что в файле `blog/view.py` объявлен класс `{view_name}`.'
    )

    assert issubclass(blog_view.LocationDeleteView, DeleteView), (
        f'Убедитесь, что в файле `blog/view.py` класс `{view_name}` является наследником класса `DeleteView`.'
    )

    return blog_view.LocationDeleteView()


def test_location_delete_view_object(user_client, location_delete_view, published_location):
    url = reverse("blog:location_delete", args=(published_location.pk,))
    response = user_client.post(url, follow=True)
    assert response.status_code == HTTPStatus.OK, (
        f'Убедитесь, что удаление существующей локации отработало без ошибок.'
    )

    expected_template_name = "blog/location_list.html"
    actual_template_name = response.template_name[0]

    assert actual_template_name == expected_template_name, (
        "Убедитесь, что после удаления локации пользователь "
        "перенаправлен на страницу со списком локаций."
    )
