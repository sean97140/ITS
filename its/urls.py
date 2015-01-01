from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from .views import home
from its.items import views as items

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'its.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home, name='home'),
    url(r'^items/checkin$', items.checkin, name='checkin'),
	url(r'^items/checkin$', items.checkin, name='index'),
    url(r'^items/itemlist$', items.itemlist, name='itemlist'),
    url(r'^items/autocomplete/?$', items.autocomplete, name='users-autocomplete'),
    url(r'^items/(?P<item_id>\d+)/$', items.printoff, name='printoff'),
    #url(r'^items/(?P<pk>\d+)/$', items.printoff, name='printoff'),


    url(r'^cloak/', include('cloak.urls'))
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static("htmlcov", document_root="htmlcov", show_indexes=True)
