 # -*- coding: utf-8 -*-
from __future__ import division
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils import timezone
import pickle
from jsonfield import JSONField

materia_dificultad = (
    ('e', 'Easy'),
    ('m', 'Medium'),
    ('h', 'Hard'),
)

class Materia(models.Model):

    DIFICULTADES = (
        (0, u'None'),
        (1, u'Fácil'),
        (2, u'Medio'),
        (3, u'Difícil'),
    )

    nombre = models.CharField(max_length=256)
    plan = models.CharField(max_length=4)
    anio = models.IntegerField()
    dificultad = models.IntegerField(choices=DIFICULTADES, null=True, blank=True)
    dificultad_calificaciones_cant = models.IntegerField()
    dificultad_calificaciones_sum = models.IntegerField()

    def agregar_calificacion(self, calificacion):
        if calificacion in [1, 2, 3]:
            dificultad_calificaciones_sum += calificacion
            dificultad_calificaciones_cant += 1
            self.dificultad = dificultad_calificaciones_sum / dificultad_calificaciones_cant
            return self.dificultad
        else:
            raise ValueError(u'Calificación no válida.')

    def __unicode__(self):
        return self.nombre

class AlumnoManager(BaseUserManager):

    def _create_user(self, fr, legajo, email, password,
                     is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(fr=fr, legajo=legajo, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        session = Session()
        session.save()
        user.session = session
        user.username = user.fr + user.legajo
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, fr, legajo, email=None, password=None, **extra_fields):
        return self._create_user(fr, legajo, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, fr, legajo, email, password, **extra_fields):
        return self._create_user(fr, legajo, email, password, True, True,
                                 **extra_fields)


class Session(models.Model):
    session = models.TextField(null=True)
    last_access = models.DateTimeField(default=timezone.now())

    def set_session(self, session):
        self.session = pickle.dumps(session)

    def get_session(self):
        return pickle.loads(self.session)

class Alumno(AbstractUser):

    fr = models.CharField(max_length=5)
    legajo = models.CharField(max_length=30)
    last_activity = models.DateTimeField(default=timezone.now())
    session = models.ForeignKey(Session, null=True)

    objects = AlumnoManager()

    REQUIRED_FIELDS = ['fr', 'legajo', 'email']

    def actualizar_materias(self, materias_dict):
        for mat in materias_dict:
            # Actualizar la tabla materias (esto se hace la primera vez)

            # Ignorar año materias de ingreso.
            if int(mat['anio']) == 0:
                continue

            try:
                materia_obj = Materia.objects.get(nombre=mat['nombre'])
            except Materia.DoesNotExist:
                materia_obj = Materia.objects.create(
                    nombre = mat['nombre'],
                    plan = mat['plan'],
                    anio = mat['anio']
                )

            # Actualizar materias de alumno.
            # Acá estoy seteando todo otra vez. Pero hay que verificar, no setear todo otra vez.
            # Así si detectamos un cambio mandamos la Notification.
            al_mat = self.materias.get_or_create(materia=materia_obj)[0]
            if mat['estado']['estado'] == 'aprobada':
                al_mat.estado = 'aprobada'
                al_mat.nota = mat['estado']['nota']
                al_mat.tomo = mat['estado']['tomo']
                al_mat.folio = mat['estado']['folio']
            elif mat['estado']['estado'] == 'cursa':
                al_mat.estado = 'cursa'
                al_mat.aula = mat['estado']['aula']
                al_mat.comision = mat['estado']['comision']
            elif mat['estado']['estado'] == 'regular':
                al_mat.estado = 'regular'
            al_mat.save()
        return self.materias

    def get_materia_percent(self, estado):
        return int(round((self.materias.filter(estado=estado).count() / self.materias.count()) * 100))

    def get_carrera_progress(self):
        a = self.get_materia_percent('aprobada')
        r = self.get_materia_percent('regular')
        c = self.get_materia_percent('cursa')
        return str(int(a + (r / 4) + (c / 8)))

class EstadoMateria(models.Model):
    alumno = models.ForeignKey(Alumno, related_name='materias')
    info = models.ForeignKey(Materia)
    estado = models.CharField(max_length=32)

    # Incluye aula, nota, tomo, folio, comision (según corresponda)
    data =JSONField()

    def __unicode__(self):
        return u'%s: %s' % (self.materia_info.nombre, self.estado)