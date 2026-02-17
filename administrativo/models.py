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

    martes_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    martes_salida = models.TimeField(default=SALIDA_DEFAULT)

    miercoles_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    miercoles_salida = models.TimeField(default=SALIDA_DEFAULT)

    jueves_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    jueves_salida = models.TimeField(default=SALIDA_DEFAULT)

    viernes_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    viernes_salida = models.TimeField(default=SALIDA_DEFAULT)

    sabado_entrada = models.TimeField(default=ENTRADA_DEFAULT)
    sabado_salida = models.TimeField(default=SALIDA_SABADO_DEFAULT)

    class Meta:
        verbose_name = "Horario Laboral"
        verbose_name_plural = "Horarios Laborales"

    def __str__(self):
        return f"Horario de {self.empleado.get_full_name() or self.empleado.username}"

    @property
    def dias(self):
        return [
            ("Lunes", self.lunes_entrada, self.lunes_salida),
            ("Martes", self.martes_entrada, self.martes_salida),
            ("Miercoles", self.miercoles_entrada, self.miercoles_salida),
            ("Jueves", self.jueves_entrada, self.jueves_salida),
            ("Viernes", self.viernes_entrada, self.viernes_salida),
            ("Sabado", self.sabado_entrada, self.sabado_salida),
        ]

    @property
    def total_horas_semana(self):
        total_minutos = 0
        for _, entrada, salida in self.dias:
            diff = (
                salida.hour * 60 + salida.minute
            ) - (
                entrada.hour * 60 + entrada.minute
            )
            if diff > 0:
                total_minutos += diff
        horas = total_minutos // 60
        minutos = total_minutos % 60
        if minutos:
            return f"{horas}h {minutos}m"
        return f"{horas}h"
