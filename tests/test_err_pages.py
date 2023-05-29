import inspect
import os
import uuid

import pytest
from django.conf import settings
from django.views.csrf import csrf_failure
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_custom_err_handlers(client):
    err_pages_vs_file_names = {
        404: '404.html',
        403: '403csrf.html',
        500: '500.html'
    }
    for status, fname in err_pages_vs_file_names.items():
        fpath = settings.TEMPLATES_DIR / 'core' / fname
        assert os.path.isfile(fpath.resolve()), (
            f'Убедитесь, что файл шаблона `{fpath}` существует.'
        )

    try:
        from blogicum.urls import handler500
    except Exception:
        raise AssertionError(
            'Убедитесь, что задали обработчик ошибки со статусом 500 в '
            'головном файле с маршрутами, и что в этом файле нет ошибок.'
        )

    assert csrf_failure.__module__ not in settings.CSRF_FAILURE_VIEW, (
        'Убедитесь, что задали view-функцию для обработки ошибки CSRF-токена '
        'через настройку CSRF_FAILURE_VIEW.')

    try:
        from core import views as core_views
    except Exception:
        raise AssertionError(
            'Убедитесь, что в файле `core/views.py` нет ошибок.')

    for status, fname in err_pages_vs_file_names.items():
        assert fname in inspect.getsource(core_views), (
            'Проверьте вью функции приложения `core`: убедитесь, '
            f'что для генерации страниц со статусом ответа `{status}` '
            f'используется шаблон `core/{fname}`')

    # test template for 404
    debug = settings.DEBUG
    settings.DEBUG = False

    status = 404
    fname = err_pages_vs_file_names[status]
    non_existing_url = uuid.uuid4()
    expected_template = f'core/{fname}'
    response = client.get(non_existing_url)
    assertTemplateUsed(
        response, expected_template,
        f'Убедитесь, что для страниц со статусом ответа `{status}` '
        f'используется шаблон `{expected_template}`')

    settings.DEBUG = debug
