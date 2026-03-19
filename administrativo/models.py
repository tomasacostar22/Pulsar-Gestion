import datetime

from django.db import models
from django.conf import settings

ENTRADA_DEFAULT = datetime.time(7, 0)
SALIDA_DEFAULT = datetime.time(16, 0)
SALIDA_SABADO_DEFAULT = datetime.time(12, 0)


class HorarioLaboral(models.Model):
    empleado = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="horario_laboral",
    )

    lunes_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    lunes_salida = models.TimeField(default=SALIDA_DEFAULT)
    lunes_entrada_2 = models.TimeField(null=True, blank=True)
    lunes_salida_2 = models.TimeField(null=True, blank=True)

    martes_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    martes_salida = models.TimeField(default=SALIDA_DEFAULT)
    martes_entrada_2 = models.TimeField(null=True, blank=True)
    martes_salida_2 = models.TimeField(null=True, blank=True)

    miercoles_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    miercoles_salida = models.TimeField(default=SALIDA_DEFAULT)
    miercoles_entrada_2 = models.TimeField(null=True, blank=True)
    miercoles_salida_2 = models.TimeField(null=True, blank=True)

    jueves_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    jueves_salida = models.TimeField(default=SALIDA_DEFAULT)
    jueves_entrada_2 = models.TimeField(null=True, blank=True)
    jueves_salida_2 = models.TimeField(null=True, blank=True)

    viernes_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    viernes_salida = models.TimeField(default=SALIDA_DEFAULT)
    viernes_entrada_2 = models.TimeField(null=True, blank=True)
    viernes_salida_2 = models.TimeField(null=True, blank=True)

    sabado_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    sabado_salida = models.TimeField(default=SALIDA_SABADO_DEFAULT)
    sabado_entrada_2 = models.TimeField(null=True, blank=True)
    sabado_salida_2 = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Horario Laboral"
        verbose_name_plural = "Horarios Laborales"

    def __str__(self):
        return f"Horario de {self.empleado.get_full_name() or self.empleado.username}"

    @property
    def dias(self):
        return [
            ("Lunes", self.lunes_entrada, self.lunes_salida, self.lunes_entrada_2, self.lunes_salida_2),
            ("Martes", self.martes_entrada, self.martes_salida, self.martes_entrada_2, self.martes_salida_2),
            ("Miercoles", self.miercoles_entrada, self.miercoles_salida, self.miercoles_entrada_2, self.miercoles_salida_2),
            ("Jueves", self.jueves_entrada, self.jueves_salida, self.jueves_entrada_2, self.jueves_salida_2),
            ("Viernes", self.viernes_entrada, self.viernes_salida, self.viernes_entrada_2, self.viernes_salida_2),
            ("Sabado", self.sabado_entrada, self.sabado_salida, self.sabado_entrada_2, self.sabado_salida_2),
        ]

    @property
    def total_horas_semana(self):
        total_minutos = 0
        for _, entrada, salida, entrada_2, salida_2 in self.dias:
            for e, s in [(entrada, salida), (entrada_2, salida_2)]:
                if e and s:
                    diff = (s.hour * 60 + s.minute) - (e.hour * 60 + e.minute)
                    if diff > 0:
                        total_minutos += diff
        horas = total_minutos // 60
        minutos = total_minutos % 60
        if minutos:
            return f"{horas}h {minutos}m"
        return f"{horas}h"
