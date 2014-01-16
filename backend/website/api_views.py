from rest_framework import views, generics, exceptions, serializers
from rest_framework.permissions import BasePermission
from django.contrib.auth import authenticate, login, logout
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from website.auth import SysacadSession

from website.models import Alumno, EstadoMateria, Materia

class AlumnoDetailPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.pk == obj.pk:
            return True
        return False

class EstadoMateriaPermission(BasePermission):
    def has_permission(self, request, view):
        alumno_pk = view.kwargs['alumno_pk']
        if alumno_pk == request.user.pk:
            return True
        return False


class AlumnoSerializer(ModelSerializer):
    class Meta:
        model = Alumno
        fields = ('id', 'first_name', 'last_name', 'fr', 'legajo', 'email')
        read_only_fields = ('id', 'first_name', 'last_name', 'fr', 'legajo')
        write_only_fields = ('password',)

    def restore_object(self, attrs, instance=None):
        assert instance is not None, 'Solo updates.'
        password = attrs.get('password', instance.password)
        email = attrs.get('email', instance.email)

        instance.email = email
        instance.set_password(password)

        return instance

class Login(views.APIView):

    def post(self, request, format=None):
        fr = request.DATA.get('fr', '')
        legajo = request.DATA.get('legajo', '')
        password = request.DATA.get('password', '')

        user = authenticate(fr=fr, legajo=legajo, password=password)
        if user:
            login(request, user)
            serializer = AlumnoSerializer(user)
            return Response(serializer.data)
        else:
            return Response({'error': 'incorrect_login_data'}, status=401)

class Logout(views.APIView):

    def post(self, request, format=None):
        if request.user and request.user.is_authenticated():
            logout(request)
            return Response({}, 200)
        else:
            return Response({}, 401)

class AlumnosDetail(generics.RetrieveUpdateAPIView):

    def get_object(self):
        alumno = super(AlumnosDetail, self).get_object()
        if self.request.QUERY_PARAMS.get('cached', 'true') == 'false':
            # Actualizar la data del alumno
            sysacad = SysacadSession(alumno=alumno)
            try:
                datos_alumno = sysacad.estado_academico_data()['datos_alumno']
            except SysacadSession.AuthenticationError:
                raise exceptions.NotAuthenticated
            alumno.first_name, alumno.last_name = datos_alumno
            alumno.save()
            sysacad.close()

        return alumno

    model = Alumno
    serializer_class = AlumnoSerializer
    permission_classes = (AlumnoDetailPermission,)

class EstadosMateriaList(generics.ListAPIView):

    depth = 1

    def get_queryset(self):
        alumno_pk = self.kwargs['alumno_pk']
        alumno = Alumno.objects.get(pk=alumno_pk)

        if self.request.QUERY_PARAMS.get('cached', 'true') == 'false':
            # TODO: Actualizar datos de materias
            sysacad = SysacadSession(alumno=alumno)
            try:
                materias = sysacad.estado_academico_data()['materias']
            except SysacadSession.AuthenticationError:
                raise exceptions.NotAuthenticated
            sysacad.close()

            for materia in materias:
                if int(materia['anio']) == 0:
                    continue

                try:
                    materia_obj = Materia.objects.get(nombre=materia['nombre'])
                except Materia.DoesNotExist:
                    materia_obj = Materia.objects.create(
                        nombre = materia['nombre'],
                        plan = materia['plan'],
                        anio = materia['anio']
                    )

                estadomateria = alumno.materias.get_or_create(info=materia_obj)[0]
                if materia['estado']['estado'] == 'aprobada':
                    estadomateria.estado = 'aprobada'
                    estadomateria.data = {
                        'nota': materia['estado']['nota'],
                        'tomo': materia['estado']['tomo'],
                        'folio': materia['estado']['folio'],
                    }

                elif materia['estado']['estado'] == 'cursa':
                    estadomateria.estado = 'cursa'
                    estadomateria.data = {
                        'aula': materia['estado']['aula'],
                        'comision': materia['estado']['comision']
                    }

                elif materia['estado']['estado'] == 'regular':
                    estadomateria.estado = 'regular'

                else:
                    estadomateria.estado = 'no_inscripto'

                estadomateria.save()

        return alumno.materias.all()

    model = EstadoMateria