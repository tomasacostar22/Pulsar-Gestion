from django.db import models
from django.conf import settings


class HorarioLaboral(models.Model):
    empleado = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="horario_laboral",
    )

    lunes_entrada = models.TimeField(default="07:00")
    lunes_salida = models.TimeField(default="16:00")

    martes_entrada = models.TimeField(default="07:00")
    martes_salida = models.TimeField(default="16:00")

    miercoles_entrada = models.TimeField(default="07:00")
    miercoles_salida = models.TimeField(default="16:00")

    jueves_entrada = models.TimeField(default="07:00")
    jueves_salida = models.TimeField(default="16:00")

    viernes_entrada = models.TimeField(default="07:00")
    viernes_salida = models.TimeField(default="16:00")

    sabado_entrada = models.TimeField(default="07:00")
    sabado_salida = models.TimeField(default="12:00")

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
