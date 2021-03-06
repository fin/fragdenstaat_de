
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings

from froide.foirequest.feeds import clean

from .models import Article


class BaseFeed(Feed):
    protocol = settings.META_SITE_PROTOCOL
    limit = 20

    def __call__(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(*args, **kwargs)
        response = cache.get(cache_key)

        if response is None:
            response = super().__call__(request, *args, **kwargs)
            cache.set(cache_key, response, 900)  # cache for 15 minutes

        return response

    def get_cache_key(self, *args, **kwargs):
        # Override this in subclasses for more caching control
        return "feed:%s-%s" % (
            self.__class__.__module__,
            '/'.join(['%s,%s' % (key, val) for key, val in kwargs.items()])
        )

    def title(self, obj=None):
        return settings.SITE_NAME

    @property
    def site_url(self):
        """
        Return the URL of the current site.
        """
        return settings.SITE_URL

    def item_pubdate(self, item):
        """
        Publication date of an entry.
        """
        return item.start_publication

    def get_queryset(self):
        """
        Items are published entries.
        """
        return Article.published.all()

    def item_title(self, item):
        return clean(item.title)

    def item_description(self, obj):
        return clean(obj.get_full_html_content())


class LatestArticlesFeed(BaseFeed):
    feed_copyright = settings.SITE_NAME

    def get_object(self, request):
        self.request = request
        return request

    def item_author_email(self, item):
        """
        Return the first author's email.
        Should not be called if self.item_author_name has returned None.
        """
        return ''

    def items(self):
        """
        Items are published entries.
        """
        queryset = self.get_queryset()
        return queryset[:self.limit]

    def item_link(self, item):
        return self.site_url + item.get_absolute_url()

    def feed_url(self):
        return self.site_url + reverse('blog:article-latest-feed')

    def link(self):
        """
        URL of latest entries.
        """
        return self.site_url + reverse('blog:article-latest')
