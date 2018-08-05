import requests
import dateutil.parser
from collections import namedtuple
from datetime import date, datetime
from django.contrib.postgres.search import SearchVector
from django import forms
from django.http import Http404, HttpResponse
from django.db import models
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils import translation
from django.utils.formats import date_format
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.api.fields import ImageRenditionField
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.api import APIField
from taggit.models import TaggedItemBase, Tag as TaggitTag
from modelcluster.fields import ParentalKey, ParentalManyToManyField, ForeignKey
from modelcluster.tags import ClusterTaggableManager
from rest_framework.fields import DateTimeField
# Create your models here.

fb_post = namedtuple('FbPost', ['post_id', 'page_id', 'story', 'message', 'created_time'])

class TranslatedField:
    def __init__(self, en_field, th_field):
        self.en_field = en_field
        self.th_field = th_field

    def __get__(self, instance, owner):
        if translation.get_language() == 'en':
            return getattr(instance, self.th_field)
        else:
            return getattr(instance, self.th_field)


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('PostPage', related_name='post_tags')


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True

#fb_page_access_token = 'EAAEzlJsTZBB8BABslGZBK5gquc526CvFhGcR4IvwDRzZC4pn7qVvgZAr7S0KJ2wqcZCcZCqdYoIWqHGWsNZCXVucU633gFiLSZCreekpUAHIzHgFW99bGlAT1028dmzbGZB41jP8Rf4PaAgS2oHx8LPxQOE43CoNweecYXuMBZBCLLcFslwXZBve8Le89xIZCMa4AP4ZD'
fb_page_id = '241755426012824'
fb_user_access_token = 'EAAEzlJsTZBB8BAFvEfLNZAQXzLV0V1YN3hWrOgW8VFZBCZBhelTWm9JphPEqkWvgjFustelwuLZBhNZAf67YmbW4kW80pYcUZCU5EwfzHT9JPuJhlv2cXEniP9w6NHMGx1XlmPAYTZAGcF8XZAHoDZB64yeeLcVPi1CTHiacerLhIPrAZDZD'

class HomePage(Page):
    description = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description')
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.get_posts()
        return context

    def get_posts(self):
        resp = requests.get('https://graph.facebook.com/v2.9/{}/posts?access_token={}'.format(fb_page_id, fb_user_access_token))
        posts = []
        activities = []
        for n,st in enumerate(resp.json()['data']):
            _id = st.get('id', None)
            _page_id, _post_id = _id.split('_')
            _story = st.get('story', '')
            _message = st.get('message', '')
            _created_time = dateutil.parser.parse(st.get('created_time', ''))
            story = fb_post(_post_id, _page_id, _story, _message, _created_time)
            posts.append(story)
            if n==4:
                break
        return posts
        # return PostPage.objects.all().live().order_by('-date')

