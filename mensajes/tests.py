from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Mensaje

Usuario = get_user_model()


class MensajeModelTest(TestCase):
    def setUp(self):
        self.user1 = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.user2 = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.mensaje = Mensaje.objects.create(
            remitente=self.user1, destinatario=self.user2, titulo="Hola", contenido="Texto"
        )

    def test_str(self):
        self.assertIn("Hola", str(self.mensaje))

    def test_ordering_por_fecha_desc(self):
        msg2 = Mensaje.objects.create(
            remitente=self.user1, destinatario=self.user2, titulo="Segundo", contenido="Texto2"
        )
        mensajes = list(Mensaje.objects.all())
        self.assertEqual(mensajes[0], msg2)


class BandejaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.user2 = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.url = reverse("mensajes:bandeja")
        Mensaje.objects.create(
            remitente=self.user2, destinatario=self.user1, titulo="Recibido", contenido="Texto"
        )
        Mensaje.objects.create(
            remitente=self.user1, destinatario=self.user2, titulo="Enviado", contenido="Texto"
        )

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_vista_recibidos_por_defecto(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recibido")

    def test_vista_enviados(self):
        response = self.client.get(self.url + "?vista=enviados")
        self.assertContains(response, "Enviado")

    def test_htmx_devuelve_parcial(self):
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "mensajes/parciales/lista_mensajes.html")


class EnviarMensajeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.user2 = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.url = reverse("mensajes:enviar_mensaje")

    def test_get_muestra_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "mensajes/enviar.html")

    def test_enviar_mensaje_exitoso(self):
        response = self.client.post(self.url, {
            "destinatario": self.user2.id,
            "titulo": "Asunto",
            "contenido": "Cuerpo del mensaje",
        })
        self.assertRedirects(response, reverse("mensajes:bandeja"))
        self.assertEqual(Mensaje.objects.count(), 1)
        msg = Mensaje.objects.first()
        self.assertEqual(msg.remitente, self.user1)
        self.assertEqual(msg.destinatario, self.user2)

    def test_enviar_mensaje_campos_vacios(self):
        response = self.client.post(self.url, {"destinatario": "", "titulo": "", "contenido": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Todos los campos son obligatorios")
        self.assertEqual(Mensaje.objects.count(), 0)
