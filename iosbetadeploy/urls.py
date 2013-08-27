from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from iosbetadeploy.views import IndexView, ProjectInstanceView, FileRedirectView, InstanceFileView
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'iOSBetaDeployServer.views.home', name='home'),
    # url(r'^iOSBetaDeployServer/', include('iOSBetaDeployServer.foo.urls')),
    url(r'^$', IndexView.as_view()),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<token>[\w\.]+)$', ProjectInstanceView.as_view(), name="project_view"),
    url(r'^(?P<token>[\w\.]+)/file_manager$', InstanceFileView.as_view(), name="instancefile_view"),
    url(r'^(?P<token>[\w\.]+)/(?P<key>[\w\-=]+)$', FileRedirectView.as_view(), name="file_redirection_view"),
)

from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)