from django.db import models

class FacultadRegional(models.Model):

	ciudad = models.CharField(max_length=48)
	base_url = models.URLField(max_length=256)

    class Meta:
        verbose_name = 'Facultad Regional'
        verbose_name_plural = 'Facultades Regionales'

    def __unicode__(self):
        return 'Facultad Regional ' + self.ciudad

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