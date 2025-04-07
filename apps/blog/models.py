from django.db import models
from apps.account.models import User
from django.utils.text import slugify
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.blocks import (
    CharBlock, TextBlock, RichTextBlock, URLBlock, StructBlock, StreamBlock
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from apps.shared.models import BaseModel

# Kategoriya modeli (Snippet sifatida)
@register_snippet
class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

# Teg modeli (Wagtail’da taggit yordamida boshqariladi)
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

# Blog sahifasi modeli
class BlogPage(Page):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    subtitle = models.CharField(max_length=255, blank=True)
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    # StreamField yordamida moslashuvchan content
    content = StreamField([
        ('heading', CharBlock(form_classname="full_title")),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('video', EmbedBlock()),  # YouTube, Vimeo yoki boshqa videolarni qo‘shish uchun
        ('audio', EmbedBlock()),  # SoundCloud yoki boshqa audio manbalar uchun
        ('link', URLBlock()),
        ('embedded_content', EmbedBlock()),  # Har qanday embed content uchun
    ], use_json_field=True, blank=True)

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_pages'
    )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_pages'
    )

    # Wagtail admin panelida ko‘rinadigan maydonlar
    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('featured_image'),
        FieldPanel('content'),
        FieldPanel('category'),
        FieldPanel('tags'),
        FieldPanel('status'),
        FieldPanel('author'),
        InlinePanel('comments', label="Izohlar"),
    ]

    # Qidiruv uchun maydonlar
    search_fields = Page.search_fields + [
        index.SearchField('subtitle'),
        index.SearchField('content'),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.first_published_at:
            self.first_published_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Blog Page"
        verbose_name_plural = "Blog Pages"

# Izoh modeli
class Comment(BaseModel):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wagtail_comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=False)

    panels = [
        FieldPanel('author'),
        FieldPanel('content'),
        FieldPanel('is_approved'),
    ]

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.author.username} on {self.page.title}"

# Blog ro‘yxati sahifasi
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context