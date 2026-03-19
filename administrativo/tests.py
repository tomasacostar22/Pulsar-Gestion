import datetime

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AnonymousUser

from django.utils import timezone

from .models import HorarioLaboral
from .context_processors import permisos_administrativo
from tareas.models import Tarea

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

    def test_dias_incluye_segundo_bloque(self):
        for dia in self.horario.dias:
            self.assertEqual(len(dia), 5)  # nombre, entrada, salida, entrada_2, salida_2

    def test_segundo_bloque_nulo_por_defecto(self):
        for dia in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]:
            self.assertIsNone(getattr(self.horario, f"{dia}_entrada_2"))
            self.assertIsNone(getattr(self.horario, f"{dia}_salida_2"))

    def test_total_horas_con_segundo_bloque(self):
        # Lunes: bloque1 07:00-12:00 (5h) + bloque2 13:00-16:00 (3h) = 8h
        # Resto igual que default: martes-viernes 9h c/u = 36h, sabado 5h
        # Total = 8 + 36 + 5 = 49h
        self.horario.lunes_salida = datetime.time(12, 0)
        self.horario.lunes_entrada_2 = datetime.time(13, 0)
        self.horario.lunes_salida_2 = datetime.time(16, 0)
        self.horario.save()
        self.horario.refresh_from_db()
        self.assertEqual(self.horario.total_horas_semana, "49h")

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

    def test_post_guarda_segundo_bloque(self):
        HorarioLaboral.objects.create(empleado=self.empleado)
        response = self.client.post(self.url + f"?empleado={self.empleado.id}", {
            "lunes_entrada": "07:00", "lunes_salida": "12:00",
            "lunes_entrada_2": "13:00", "lunes_salida_2": "16:00",
            "martes_entrada": "08:00", "martes_salida": "17:00",
            "miercoles_entrada": "08:00", "miercoles_salida": "17:00",
            "jueves_entrada": "08:00", "jueves_salida": "17:00",
            "viernes_entrada": "08:00", "viernes_salida": "17:00",
            "sabado_entrada": "08:00", "sabado_salida": "13:00",
        })
        self.assertEqual(response.status_code, 200)
        horario = HorarioLaboral.objects.get(empleado=self.empleado)
        self.assertEqual(horario.lunes_entrada_2, datetime.time(13, 0))
        self.assertEqual(horario.lunes_salida_2, datetime.time(16, 0))

    def test_post_limpia_segundo_bloque_si_vacio(self):
        horario = HorarioLaboral.objects.create(empleado=self.empleado)
        horario.lunes_entrada_2 = datetime.time(13, 0)
        horario.lunes_salida_2 = datetime.time(16, 0)
        horario.save()
        self.client.post(self.url + f"?empleado={self.empleado.id}", {
            "lunes_entrada": "08:00", "lunes_salida": "17:00",
            "lunes_entrada_2": "", "lunes_salida_2": "",
            "martes_entrada": "08:00", "martes_salida": "17:00",
            "miercoles_entrada": "08:00", "miercoles_salida": "17:00",
            "jueves_entrada": "08:00", "jueves_salida": "17:00",
            "viernes_entrada": "08:00", "viernes_salida": "17:00",
            "sabado_entrada": "08:00", "sabado_salida": "13:00",
        })
        horario.refresh_from_db()
        self.assertIsNone(horario.lunes_entrada_2)
        self.assertIsNone(horario.lunes_salida_2)

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


class SupervisarTareasViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.grupo = Group.objects.create(name="Gerencia")
        self.gerente = Usuario.objects.create_user(username="gerente", email="gerente@test.com", password="pass123")
        self.gerente.groups.add(self.grupo)
        self.empleado = Usuario.objects.create_user(username="pedro", email="pedro@test.com", password="pass123")
        self.client.login(username="gerente", password="pass123")
        self.url = reverse("administrativo:supervisar_tareas")
        limite = timezone.now() + timezone.timedelta(days=7)
        self.tarea1 = Tarea.objects.create(
            nombre="Tarea alta", responsable=self.empleado, supervisor=self.gerente,
            prioridad="ALTA", estado="PENDIENTE", fecha_limite=limite,
        )
        self.tarea2 = Tarea.objects.create(
            nombre="Tarea finalizada", responsable=self.empleado, supervisor=self.gerente,
            prioridad="BAJA", estado="FINALIZADA", fecha_limite=limite,
        )

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_requiere_gerencia(self):
        self.client.login(username="pedro", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_muestra_todas_las_tareas(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tarea alta")
        self.assertContains(response, "Tarea finalizada")

    def test_filtro_estado(self):
        response = self.client.get(self.url + "?estado=PENDIENTE", HTTP_HX_REQUEST="true")
        self.assertContains(response, "Tarea alta")
        self.assertNotContains(response, "Tarea finalizada")

    def test_filtro_prioridad(self):
        response = self.client.get(self.url + "?prioridad=BAJA", HTTP_HX_REQUEST="true")
        self.assertNotContains(response, "Tarea alta")
        self.assertContains(response, "Tarea finalizada")

    def test_filtro_empleado(self):
        otro = Usuario.objects.create_user(username="otro", email="otro@test.com", password="pass123")
        limite = timezone.now() + timezone.timedelta(days=7)
        Tarea.objects.create(nombre="Tarea otro", responsable=otro, supervisor=self.gerente, fecha_limite=limite)
        response = self.client.get(self.url + f"?empleado={otro.id}", HTTP_HX_REQUEST="true")
        self.assertContains(response, "Tarea otro")
        self.assertNotContains(response, "Tarea alta")

    def test_htmx_devuelve_parcial(self):
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "administrativo/parciales/lista_tareas_admin.html")

    def test_get_normal_devuelve_pagina_completa(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "administrativo/supervisar_tareas.html")
