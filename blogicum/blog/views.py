from datetime import datetime
from django.shortcuts import render, get_object_or_404

from .models import Post, Category


def get_now_datetime():
    return datetime.now()


def index(request):
    template_name = "blog/index.html"
    post_list = Post.objects.filter(
        pub_date__lte=get_now_datetime(),
        is_published=True,
        category__is_published=True,
    ).order_by(
        'created_at'
    )[:5]
    context = {
        "post_list": post_list
    }
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = "blog/detail.html"

    context = {
        "post":  get_object_or_404(Post, id=id, is_published=True, category__is_published=True, pub_date__lte=get_now_datetime())
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = "blog/category.html"
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    post_list = Post.objects.filter(category=category, is_published=True, pub_date__lte=get_now_datetime())

    context = {
        "category": category,
        "post_list": post_list,
    }
    return render(request, template_name, context)
