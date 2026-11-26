# Estado atual

Atualizado em: 2026-11-25

Este arquivo guarda apenas o que não está em outro lugar. Mantenha-o com cerca de 30 linhas e retire o que estiver resolvido. O status de cada documento fica no próprio documento, e o histórico fica no Git.

## Em andamento

Nada.

## Concluído recentemente

- Integração nativa da API ViaCEP em JavaScript puro (`static/js/viacep.js`) com `fetch`, sem bibliotecas externas:
  - Disparo automático ao atingir 8 dígitos válidos, no evento `blur` ou no clique do botão `Buscar CEP`.
  - Preenchimento dinâmico de Logradouro e Bairro no Cadastro do Cidadão (RF001), Edição de Perfil (RF008) e Registro de Ocorrência.
  - Validação de abrangência geográfica para Maceió/AL (RNF02), exibindo aviso e bloqueando autopreenchimento de outros municípios.
  - Tolerância a falhas e resiliência com timeout (7s via `AbortController`), tratamento de erro de rede ou CEP não encontrado, liberando os campos para digitação manual (RNF07).
  - Feedback visual e acessível com `aria-live="polite"` e estilos no padrão WCAG AA.
- Implementação e proteção das rotas do Cidadão (`registrar_ocorrencia`, `minhas_ocorrencias`, `meu_perfil_cidadao`) com `LoginRequiredMixin`.
- Suíte completa de 65 testes automatizados executando com 100% de aprovação (OK).

## Próximos passos

- Integrar fluxo administrativo e de atendentes (painel corporativo de ocorrências e gestão de operadores).

## Pendências

- Antes de um deploy real (revisão OWASP de 2026-11-04):
  - Limitar tentativas de login e envios de formulário.
  - Tirar `DEBUG = True` do código, preencher `ALLOWED_HOSTS` e resolver os avisos de `check --deploy`.
  - Registrar falhas de login e acessos negados com `LOGGING`.
- Melhoria menor de segurança: adicionar CSP.
