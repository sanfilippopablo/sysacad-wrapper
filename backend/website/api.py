from tastypie.resources import ModelResource
from tastypie.api import Api
from django.contrib.auth import authenticate, login, logout
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie import fields
from website.models import Materia, Carrera, EstadoMateria, Alumno



class MateriaResource(ModelResource):
    class Meta:
        queryset = Materia.objects.all()
        resource_name = 'materias'

class EstadoMateriaResource(ModelResource):
    class Meta:
        queryset = EstadoMateria.objects.all()
        resource_name = 'estadosmateria'

class AlumnoResource(ModelResource):
    materias = fields.ToManyField('website.api.EstadoMateriaResource', 'materias')

    class Meta:
        queryset = Alumno.objects.all()
        resource_name = 'alumnos'

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        print request.body, "asdadawd"

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        fr = data.get('fr', '')
        legajo = data.get('legajo', '')
        password = data.get('password', '')
        print fr, legajo, password

        user = authenticate(fr=fr, legajo=legajo, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                    }, HttpForbidden )
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
                }, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)

cached_api = Api(api_name='cached')
cached_api.register(MateriaResource())
cached_api.register(AlumnoResource())
cached_api.register(EstadoMateriaResource())

actual_api = Api(api_name='actual')
actual_api.register(MateriaResource())
actual_api.register(AlumnoResource())