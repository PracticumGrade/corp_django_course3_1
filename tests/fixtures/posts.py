from datetime import datetime, timedelta
from typing import Tuple

import pytest
import pytz
from django.db.models import Model
from mixer.backend.django import Mixer

from conftest import (
    N_PER_FIXTURE, N_PER_PAGE)


@pytest.fixture
def published_post(mixer: Mixer):
    return mixer.blend('blog.Post', is_published=True)


@pytest.fixture
def posts_with_unpublished_category(mixer: Mixer, user: Model):
    return mixer.cycle(N_PER_FIXTURE).blend(
        'blog.Post', author=user, category__is_published=False)


@pytest.fixture
def future_posts(mixer: Mixer, user: Model):
    date_later_now = (
        datetime.now(tz=pytz.UTC) + timedelta(days=date)
        for date in range(1, 11)
    )
    return mixer.cycle(N_PER_FIXTURE).blend(
        'blog.Post', author=user, pub_date=date_later_now)


@pytest.fixture
def unpublished_posts_with_published_locations(
        mixer: Mixer, user, published_locations, published_category):
    return mixer.cycle(N_PER_FIXTURE).blend(
        'blog.Post', author=user, is_published=False,
        category=published_category,
        location=mixer.sequence(*published_locations))


@pytest.fixture
def post_with_published_location(
        mixer: Mixer, user, published_location, published_category):
    return mixer.blend(
        'blog.Post', location=published_location, category=published_category,
        author=user
    )


@pytest.fixture
def many_posts_with_published_locations(
        mixer: Mixer, user, published_locations, published_category):
    return mixer.cycle(N_PER_PAGE * 2).blend(
        'blog.Post', author=user, category=published_category,
        location=mixer.sequence(*published_locations))
