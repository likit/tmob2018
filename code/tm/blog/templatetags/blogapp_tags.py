from django.template import Library, loader
from django.contrib.auth.models import Group
from django.urls import resolve

register = Library()

@register.simple_tag()
def post_date_url(post, blog_page):
    post_date = post.date
    url = blog_page.url + blog_page.reverse_subpage(
        'post_by_date_slug',
        args=(
            post_date.year,
            '{0:02}'.format(post_date.month),
            '{0:02}'.format(post_date.day),
            post.slug,
        )
    )
    return url

@register.filter(name="has_group")
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()