from datetime import date, datetime
from django import forms
from django.http import Http404, HttpResponse
from django.db import models
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.formats import date_format
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from taggit.models import TaggedItemBase, Tag as TaggitTag
from modelcluster.fields import ParentalKey, ParentalManyToManyField, ForeignKey
from modelcluster.tags import ClusterTaggableManager
# Create your models here.

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('PostPage', related_name='post_tags')


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True

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
        return PostPage.objects.all().live()

class BlogPage(RoutablePageMixin, Page):
    description = models.CharField(max_length=255, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description')
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(BlogPage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.posts
        context['blog_page'] = self
        context['categories'] = BlogCategory.objects.all()
        context['search_type'] = getattr(self, 'search_type', "")
        context['search_term'] = getattr(self, 'search_term', "")
        context['menuitems'] = self.get_children().filter(live=True, show_in_menus=True)
        return context

    def get_posts(self):
        return PostPage.objects.descendant_of(self).live()

    @route(r'^search/$')
    def post_search(self, request, *args, **kwargs):
        search_query = request.GET.get('q', None)
        self.posts = self.get_posts()
        if search_query:
            self.posts = self.posts.filter(body__contains=search_query)
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
    body = RichTextField(blank=True)
    date = models.DateTimeField(verbose_name="Post date", default=datetime.today)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    tags = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('date'),
    ]

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
    body = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]
