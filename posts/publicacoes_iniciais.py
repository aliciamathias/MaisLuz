"""Textos das publicações iniciais do blog, da mais antiga para a mais recente."""

PUBLICACOES_INICIAIS: tuple[dict[str, str], ...] = (
    {
        "titulo": "O que um bom teste conta sobre o seu código",
        "conteudo": "\n\n".join(
            (
                "Costumamos pensar nos testes como uma rede de proteção: eles existem para "
                "avisar quando algo quebra. Essa função é importante, mas um bom teste faz "
                "outra coisa igualmente valiosa: ele descreve, em linguagem executável, o que "
                "o sistema promete fazer.",
                "Um nome como test_publicar_preenche_data_na_primeira_vez já é uma pequena "
                "especificação. Quem chega ao projeto meses depois lê essa linha e entende "
                "uma regra que talvez não esteja escrita em nenhum outro lugar.",
                "Os testes também são a primeira pessoa a usar o seu código. Quando preparar "
                "um cenário exige dez objetos e três simulações, o problema raramente está no "
                "teste. Normalmente é o código avisando que faz coisas demais ao mesmo tempo.",
                "Vale testar também os caminhos desagradáveis: o post que não existe, o "
                "usuário sem permissão, a página além do limite. É nesses cantos que os "
                "defeitos costumam se esconder, justamente porque ninguém passa por eles "
                "durante uma demonstração.",
            )
        ),
    },
    {
        "titulo": "Texto puro: quando menos formatação ajuda",
        "conteudo": "\n\n".join(
            (
                "Este blog não tem editor visual, Markdown nem envio de imagens. Cada "
                "publicação é apenas texto, dividido em parágrafos. À primeira vista parece "
                "uma limitação, e de fato é. Mas é uma limitação escolhida.",
                "Aceitar HTML de quem escreve abriria uma porta para ataques de script entre "
                "sites, e fechá-la exigiria sanitizar cada conteúdo com cuidado. Com texto "
                "puro, o próprio mecanismo de templates escapa tudo o que é exibido, e esse "
                "risco fica coberto sem nenhuma dependência adicional.",
                "Existe também um efeito sobre a escrita. Sem negrito para dar ênfase nem "
                "subtítulos para organizar, a frase precisa fazer o trabalho sozinha. A ordem "
                "das ideias passa a importar mais, e o parágrafo volta a ser a unidade "
                "principal do texto.",
                "Nada disso significa que a decisão seja definitiva. Se um dia o blog precisar "
                "de mais recursos, os textos já gravados continuam válidos. Começar pelo "
                "simples mantém essa opção aberta, sem pagar por ela antes da hora.",
            )
        ),
    },
    {
        "titulo": "Por que as regras de negócio moram nos services",
        "conteudo": "\n\n".join(
            (
                "O Django organiza uma aplicação em models, views e templates, e isso resolve "
                "boa parte do problema. Falta responder a uma pergunta: onde fica a regra que "
                "diz que um post só recebe a data de publicação na primeira vez em que é "
                "publicado?",
                "Se ela ficar na view, será preciso repeti-la no próximo ponto de entrada, "
                "seja um comando de terminal, uma ação do Admin ou uma futura API. Se ficar no "
                "model, ele logo acumula responsabilidades que não têm relação com a "
                "persistência dos dados.",
                "A camada de service dá um endereço a essas regras. A view lê a requisição, "
                "chama o service e devolve uma resposta. O service não conhece HTTP: recebe "
                "dados simples, aplica as regras e comunica falhas com exceções do domínio.",
                "O ganho aparece nos testes, que verificam as regras sem simular requisições, "
                "e na reutilização. As publicações que você está lendo, por exemplo, foram "
                "criadas por um comando que chama os mesmos services usados pelo painel dos "
                "autores.",
            )
        ),
    },
    {
        "titulo": "Rascunhos existem para serem ruins",
        "conteudo": "\n\n".join(
            (
                "Todo post neste blog nasce como rascunho. É uma regra técnica simples, mas "
                "ela carrega uma ideia útil para quem escreve: a primeira versão não precisa "
                "estar boa, porque ninguém vai lê-la.",
                "Boa parte do bloqueio diante da página em branco vem de tentar escrever e "
                "revisar ao mesmo tempo. A cada frase, o editor interno interrompe o autor, e "
                "o texto não avança. Separar as duas etapas costuma destravar a escrita.",
                "Depois que as ideias estão no papel, o trabalho muda de natureza. Agora "
                "existe algo concreto para cortar, reordenar e esclarecer. Ler o texto em voz "
                "alta ajuda a encontrar frases longas demais, e voltar a ele no dia seguinte "
                "revela o que parecia óbvio apenas para quem escreveu.",
                "Publicar também não precisa ser o fim. Um texto publicado pode ser corrigido, "
                "ou voltar a ser rascunho enquanto amadurece. O que importa é que a porta entre "
                "as duas etapas continue aberta.",
            )
        ),
    },
    {
        "titulo": "Boas-vindas ao blog",
        "conteudo": "\n\n".join(
            (
                "Este é um espaço para ler e escrever com calma. Aqui, cada pessoa autora "
                "publica os próprios textos, e quem visita pode ler e comentar sem precisar "
                "criar uma conta.",
                "As primeiras publicações falam sobre o que está por trás deste próprio blog: "
                "como o código foi organizado, por que os textos são tão simples e o que os "
                "testes têm a dizer sobre tudo isso. Há também uma conversa sobre o ato de "
                "escrever, que vale para qualquer assunto.",
                "Os comentários passam por moderação antes de aparecer na página. Por isso, "
                "não se preocupe se o seu não surgir de imediato: depois de aprovado, ele "
                "ficará visível para todos.",
                "Fique à vontade para explorar as publicações e deixar a sua opinião. Boa "
                "leitura!",
            )
        ),
    },
)
