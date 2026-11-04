from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class UsuarioAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuarios = get_user_model().objects
        cls.admin = cls.usuarios.create_superuser("admin")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_administrador_cria_conta(self):
        senha = "senha-de-teste-123"

        resposta = self.client.post(
            reverse("admin:contas_usuario_add"),
            {"username": "autora", "usable_password": "true", "password1": senha, "password2": senha},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(self.usuarios.get(username="autora").check_password(senha))

    def test_administrador_desativa_conta(self):
        autor = self.usuarios.create_user("autora")
        agora = timezone.localtime()

        resposta = self.client.post(
            reverse("admin:contas_usuario_change", args=[autor.pk]),
            {
                "username": "autora",
                "date_joined_0": agora.strftime("%d/%m/%Y"),
                "date_joined_1": agora.strftime("%H:%M:%S"),
            },
        )

        self.assertEqual(resposta.status_code, 302)
        autor.refresh_from_db()
        self.assertFalse(autor.is_active)
