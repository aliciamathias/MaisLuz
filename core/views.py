from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from contas.exceptions import (
    CPFCadastradoErro,
    EmailCadastradoErro,
)
from contas.forms import CadastroCidadaoForm, EdicaoPerfilCidadaoForm
from contas.services import CidadaoService
from ocorrencias.exceptions import (
    DadosInsuficientesErro,
    NumeroPosteInvalidoErro,
    OcorrenciaEmAndamentoErro,
    PermissaoOcorrenciaNegadaErro,
)
from ocorrencias.forms import RegistroOcorrenciaForm
from ocorrencias.models import Ocorrencia, StatusOcorrencia
from ocorrencias.services import OcorrenciaService


class LandingPageView(View):
    """Exibe a landing page / home pública do MaisLuz."""

    def get(self, request):
        contexto = {
            "header_variante": "landing",
        }
        return render(request, "paginas/landing-page.html", contexto)


class PainelOcorrenciasView(View):
    """Exibe o painel corporativo de ocorrências (Atendente e Administrador)."""

    def get(self, request):
        is_admin = (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_staff)
        )
        contexto = {
            "nav_ativa": "ocorrencias",
            "is_admin": is_admin,
            "perfil": "administrador" if is_admin else "atendente",
        }
        return render(request, "ocorrencias/ocorrencias-atendente.html", contexto)


class CadastroAtendenteView(View):
    """Exibe o formulário de cadastro e listagem de atendentes (Administrador)."""

    def get(self, request):
        contexto = {
            "nav_ativa": "funcionarios",
            "subnav_ativa": "listagem",
            "is_admin": True,
            "perfil": "administrador",
        }
        return render(request, "funcionarios/cadastro-atendente.html", contexto)


class EditarAtendenteView(View):
    """Exibe o formulário de edição de atendente (Administrador)."""

    def get(self, request):
        contexto = {
            "nav_ativa": "funcionarios",
            "subnav_ativa": "listagem",
            "is_admin": True,
            "perfil": "administrador",
        }
        return render(request, "funcionarios/editar-atendente.html", contexto)


class MeuPerfilInternoView(View):
    """Exibe o perfil do operador logado (Atendente e Administrador)."""

    def get(self, request):
        is_admin = (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_staff)
        )
        contexto = {
            "nav_ativa": "perfil",
            "is_admin": is_admin,
            "perfil": "administrador" if is_admin else "atendente",
        }
        return render(request, "funcionarios/meu-perfil-interno.html", contexto)


class RegistrarOcorrenciaView(LoginRequiredMixin, View):
    """Exibe o fluxo e processa o registro de nova ocorrência (Cidadão)."""

    login_url = "contas:entrar"

    def get(self, request):
        contexto = {
            "form": RegistroOcorrenciaForm(),
        }
        return render(request, "ocorrencias/registrar-ocorrencia-cidadao.html", contexto)

    def post(self, request):
        form = RegistroOcorrenciaForm(request.POST, request.FILES)
        if not form.is_valid():
            erros = form.errors
            tem_obrigatorio = any(
                "Campos obrigatórios não preenchidos" in str(err)
                for err in erros.values()
            )
            mensagem_topo = (
                "Campos obrigatórios não preenchidos"
                if tem_obrigatorio
                else "Não foi dada informações o suficiente"
            )
            contexto = {
                "form": form,
                "erro_geral": mensagem_topo,
            }
            return render(request, "ocorrencias/registrar-ocorrencia-cidadao.html", contexto)

        dados = form.cleaned_data
        try:
            OcorrenciaService.criar_ocorrencia(
                cidadao=request.user,
                numero_poste=dados["numero_poste"],
                logradouro=dados["logradouro"],
                rua=dados["rua"],
                bairro=dados["bairro"],
                ponto_referencia=dados["ponto_referencia"],
                tipo_defeito=dados["tipo_problema"],
                descricao=dados.get("descricao", ""),
                foto=dados.get("foto"),
            )
        except (NumeroPosteInvalidoErro, DadosInsuficientesErro, PermissaoOcorrenciaNegadaErro) as e:
            contexto = {
                "form": form,
                "erro_geral": str(e),
            }
            return render(request, "ocorrencias/registrar-ocorrencia-cidadao.html", contexto)

        messages.success(
            request,
            "Ocorrência registrada com sucesso! O chamado foi encaminhado para a empresa de energia.",
        )
        return redirect("minhas_ocorrencias")


class MinhasOcorrenciasView(LoginRequiredMixin, View):
    """Exibe as ocorrências do cidadão logado e permite exclusão lógica."""

    login_url = "contas:entrar"

    def get(self, request):
        ocorrencias = OcorrenciaService.listar_para_cidadao(request.user)
        total = ocorrencias.count()
        em_andamento = ocorrencias.filter(
            status__in=[StatusOcorrencia.PENDENTE, StatusOcorrencia.EM_PROGRESSO]
        ).count()
        concluidas = ocorrencias.filter(status=StatusOcorrencia.CONCLUIDO).count()

        contexto = {
            "ocorrencias": ocorrencias,
            "total_ocorrencias": total,
            "total_andamento": em_andamento,
            "total_concluidas": concluidas,
        }
        return render(request, "ocorrencias/minhas-ocorrencias-cidadao.html", contexto)

    def post(self, request):
        protocolo = request.POST.get("protocolo")
        ocorrencia = get_object_or_404(
            Ocorrencia, protocolo=protocolo, cidadao=request.user
        )
        try:
            OcorrenciaService.excluir_logica_cidadao(ocorrencia, request.user)
            messages.success(request, "Ocorrência excluída com sucesso.")
        except OcorrenciaEmAndamentoErro as e:
            messages.error(request, str(e))
        except PermissaoOcorrenciaNegadaErro as e:
            messages.error(request, str(e))

        return redirect("minhas_ocorrencias")


