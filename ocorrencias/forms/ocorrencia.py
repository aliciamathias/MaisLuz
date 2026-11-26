from django import forms
from ocorrencias.exceptions import NumeroPosteInvalidoErro
from ocorrencias.models import TipoDefeito


class RegistroOcorrenciaForm(forms.Form):
    numero_poste = forms.CharField(
        max_length=15,
        required=True,
        error_messages={"required": "Campos obrigatórios não preenchidos"},
    )
    logradouro = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "Campos obrigatórios não preenchidos"},
    )
    rua = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "Campos obrigatórios não preenchidos"},
    )
    bairro = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "Campos obrigatórios não preenchidos"},
    )
    ponto_referencia = forms.CharField(
        max_length=200,
        required=True,
        error_messages={"required": "Campos obrigatórios não preenchidos"},
    )
    tipo_problema = forms.ChoiceField(
        choices=[
            ("Poste Apagado", "Poste Apagado"),
            ("Luz Oscilando", "Luz Oscilando"),
            ("Estrutura Danificada", "Estrutura Danificada"),
            ("poste_apagado", "Poste Apagado"),
            ("luz_oscilando", "Luz Oscilando"),
            ("poste_danificado", "Estrutura Danificada"),
        ],
        required=True,
        error_messages={"required": "Campos obrigatórios não preenchidos"},
    )
    descricao = forms.CharField(max_length=300, required=False)
    foto = forms.FileField(required=False)

    def clean_numero_poste(self):
        poste = (self.cleaned_data.get("numero_poste") or "").strip()
        if len(poste) < 8 or len(poste) > 10:
            raise forms.ValidationError("Número de identificação do poste incorreta")
        return poste

    def clean_tipo_problema(self):
        valor = self.cleaned_data.get("tipo_problema")
        mapeamento = {
            "poste_apagado": TipoDefeito.POSTE_APAGADO,
            "luz_oscilando": TipoDefeito.LUZ_OSCILANDO,
            "poste_danificado": TipoDefeito.ESTRUTURA_DANIFICADA,
            "Poste Apagado": TipoDefeito.POSTE_APAGADO,
            "Luz Oscilando": TipoDefeito.LUZ_OSCILANDO,
            "Estrutura Danificada": TipoDefeito.ESTRUTURA_DANIFICADA,
        }
        return mapeamento.get(valor, TipoDefeito.POSTE_APAGADO)
