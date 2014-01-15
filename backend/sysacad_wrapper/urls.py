from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from website.auth import AuthenticationForm
from django.contrib.auth.decorators import login_required
import website.views, website.ajax_views
from website import api_views
from rest_framework.urlpatterns import format_suffix_patterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # Auth
    url(r'^api/alumnos/login/$', api_views.Login.as_view(), name='login'),
    url(r'^api/alumnos/logout/$', api_views.Logout.as_view(), name='logout'),

    # Alumnos
    url(r'^api/alumnos/(?P<pk>\d+)/$', api_views.AlumnosDetail.as_view(), name='alumnos-detail'),

    # EstadosMateria
    url(r'^api/alumnos/(?P<alumno_pk>\d+)/materias/$', api_views.EstadosMateriaList.as_view(), name='estadosmateria-list'),
#    url(r'^api/alumnos/(?P<alumno_pk>\d+)/materias/(?P<estadomateria_pk>\d+)/$', api_views.AlumnosList.as_view(), name='estadosmateria-detail'),

    # Materias
#    url(r'^api/materias/$', api_views.MateriasList.as_view(), name='materias-list'),
#    url(r'^api/materias/(?P<pk>\d+)/$', api_views.MateriasDetail.as_view(), name='materias-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns)