from rest_framework import views, generics
from rest_framework.permissions import BasePermission
from django.contrib.auth import authenticate, login, logout
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response

from website.models import Alumno

class AlumnoDetailPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.pk == obj.pk:
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

    model = Alumno
    serializer_class = AlumnoSerializer
    permission_classes = (AlumnoDetailPermission,)