class BlogPage(RoutablePageMixin, Page):
    description_en = models.CharField(max_length=255, blank=True)
    description_th = models.CharField(max_length=255, blank=True)
    title_th = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('title_th'),
        FieldPanel('description_en'),
        FieldPanel('description_th'),
    ]

    translated_title = TranslatedField(
        'title',
        'title_th',
    )
    description = TranslatedField(
        'description_en',
        'description_th',
    )

    def get_context(self, request, *args, **kwargs):
        context = super(BlogPage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.get_posts()
        context['blog_page'] = self
        context['categories'] = BlogCategory.objects.all()
        context['search_type'] = getattr(self, 'search_type', "")
        context['search_term'] = getattr(self, 'search_term', "")
        context['menuitems'] = self.get_children().filter(live=True, show_in_menus=True)
        return context

    def get_posts(self):
        return PostPage.objects.descendant_of(self).live().order_by('-date')

    @route(r'^search/$')
    def post_search(self, request, *args, **kwargs):
        search_query = request.GET.get('q', None)
        self.posts = self.get_posts()
        if search_query:
            self.posts = self.posts.annotate(
                search=SearchVector('title', 'title_th', 'body_en', 'body_th')).filter(search=search_query)
            self.search_term = search_query
            self.search_type = 'search'
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.posts = self.get_posts().filter(date__year=year)
        self.search_type = 'date'
        self.search_term = year
        if month:
            self.posts = self.posts.filter(date__month=month)
            df = DateFormat(date(int(year), int(month), 1))
            self.search_term = df.format('F Y')
        if day:
            self.posts = self.posts.filter(date__day=day)
            self.search_term = date_format(date(int(year), int(month), int(day)))
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^(\d{4})/(\d{2})/(\d{2})/(.+)/$')
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        post_page = self.get_posts().filter(slug=slug).first()
        if not post_page:
            raise Http404
        if request.method == 'POST':
            form = PostCommentForm(request.POST)
            if form.is_valid():
                PostComment.objects.create(
                    user=request.user,
                    comment=form.cleaned_data['comment'],
                    post=post_page
                )
        return Page.serve(post_page, request, *args, **kwargs)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts = self.get_posts().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^categoty/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.posts = self.get_posts().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return Page.serve(self, request, *args, **kwargs)

@register_snippet
class PostComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=False)
    commented_at = models.DateTimeField(default=datetime.now,
                                            null=False, blank=False)
    # use parental key to temporarily associate comments to a post page.
    # ForeignKey would replace ParentalKey for one-to-one relationship
    post = ParentalKey('PostPage', on_delete=models.SET_NULL,
                        null=True, related_name='comments')
    content_panels = Page.content_panels + [
        FieldPanel('comment', classname='full'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('commented_at'),
    ]

    def __str__(self):
        return self.comment

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-commented_at',]


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ('comment',)
        widgets = {
            'comment': forms.Textarea(attrs={'placeholder': 'Leave you comment here..'})
        }


class PostPage(RoutablePageMixin, Page):
    title_th = models.CharField(max_length=255)
    body_en = RichTextField(blank=True)
    body_th = RichTextField(blank=True)
    date = models.DateTimeField(verbose_name="Post date", default=datetime.today)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    tags = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)
    feed_image = models.ForeignKey('wagtailimages.Image', null=True,
                                    blank=True, on_delete=models.SET_NULL, related_name='+')
    content_panels = Page.content_panels + [
        FieldPanel('title_th', classname='full'),
        FieldPanel('body_en', classname='full'),
        FieldPanel('body_th', classname='full'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('date'),
    ]

    promote_panels = [
        ImageChooserPanel('feed_image'),
    ]

    api_fields = [
        APIField('pubdate', serializer=DateTimeField(format='%A %d %B %Y', source='date')),
        APIField('title_th'),
        APIField('slug'),
        APIField('body_th'),
        APIField('categories'),
        APIField('tags'),
        APIField('feed_image_thumbnail',
            serializer=ImageRenditionField('width-200', source='feed_image')),
    ]

    translated_title = TranslatedField(
        'title',
        'title_th',
    )
    body = TranslatedField(
        'body_en',
        'body_th',
    )


    @property
    def blog_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(PostPage, self).get_context(request, *args, **kwargs)
        context['blog_page'] = self.blog_page
        context['comment_form'] = PostCommentForm()
        return context



@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class AboutPage(Page):
    body_en = RichTextField(blank=True)
    body_th = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('body_en', classname='full'),
        FieldPanel('body_th', classname='full'),
    ]
    body = TranslatedField(
        'body_en',
        'body_th',
    )


class PortalPage(RoutablePageMixin,Page):
    title_th = models.CharField(max_length=255, blank=True)
    description_en = models.CharField(max_length=255, blank=True)
    description_th = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('title_th', classname='full'),
        FieldPanel('description_en', classname='full'),
        FieldPanel('description_th', classname='full'),
    ]
    translated_title = TranslatedField(
        'title',
        'title_th',
    )
    translated_description = TranslatedField(
        'description_en',
        'description_th',
    )

    def get_context(self, request, *args, **kwargs):
        context = super(PortalPage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.get_posts()
        context['portal_page'] = self
        context['menuitems'] = self.get_children().filter(live=True, show_in_menus=True)
        return context

    def get_posts(self):
        return PostPage.objects.descendant_of(self).live().order_by('-date')

    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.posts = self.get_posts().filter(date__year=year)
        self.search_type = 'date'
        self.search_term = year
        if month:
            self.posts = self.posts.filter(date__month=month)
            df = DateFormat(date(int(year), int(month), 1))
            self.search_term = df.format('F Y')
        if day:
            self.posts = self.posts.filter(date__day=day)
            self.search_term = date_format(date(int(year), int(month), int(day)))
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^(\d{4})/(\d{2})/(\d{2})/(.+)/$')
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        post_page = self.get_posts().filter(slug=slug).first()
        if not post_page:
            raise Http404
        if request.method == 'POST':
            form = PostCommentForm(request.POST)
            if form.is_valid():
                PostComment.objects.create(
                    user=request.user,
                    comment=form.cleaned_data['comment'],
                    post=post_page
                )
        return Page.serve(post_page, request, *args, **kwargs)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts = self.get_posts().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^categoty/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.posts = self.get_posts().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return Page.serve(self, request, *args, **kwargs)


class HomePageLink(Page):
    title_th = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=64, blank=True)
    description_en = models.CharField(max_length=255, blank=True)
    description_th = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('title_th', classname='full'),
        FieldPanel('description_en', classname='full'),
        FieldPanel('description_th', classname='full'),
    ]
    translated_title = TranslatedField(
        'title',
        'title_th',
    )
    translated_description = TranslatedField(
        'description_en',
        'description_th',
    )

    def get_context(self, request, *args, **kwargs):
        context = super(PortalPage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.get_posts()
        return context

    def get_posts(self):
        return HomePageLink.objects.descendant_of(self).live()
