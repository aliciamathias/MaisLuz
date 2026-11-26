/**
 * viacep.js - Integração com a API oficial do ViaCEP para MaisLuz Maceió
 * 
 * Requisitos atendidos:
 * - RF001: Preenchimento automático de Logradouro e Bairro no cadastro do cidadão
 * - RF008: Atualização automática de Logradouro e Bairro na edição de perfil
 * - RNF02: Abrangência Geográfica - Validação estrita para município de Maceió/AL
 * - RNF07: Resiliência e Tolerância a Falhas - Timeout, tratamento de erros de rede e liberação de campos manuais
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.ViaCEP = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var MUNICIPIO_ALVO = 'maceió';
  var MUNICIPIO_ALVO_SEM_ACENTO = 'maceio';
  var UF_ALVO = 'AL';
  var TIMEOUT_PADRAO_MS = 7000;

  /**
   * Remove formatação deixando apenas números.
   * @param {string} valor 
   * @returns {string}
   */
  function limparCep(valor) {
    return (valor || '').replace(/\D/g, '');
  }

  /**
   * Formata número para máscara 00000-000.
   * @param {string} cepLimpo 
   * @returns {string}
   */
  function formatarCep(cepLimpo) {
    if (cepLimpo.length > 5) {
      return cepLimpo.substring(0, 5) + '-' + cepLimpo.substring(5, 8);
    }
    return cepLimpo;
  }

  /**
   * Inicializa o monitoramento e integração do CEP em um formulário.
   * 
   * @param {Object} opcoes
   * @param {string|HTMLInputElement} opcoes.cepInput - Input do CEP
   * @param {string|HTMLInputElement} [opcoes.logradouroInput] - Input de Logradouro
   * @param {string|HTMLInputElement} [opcoes.bairroInput] - Input de Bairro
   * @param {string|HTMLInputElement} [opcoes.ruaInput] - Input de Rua (específico para telas que separam tipo de logradouro e nome da rua)
   * @param {string|HTMLInputElement} [opcoes.numeroInput] - Input de Número (para foco após busca)
   * @param {string|HTMLButtonElement} [opcoes.btnBuscar] - Botão acionador de busca
   * @param {string|HTMLElement} [opcoes.feedbackEl] - Elemento de feedback textual / acessibilidade
   * @param {number} [opcoes.timeoutMs=7000] - Tempo limite em milissegundos
   * @param {Function} [opcoes.onSuccess] - Callback opcional após preenchimento com sucesso
   * @param {Function} [opcoes.onError] - Callback opcional em caso de erro
   */
  function inicializar(opcoes) {
    opcoes = opcoes || {};

    var cepInput = typeof opcoes.cepInput === 'string'
      ? document.getElementById(opcoes.cepInput)
      : opcoes.cepInput;

    if (!cepInput) {
      return null;
    }

    var logradouroInput = typeof opcoes.logradouroInput === 'string'
      ? document.getElementById(opcoes.logradouroInput)
      : opcoes.logradouroInput;

    var bairroInput = typeof opcoes.bairroInput === 'string'
      ? document.getElementById(opcoes.bairroInput)
      : opcoes.bairroInput;

    var ruaInput = typeof opcoes.ruaInput === 'string'
      ? document.getElementById(opcoes.ruaInput)
      : opcoes.ruaInput;

    var numeroInput = typeof opcoes.numeroInput === 'string'
      ? document.getElementById(opcoes.numeroInput)
      : opcoes.numeroInput;

    var btnBuscar = typeof opcoes.btnBuscar === 'string'
      ? document.getElementById(opcoes.btnBuscar)
      : opcoes.btnBuscar;

    var feedbackEl = typeof opcoes.feedbackEl === 'string'
      ? document.getElementById(opcoes.feedbackEl)
      : opcoes.feedbackEl;

    var timeoutMs = opcoes.timeoutMs || TIMEOUT_PADRAO_MS;
    var ultimoCepBuscado = '';
    var emRequisicao = false;

    // Garante atributos de acessibilidade no feedback
    if (feedbackEl) {
      feedbackEl.setAttribute('aria-live', 'polite');
      feedbackEl.setAttribute('role', 'status');
    }

    function definirMensagem(tipo, texto) {
      if (!feedbackEl) return;
      feedbackEl.textContent = texto;
      feedbackEl.className = 'cep-dica';
      if (tipo === 'sucesso') {
        feedbackEl.classList.add('cep-feedback--sucesso');
      } else if (tipo === 'aviso') {
        feedbackEl.classList.add('cep-feedback--aviso');
      } else if (tipo === 'erro') {
        feedbackEl.classList.add('cep-feedback--erro');
      } else if (tipo === 'carregando') {
        feedbackEl.classList.add('cep-feedback--carregando');
      }
    }

    function setErroCampo(temErro) {
      if (!cepInput) return;
      if (temErro) {
        cepInput.classList.add('campo-input--erro');
        cepInput.setAttribute('aria-invalid', 'true');
      } else {
        cepInput.classList.remove('campo-input--erro');
        cepInput.removeAttribute('aria-invalid');
      }
    }

    function liberarCamposParaDigitacaoManual() {
      // RNF07: Garante que todos os campos permaneçam desbloqueados para preenchimento manual
      var campos = [logradouroInput, bairroInput, ruaInput, numeroInput];
      campos.forEach(function (campo) {
        if (campo) {
          campo.readOnly = false;
          campo.disabled = false;
        }
      });
      if (btnBuscar) {
        btnBuscar.disabled = false;
      }
    }

    function separarTipoENomeLogradouro(logradouroCompleto) {
      if (!logradouroCompleto) return { tipo: '', nome: '' };
      var tiposConhecidos = [
        'Avenida', 'Av.', 'Rua', 'R.', 'Travessa', 'Tv.', 'Alameda', 'Al.',
        'Praça', 'Pça.', 'Rodovia', 'Rod.', 'Estrada', 'Largo', 'Beco', 'Viaduto'
      ];
      var partes = logradouroCompleto.trim().split(/\s+/);
      if (partes.length > 1) {
        var primeira = partes[0];
        for (var i = 0; i < tiposConhecidos.length; i++) {
          if (tiposConhecidos[i].toLowerCase() === primeira.toLowerCase()) {
            return {
              tipo: primeira,
              nome: partes.slice(1).join(' ')
            };
          }
        }
      }
      return {
        tipo: 'Rua',
        nome: logradouroCompleto.trim()
      };
    }

    function preencherEndereco(dados) {
      var logradouroTexto = (dados.logradouro || '').trim();
      var bairroTexto = (dados.bairro || '').trim();

      if (ruaInput && logradouroInput) {
        // Cenário onde existem campos separados para tipo e rua (ex: registrar ocorrência)
        if (logradouroTexto) {
          var separacao = separarTipoENomeLogradouro(logradouroTexto);
          logradouroInput.value = separacao.tipo || 'Rua';
          ruaInput.value = separacao.nome || logradouroTexto;
        }
      } else {
        // Cenário padrão (cadastro do cidadão e perfil)
        if (logradouroInput && logradouroTexto) {
          logradouroInput.value = logradouroTexto;
        }
      }

      if (bairroInput && bairroTexto) {
        bairroInput.value = bairroTexto;
      }

      // Foca no próximo campo de interesse (número ou logradouro)
      if (numeroInput && !numeroInput.value) {
        numeroInput.focus();
      } else if (logradouroInput && !logradouroTexto) {
        logradouroInput.focus();
      }
    }

    function buscarCep(cepLimpo, disparadoPorAcaoExplicita) {
      if (emRequisicao) return;
      if (!cepLimpo || cepLimpo.length !== 8) {
        if (disparadoPorAcaoExplicita) {
          setErroCampo(true);
          definirMensagem('aviso', 'Por favor, informe um CEP válido com 8 dígitos.');
          cepInput.focus();
        }
        return;
      }

      // Se já consultou este mesmo CEP com sucesso, evita requisição duplicada
      if (cepLimpo === ultimoCepBuscado && !disparadoPorAcaoExplicita) {
        return;
      }

      emRequisicao = true;
      definirMensagem('carregando', 'Buscando endereço no ViaCEP...');
      if (btnBuscar) {
        btnBuscar.disabled = true;
      }

      // Configura AbortController para timeout (RNF07)
      var controller = null;
      var timeoutId = null;
      if (typeof AbortController !== 'undefined') {
        controller = new AbortController();
        timeoutId = setTimeout(function () {
          controller.abort();
        }, timeoutMs);
      }

      var url = 'https://viacep.com.br/ws/' + encodeURIComponent(cepLimpo) + '/json/';
      var fetchOptions = controller ? { signal: controller.signal } : {};

      fetch(url, fetchOptions)
        .then(function (resposta) {
          if (timeoutId) clearTimeout(timeoutId);
          if (!resposta.ok) {
            throw new Error('Falha na resposta do serviço ViaCEP (Status ' + resposta.status + ')');
          }
          return resposta.json();
        })
        .then(function (dados) {
          emRequisicao = false;
          liberarCamposParaDigitacaoManual();

          // Caso de CEP inexistente na base dos Correios
          if (dados.erro === true || dados.erro === 'true') {
            setErroCampo(true);
            definirMensagem(
              'aviso',
              'CEP não encontrado. Por favor, preencha o logradouro e o bairro manualmente.'
            );
            if (opcoes.onError) opcoes.onError({ tipo: 'nao_encontrado', cep: cepLimpo });
            return;
          }

          // Validação RNF02: Abrangência Geográfica - Maceió/AL
          var localidade = (dados.localidade || '').trim().toLowerCase();
          var uf = (dados.uf || '').trim().toUpperCase();
          var ehMaceio = (localidade === MUNICIPIO_ALVO || localidade === MUNICIPIO_ALVO_SEM_ACENTO) && uf === UF_ALVO;

          if (!ehMaceio) {
            setErroCampo(true);
            var cidadeExibicao = (dados.localidade || 'outro município') + '/' + (dados.uf || 'UF');
            definirMensagem(
              'aviso',
              'O MaisLuz atende exclusivamente o município de Maceió/AL. O CEP informado pertence a ' + cidadeExibicao + '.'
            );
            if (opcoes.onError) {
              opcoes.onError({
                tipo: 'municipio_invalido',
                cep: cepLimpo,
                localidade: dados.localidade,
                uf: dados.uf
              });
            }
            return;
          }

          // Sucesso: CEP válido em Maceió/AL
          ultimoCepBuscado = cepLimpo;
          setErroCampo(false);
          preencherEndereco(dados);

          var textoSucesso = 'Endereço localizado: ' + (dados.bairro ? dados.bairro + ', ' : '') + 'Maceió/AL.';
          definirMensagem('sucesso', textoSucesso);

          if (opcoes.onSuccess) {
            opcoes.onSuccess(dados);
          }
        })
        .catch(function (erro) {
          if (timeoutId) clearTimeout(timeoutId);
          emRequisicao = false;
          liberarCamposParaDigitacaoManual();

          // RNF07: Resiliência em caso de falha de rede ou timeout
          var mensagemErro = 'Não foi possível consultar o CEP automaticamente. Por favor, preencha o endereço manualmente.';
          if (erro && erro.name === 'AbortError') {
            mensagemErro = 'A consulta ao CEP demorou muito para responder (tempo limite excedido). Por favor, preencha o endereço manualmente.';
          }

          setErroCampo(false);
          definirMensagem('aviso', mensagemErro);

          if (opcoes.onError) {
            opcoes.onError({ tipo: 'erro_rede', erro: erro });
          }
        });
    }

    // Evento de digitação: dispara automaticamente ao atingir 8 dígitos
    cepInput.addEventListener('input', function () {
      var cepLimpo = limparCep(this.value);
      if (this.value.length > 5 && this.value.indexOf('-') === -1 && cepLimpo.length <= 8) {
        this.value = formatarCep(cepLimpo);
      }
      if (cepLimpo.length === 8) {
        buscarCep(cepLimpo, false);
      } else if (cepLimpo.length > 8) {
        setErroCampo(true);
      } else {
        setErroCampo(false);
      }
    });

    // Evento blur: valida se 8 dígitos foram digitados
    cepInput.addEventListener('blur', function () {
      var cepLimpo = limparCep(this.value);
      if (cepLimpo.length === 8) {
        buscarCep(cepLimpo, false);
      }
    });

    // Evento de clique no botão de busca explícito
    if (btnBuscar) {
      btnBuscar.addEventListener('click', function (e) {
        e.preventDefault();
        var cepLimpo = limparCep(cepInput.value);
        buscarCep(cepLimpo, true);
      });
    }

    return {
      buscar: function (cepManual) {
        var cep = limparCep(cepManual || cepInput.value);
        buscarCep(cep, true);
      },
      limpar: function () {
        ultimoCepBuscado = '';
        definirMensagem('padrao', '');
        setErroCampo(false);
        liberarCamposParaDigitacaoManual();
      }
    };
  }

  return {
    limparCep: limparCep,
    formatarCep: formatarCep,
    inicializar: inicializar
  };
}));
