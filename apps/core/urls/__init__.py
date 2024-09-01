# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin, sitemaps
from django.contrib.sitemaps.views import sitemap
from django.urls import path, reverse
from django.views.generic import TemplateView

from apps.core.views import MainPage, favicon
from apps.qr.views import GetSaveQr


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "monthly"
    # i18n = True

    def items(self):
        return ["main_page", "qr_manual", "qr_scan"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
}

api = [
    path("v1/", include("apps.core.urls.v1")),
]

urlpatterns = [
    path("qr/manual/", MainPage.as_view(), name='qr_manual', kwargs={'mode': 'manual'}),
    path("qr/scan/", MainPage.as_view(), name='qr_scan', kwargs={'mode': 'scan'}),
    path("qr/<str:rnd_id>/edit/", MainPage.as_view(), name='qr_edit', kwargs={'mode': 'edit'}),
    path("qr/<str:rnd_id>/", GetSaveQr.as_view(), name='qr_open', kwargs={'mode': 'open'}),

    path('lang/', MainPage.as_view(), name='main_page_lang', kwargs={'mode': 'lang'}),
    path('', MainPage.as_view(), name='main_page'),

    path("admin/", admin.site.urls),
    path("favicon.ico", favicon),
    path("api/", include(api)),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path('robots.txt', TemplateView.as_view(
        template_name="robots.txt", content_type="text/plain"
    )),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
