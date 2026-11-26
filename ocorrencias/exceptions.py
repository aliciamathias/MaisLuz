class OcorrenciaErro(Exception):
    pass


class NumeroPosteInvalidoErro(OcorrenciaErro):
    pass


class DadosInsuficientesErro(OcorrenciaErro):
    pass


class OcorrenciaNaoEncontradaErro(OcorrenciaErro):
    pass


class OcorrenciaEmAndamentoErro(OcorrenciaErro):
    pass


class PermissaoOcorrenciaNegadaErro(OcorrenciaErro):
    pass
