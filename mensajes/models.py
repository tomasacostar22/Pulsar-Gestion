from django.db import models
from django.conf import settings


class Mensaje(models.Model):
    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensajes_enviados",
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensajes_recibidos",
    )
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"{self.remitente} -> {self.destinatario}: {self.titulo}"
