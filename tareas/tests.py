from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Tarea, Anuncio

Usuario = get_user_model()


class TareaModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.tarea = Tarea.objects.create(
            nombre="Tarea test",
            fecha_limite=timezone.now() + timezone.timedelta(days=1),
            responsable=self.user,
            supervisor=self.user,
        )

    def test_str(self):
        self.assertEqual(str(self.tarea), "Tarea test")

    def test_estado_default_pendiente(self):
        self.assertEqual(self.tarea.estado, "PENDIENTE")

    def test_prioridad_default_media(self):
        self.assertEqual(self.tarea.prioridad, "MEDIA")


class AnuncioModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.anuncio = Anuncio.objects.create(autor=self.user, titulo="Test", contenido="Contenido de prueba")

    def test_str(self):
        self.assertIn("juan@test.com", str(self.anuncio))

    def test_ordering_por_fecha_desc(self):
        anuncio2 = Anuncio.objects.create(autor=self.user, titulo="Test2", contenido="Otro contenido")
        anuncios = list(Anuncio.objects.all())
        self.assertEqual(anuncios[0], anuncio2)


class PrincipalViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.otro = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.url = reverse("principal")
        self.tarea = Tarea.objects.create(
            nombre="Mi tarea",
            fecha_limite=timezone.now() + timezone.timedelta(days=1),
            responsable=self.user,
            supervisor=self.otro,
        )

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_vista_realizar_por_defecto(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi tarea")

    def test_vista_supervisar(self):
        tarea_sup = Tarea.objects.create(
            nombre="Tarea supervisada",
            fecha_limite=timezone.now() + timezone.timedelta(days=1),
            responsable=self.otro,
            supervisor=self.user,
        )
        response = self.client.get(self.url + "?vista=supervisar")
        self.assertContains(response, "Tarea supervisada")

    def test_filtro_estado_finalizada(self):
        self.tarea.estado = "FINALIZADA"
        self.tarea.save()
        response = self.client.get(self.url + "?estado=FINALIZADA")
        self.assertContains(response, "Mi tarea")

    def test_htmx_devuelve_parcial(self):
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "tareas/parciales/lista_tareas.html")


class CrearAnuncioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.url = reverse("crear_anuncio")

    def test_crear_anuncio_post(self):
        response = self.client.post(self.url, {"titulo": "Titulo", "contenido": "Contenido"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Anuncio.objects.count(), 1)
        self.assertEqual(Anuncio.objects.first().titulo, "Titulo")

    def test_no_crea_anuncio_vacio(self):
        self.client.post(self.url, {"titulo": "", "contenido": ""}, HTTP_HX_REQUEST="true")
        self.assertEqual(Anuncio.objects.count(), 0)


class EliminarAnuncioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.otro = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.anuncio = Anuncio.objects.create(autor=self.user, titulo="Test", contenido="Contenido")

    def test_eliminar_propio_anuncio(self):
        url = reverse("eliminar_anuncio", args=[self.anuncio.id])
        self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(Anuncio.objects.count(), 0)

    def test_no_puede_eliminar_anuncio_ajeno(self):
        self.client.logout()
        self.client.login(username="pedro", password="pass123")
        url = reverse("eliminar_anuncio", args=[self.anuncio.id])
        self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(Anuncio.objects.count(), 1)


class CrearTareaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.otro = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.url = reverse("crear_tarea")

    def test_get_muestra_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tareas/crear.html")

    def test_crear_tarea_exitoso(self):
        response = self.client.post(self.url, {
            "nombre": "Nueva tarea",
            "descripcion": "Descripcion",
            "fecha_limite": "2026-12-31 23:59",
            "prioridad": "ALTA",
            "responsable": self.otro.id,
        })
        self.assertRedirects(response, "/tareas/?vista=supervisar")
        self.assertEqual(Tarea.objects.count(), 1)
        tarea = Tarea.objects.first()
        self.assertEqual(tarea.supervisor, self.user)
        self.assertEqual(tarea.responsable, self.otro)

    def test_crear_tarea_campos_faltantes(self):
        response = self.client.post(self.url, {"nombre": "", "fecha_limite": "", "responsable": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Todos los campos obligatorios")
        self.assertEqual(Tarea.objects.count(), 0)


class FinalizarTareaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.otro = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.tarea = Tarea.objects.create(
            nombre="Tarea",
            fecha_limite=timezone.now() + timezone.timedelta(days=1),
            responsable=self.user,
            supervisor=self.otro,
        )

    def test_finalizar_tarea_propia(self):
        url = reverse("finalizar_tarea", args=[self.tarea.id])
        self.client.post(url, HTTP_HX_REQUEST="true")
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.estado, "FINALIZADA")

    def test_no_puede_finalizar_tarea_ajena(self):
        self.client.logout()
        self.client.login(username="pedro", password="pass123")
        url = reverse("finalizar_tarea", args=[self.tarea.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.estado, "PENDIENTE")

    def test_finalizar_tarea_inexistente(self):
        url = reverse("finalizar_tarea", args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
