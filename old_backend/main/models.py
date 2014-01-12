from django.db import models

FACULTAD_REGIONAL = {
	'frro': {
		'ciudad': 'Rosario',
		'base_url': 'http://www.alumnos.frro.utn.edu.ar/'
	}
}

class Carrera(models.Model):

	nombre = models.CharField(max_length=128)

	class Meta:
		verbose_name = 'Carrera'
		verbose_name_plural = 'Carreras'

	def __unicode__(self):
		return self.nombre

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

	class Meta:
		verbose_name = 'Materia'
		verbose_name_plural = 'Materias'

	def __unicode__(self):
		return self.nombre

class Session(models.Model):
        session = models.TextField(null=True)
        last_access = models.DateTimeField(default=timezone.now())

        def set_session(self, session):
                self.session = pickle.dumps(session)

        def get_session(self):
                return pickle.loads(self.session)

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

class Alumno(AbstractUser):

	fr = models.CharField(max_length=4)
	carrera = models.ForeignKey(Carrera, blank=True, null=True)
	legajo = models.CharField(max_length=10)
	last_activity = models.DateTimeField(default=timezone.now())
	session = models.ForeignKey(Session, null=True)
	materias = models.ManyToManyField(Materia, through='AlumnoMateriaRel')

	REQUIRED_FIELDS = ['fr', 'legajo', 'email']

	objects = AlumnoManager()

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __unicode__(self):
        return self.username

class AlumnoMateriaRel(models.Model):
    materia = models.ForeignKey(Materia)
    alumno = models.ForeignKey(Alumno)
    estado = models.CharField(max_length=32)

    # Incluye aula, nota, tomo, folio, comision (según corresponda)
    data = models.JSONField()

    def __unicode__(self):
        return u'%s: %s' % (self.materia.nombre, self.estado)

    class Meta:
        verbose_name = u'estado de materia'
        verbose_name_plural = u'estados de materia'