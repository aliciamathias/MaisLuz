class ContasErro(Exception):
    pass


class CPFInvalidoErro(ContasErro):
    pass


class CPFCadastradoErro(ContasErro):
    pass


class NomeCurtoErro(ContasErro):
    pass


class TelefoneInvalidoErro(ContasErro):
    pass


class EmailInvalidoErro(ContasErro):
    pass


class EmailCadastradoErro(ContasErro):
    pass


class SenhaCurtaErro(ContasErro):
    pass


class SenhaLongaErro(ContasErro):
    pass


class SenhasDiferentesErro(ContasErro):
    pass


class CEPCurtoErro(ContasErro):
    pass


class CEPLongoErro(ContasErro):
    pass


class CEPInvalidoErro(ContasErro):
    pass


class CampoObrigatorioErro(ContasErro):
    pass


class CampoImutavelErro(ContasErro):
    pass


class CredenciaisInvalidasErro(ContasErro):
    pass


class CredenciaisRecuperacaoInvalidasErro(ContasErro):
    pass


class UsuarioNaoEncontradoErro(ContasErro):
    pass


class PermissaoNegadaErro(ContasErro):
    pass


class JustificativaObrigatoriaErro(ContasErro):
    pass


class UsuarioBloqueadoErro(ContasErro):
    pass


class UsuarioInativoErro(ContasErro):
    pass
