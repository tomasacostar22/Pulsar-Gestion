import datetime

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AnonymousUser

from .models import HorarioLaboral
from .context_processors import permisos_administrativo

Usuario = get_user_model()


class HorarioLaboralModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.horario = HorarioLaboral.objects.create(empleado=self.user)

    def test_str(self):
        self.assertIn("juan", str(self.horario))

    def test_defaults_lunes_a_viernes(self):
        for dia in ["lunes", "martes", "miercoles", "jueves", "viernes"]:
            self.assertEqual(getattr(self.horario, f"{dia}_entrada"), datetime.time(7, 0))
            self.assertEqual(getattr(self.horario, f"{dia}_salida"), datetime.time(16, 0))

    def test_default_sabado(self):
        self.assertEqual(self.horario.sabado_entrada, datetime.time(7, 0))
        self.assertEqual(self.horario.sabado_salida, datetime.time(12, 0))

    def test_total_horas_semana_default(self):
        # Lunes a viernes: 5 * 9h = 45h, Sabado: 5h = 50h total
        self.assertEqual(self.horario.total_horas_semana, "50h")

    def test_total_horas_con_minutos(self):
        self.horario.lunes_salida = datetime.time(16, 30)
        self.horario.save()
        self.horario.refresh_from_db()
        self.assertEqual(self.horario.total_horas_semana, "50h 30m")

    def test_dias_devuelve_6_elementos(self):
        self.assertEqual(len(self.horario.dias), 6)

    def test_one_to_one_constraint(self):
        with self.assertRaises(Exception):
            HorarioLaboral.objects.create(empleado=self.user)


class HorariosViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.grupo = Group.objects.create(name="Gerencia")
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.user.groups.add(self.grupo)
        self.empleado = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="juan", password="pass123")
        self.url = reverse("administrativo:horarios")

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_sin_empleado(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "administrativo/horarios.html")

    def test_get_con_empleado_crea_horario(self):
        response = self.client.get(self.url + f"?empleado={self.empleado.id}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(HorarioLaboral.objects.filter(empleado=self.empleado).exists())

    def test_get_empleado_inexistente(self):
        response = self.client.get(self.url + "?empleado=9999")
        self.assertEqual(response.status_code, 200)

    def test_post_guarda_horario(self):
        HorarioLaboral.objects.create(empleado=self.empleado)
        response = self.client.post(self.url + f"?empleado={self.empleado.id}", {
            "lunes_entrada": "08:00", "lunes_salida": "17:00",
            "martes_entrada": "08:00", "martes_salida": "17:00",
            "miercoles_entrada": "08:00", "miercoles_salida": "17:00",
            "jueves_entrada": "08:00", "jueves_salida": "17:00",
            "viernes_entrada": "08:00", "viernes_salida": "17:00",
            "sabado_entrada": "08:00", "sabado_salida": "13:00",
        })
        self.assertEqual(response.status_code, 200)
        horario = HorarioLaboral.objects.get(empleado=self.empleado)
        self.assertEqual(horario.lunes_entrada, datetime.time(8, 0))

    def test_htmx_get_devuelve_parcial(self):
        response = self.client.get(
            self.url + f"?empleado={self.empleado.id}",
            HTTP_HX_REQUEST="true",
        )
        self.assertTemplateUsed(response, "administrativo/parciales/horario_form.html")


class GerenciaMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.grupo = Group.objects.create(name="Gerencia")
        self.gerente = Usuario.objects.create_user(username="gerente", email="gerente@test.com", password="pass123")
        self.gerente.groups.add(self.grupo)
        self.empleado = Usuario.objects.create_user(username="empleado", email="empleado@test.com", password="pass123")
        self.url = reverse("administrativo:horarios")

    def test_usuario_no_autenticado_redirige(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_usuario_sin_grupo_gerencia_403(self):
        self.client.login(username="empleado", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_usuario_gerencia_accede(self):
        self.client.login(username="gerente", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_middleware_no_afecta_otras_rutas(self):
        self.client.login(username="empleado", password="pass123")
        response = self.client.get(reverse("principal"))
        self.assertEqual(response.status_code, 200)


class ContextProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.grupo = Group.objects.create(name="Gerencia")
        self.gerente = Usuario.objects.create_user(username="gerente", email="gerente@test.com", password="pass123")
        self.gerente.groups.add(self.grupo)
        self.empleado = Usuario.objects.create_user(username="empleado", email="empleado@test.com", password="pass123")

    def test_gerente_es_gerencia_true(self):
        request = self.factory.get("/")
        request.user = self.gerente
        ctx = permisos_administrativo(request)
        self.assertTrue(ctx["es_gerencia"])

    def test_empleado_es_gerencia_false(self):
        request = self.factory.get("/")
        request.user = self.empleado
        ctx = permisos_administrativo(request)
        self.assertFalse(ctx["es_gerencia"])

    def test_anonimo_es_gerencia_false(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        ctx = permisos_administrativo(request)
        self.assertFalse(ctx["es_gerencia"])
