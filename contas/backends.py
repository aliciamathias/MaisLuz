from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class CPFEmailBackend(ModelBackend):
    """Permite autenticação por CPF, E-mail, Matrícula Funcional ou Username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or not password:
            return None

        termo = username.strip()
        usuario = UserModel.objects.filter(
            Q(username__iexact=termo)
            | Q(email__iexact=termo)
            | Q(cpf__iexact=termo)
            | Q(matricula_funcional__iexact=termo)
        ).first()

        if usuario and usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