class MeuPerfilCidadaoView(LoginRequiredMixin, View):
    """Exibe o perfil e processa a edição de dados cadastrais do cidadão."""

    login_url = "contas:entrar"

    def get(self, request):
        form = EdicaoPerfilCidadaoForm(
            initial={
                "nome": request.user.nome_completo or request.user.get_full_name(),
                "email": request.user.email,
                "celular": request.user.telefone,
                "cep": request.user.cep,
                "logradouro": request.user.logradouro,
                "bairro": request.user.bairro,
                "numero": request.user.numero,
                "complemento": request.user.complemento,
            }
        )
        contexto = {
            "form": form,
            "usuario": request.user,
        }
        return render(request, "cidadao/meu-perfil-cidadao.html", contexto)

    def post(self, request):
        form = EdicaoPerfilCidadaoForm(request.POST)
        if not form.is_valid():
            contexto = {
                "form": form,
                "usuario": request.user,
                "erro_geral": "Campo(s) obrigatório(s) não preenchido(s)"
                if form.errors
                else "Campo preenchido incorretamente",
            }
            return render(request, "cidadao/meu-perfil-cidadao.html", contexto)

        dados = form.cleaned_data
        try:
            CidadaoService.editar_perfil(
                usuario=request.user,
                operador=request.user,
                nome_completo=dados["nome"],
                email=dados["email"],
                telefone=dados["celular"],
                cep=dados.get("cep"),
                logradouro=dados.get("logradouro"),
                bairro=dados.get("bairro"),
                numero=dados.get("numero"),
                complemento=dados.get("complemento"),
                nova_senha=dados.get("nova_senha") or None,
                confirmacao_nova_senha=dados.get("confirmacao_nova_senha") or None,
            )
            messages.success(request, "Dados atualizados com sucesso")
            return redirect("meu_perfil_cidadao")
        except EmailCadastradoErro:
            form.add_error("email", "E-mail já cadastrado")
            contexto = {
                "form": form,
                "usuario": request.user,
                "erro_geral": "E-mail já cadastrado",
            }
            return render(request, "cidadao/meu-perfil-cidadao.html", contexto)


class CadastroCidadaoView(View):
    """Exibe o formulário de cadastro de novo cidadão e processa a criação."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("minhas_ocorrencias")

        contexto = {
            "form": CadastroCidadaoForm(),
            "header_variante": "cadastro",
        }
        return render(request, "cidadao/cadastro-cidadao.html", contexto)

    def post(self, request):
        form = CadastroCidadaoForm(request.POST)
        if not form.is_valid():
            tem_obrigatorio = any(
                "Campo(s) obrigatório(s) não preenchido(s)" in str(e)
                for e in form.errors.values()
            )
            contexto = {
                "form": form,
                "erro_geral": "Campo(s) obrigatório(s) não preenchido(s)"
                if tem_obrigatorio
                else "Campo preenchido incorretamente",
                "header_variante": "cadastro",
            }
            return render(request, "cidadao/cadastro-cidadao.html", contexto)

        dados = form.cleaned_data
        try:
            CidadaoService.cadastrar(
                nome_completo=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
                telefone=dados["celular"],
                senha=dados["senha"],
                confirmacao_senha=dados["confirmacao_senha"],
                cep=dados["cep"],
                logradouro=dados["logradouro"],
                bairro=dados["bairro"],
                numero=dados["numero"],
                complemento=dados.get("complemento", ""),
            )
        except CPFCadastradoErro:
            form.add_error("cpf", "CPF já cadastrado")
            return render(
                request,
                "cidadao/cadastro-cidadao.html",
                {"form": form, "erro_geral": "Campo preenchido incorretamente", "header_variante": "cadastro"},
            )
        except EmailCadastradoErro:
            form.add_error("email", "E-mail já cadastrado")
            return render(
                request,
                "cidadao/cadastro-cidadao.html",
                {"form": form, "erro_geral": "Campo preenchido incorretamente", "header_variante": "cadastro"},
            )

        return redirect("cadastro_sucesso")


class CadastroSucessoView(View):
    """Página de confirmação com 'Cadastro realizado com sucesso' no centro."""

    def get(self, request):
        return render(request, "cidadao/cadastro-sucesso.html", {"header_variante": "cadastro"})


class RecuperarSenhaCidadaoView(View):
    """Exibe a recuperação de senha do cidadão."""

    def get(self, request):
        contexto = {
            "header_variante": "recuperar_senha",
        }
        return render(request, "contas/recuperar-senha-cidadao.html", contexto)


class RecuperarSenhaAtendenteView(View):
    """Exibe a solicitação de recuperação de senha do atendente."""

    def get(self, request):
        contexto = {
            "header_variante": "recuperar_senha",
        }
        return render(request, "contas/recuperar-senha-atendente.html", contexto)
