from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    def test_str_devuelve_email(self):
        user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.assertEqual(str(user), "juan@test.com")


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("usuarios:login")
        self.user = Usuario.objects.create_user(
            username="juan", email="juan@test.com", password="pass123"
        )

    def test_get_muestra_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/login.html")

    def test_login_exitoso_redirige_a_principal(self):
        response = self.client.post(self.url, {"email": "juan@test.com", "password": "pass123"})
        self.assertRedirects(response, reverse("principal"))

    def test_login_fallido_muestra_error(self):
        response = self.client.post(self.url, {"email": "juan@test.com", "password": "mala"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Correo o contrasena incorrectos")

    def test_login_email_inexistente(self):
        response = self.client.post(self.url, {"email": "nadie@test.com", "password": "pass123"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Correo o contrasena incorrectos")

    def test_usuario_autenticado_redirige_a_principal(self):
        self.client.login(username="juan", password="pass123")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("principal"))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.client = Client()
        self.client.login(username="juan", password="pass123")

    def test_logout_redirige_a_login(self):
        response = self.client.get(reverse("usuarios:logout"))
        self.assertRedirects(response, reverse("usuarios:login"))


class CambiarContrasenaViewTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="juan", email="juan@test.com", password="pass123")
        self.client = Client()
        self.client.login(username="juan", password="pass123")
        self.url = reverse("usuarios:cambiar_contrasena")

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_muestra_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/cambiar_contrasena.html")

    def test_cambio_exitoso(self):
        response = self.client.post(self.url, {
            "actual": "pass123",
            "nueva": "nuevapass",
            "confirmar": "nuevapass",
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("nuevapass"))

    def test_contrasena_actual_incorrecta(self):
        response = self.client.post(self.url, {
            "actual": "mala",
            "nueva": "nuevapass",
            "confirmar": "nuevapass",
        })
        self.assertContains(response, "La contrasena actual es incorrecta")

    def test_contrasena_muy_corta(self):
        response = self.client.post(self.url, {
            "actual": "pass123",
            "nueva": "abc",
            "confirmar": "abc",
        })
        self.assertContains(response, "al menos 6 caracteres")

    def test_contrasenas_no_coinciden(self):
        response = self.client.post(self.url, {
            "actual": "pass123",
            "nueva": "nuevapass",
            "confirmar": "otrapass",
        })
        self.assertContains(response, "no coinciden")
