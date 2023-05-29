from collections import namedtuple
from http import HTTPStatus
from typing import Iterable, Type, Optional, Any, Tuple

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Model, Field
from django.http import HttpResponse
from django.test.client import Client
from mixer.backend.django import mixer as _mixer

N_PER_FIXTURE = 3
N_PER_PAGE = 10
COMMENT_TEXT_DISPLAY_LEN_FOR_TESTS = 50

KeyVal = namedtuple('KeyVal', 'key val')
UrlRepr = namedtuple('UrlRepr', 'url repr')


class SafeImportFromContextManager:

    def __init__(self, import_path: str,
                 import_names: Iterable[str], import_of: str = ''):
        self._import_path: str = import_path
        self._import_names: Iterable[str] = import_names
        self._import_of = f'{import_of} ' if import_of else ''

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is ImportError:
            disp_imp_names = '`, '.join(self._import_names)
            raise AssertionError(
                f'Убедитесь, что в файле `{self._import_path}` нет ошибок. '
                f'При импорте из него {self._import_of}'
                f'`{disp_imp_names}` возникла ошибка:\n'
                f'{exc_type.__name__}: {exc_value}'
            )


with SafeImportFromContextManager(
        'blog/models.py', ['Category', 'Location', 'Post'],
        import_of='моделей'):
    try:
        from blog.models import Category, Location, Post  # noqa:F401
    except RuntimeError:
        registered_apps = set(app.name for app in apps.get_app_configs())
        need_apps = {'blog': 'blog', 'pages': 'pages'}
        if not set(need_apps.values()).intersection(registered_apps):
            need_apps = {
                'blog': 'blog.apps.BlogConfig',
                'pages': 'pages.apps.PagesConfig'}

        for need_app_name, need_app_conf_name in need_apps.items():
            if need_app_conf_name not in registered_apps:
                raise AssertionError(
                    f'Убедитесь, что зарегистрировано приложение '
                    f'{need_app_name}'
                )

pytest_plugins = [
    'fixtures.posts',
    'fixtures.locations',
    'fixtures.categories',
]


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def user(mixer):
    User = get_user_model()
    user = mixer.blend(User)
    return user


@pytest.fixture
def user_client(user):
    client = Client()
    client.force_login(user)
    return client


class _TestModelAttrs:

    @property
    def model(self):
        raise NotImplementedError(
            'Override this property in inherited test class')

    def get_parameter_display_name(self, param: str) -> str:
        return param

    def test_model_attrs(self, field: str, type: type, params: dict):
        model_name = self.model.__name__
        assert hasattr(self.model, field), (
            f'В модели `{model_name}` укажите атрибут `{field}`.')
        model_field = getattr(self.model, field).field
        assert isinstance(model_field, type), (
            f'В модели `{model_name}` у атрибута `{field}` '
            f'укажите тип `{type}`.'
        )
        for param, value_param in params.items():
            display_name = self.get_parameter_display_name(param)
            assert param in model_field.__dict__, (
                f'В модели `{model_name}` для атрибута `{field}` '
                f'укажите параметр `{display_name}`.'
            )
            assert model_field.__dict__.get(param) == value_param, (
                f'В модели `{model_name}` в атрибуте `{field}` '
                f'проверьте значение параметра `{display_name}` '
                'на соответствие заданию.'
            )


@pytest.fixture
def PostModel() -> Type[Model]:
    try:
        from blog.models import Post
    except Exception as e:
        raise AssertionError(
            'Убедитесь, что в файле `blog/models.py` объявлена модель Post, '
            'и что в нём нет ошибок. '
            'При импорте модели `Post` из файла `models.py` возникла ошибка:\n'
            f'{type(e).__name__}: {e}'
        )
    return Post


def get_get_response_safely(
        user_client: Client, url: str, err_msg: Optional[str] = None
) -> HttpResponse:
    response = user_client.get(url)
    if err_msg is not None:
        assert response.status_code == HTTPStatus.OK, err_msg
    return response


def _testget_context_item_by_class(
        context, cls: type, err_msg: str,
        inside_iter: bool = False
) -> KeyVal:
    """If `err_msg` is not empty, empty return value will
    produce an AssertionError with the `err_msg` error message"""

    def is_a_match(val: Any):
        if inside_iter:
            try:
                return isinstance(iter(val).__next__(), cls)
            except Exception:
                return False
        else:
            return isinstance(val, cls)

    result: KeyVal = KeyVal(key=None, val=None)
    for key, val in dict(context).items():
        if is_a_match(val):
            result = KeyVal(key, val)
            break
    if err_msg:
        assert result.key, err_msg
    return result


def get_field_key(
        field_type: type, field: Field) -> Tuple[str, Optional[str]]:
    if field.is_relation:
        return (field_type.__name__, field.related_model.__name__)
    else:
        return (field_type.__name__, None)
