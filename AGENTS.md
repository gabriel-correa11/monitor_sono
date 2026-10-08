# AGENTS.md — Regras de desenvolvimento

Regras para todos os analistas e para qualquer assistente de código (Claude Code, Copilot, Cursor,
Codex etc.) que trabalhe neste repositório. O contexto do projeto está no `README.md` e os requisitos em
`docs/rastreabilidade.md`.

Projeto da disciplina Tópicos Especiais em Engenharia de Software.
Idioma do código, comentários, commits e documentação: **português**.

---

## 1. Regras que não se quebram

1. **Todo código segue os requisitos vigentes.** Nenhuma função, tela, tabela ou tipo de evento existe
   sem um requisito que o justifique (seção 2). Se algo parecer necessário e não tiver requisito, não
   implemente: registre como pendência e leve para a equipe.
2. **Sem diagnóstico e sem fases do sono.** O sistema detecta e apresenta eventos observáveis. Nenhum
   texto, nome de variável, tipo de evento ou tela pode sugerir diagnóstico, doença ou fase do sono
   .
3. **Dados pessoais nunca saem da máquina.** Gravações, áudio e banco ficam em `dados/`, que está no
   `.gitignore`. Nada de nuvem de terceiros, nada de gravação real em testes, nada de usuário e senha de
   câmera (RTSP) no código.
4. **Ninguém revisa o próprio código.** Cada entrega é testada e revisada por outro analista.
5. **Pendências não são decididas no código.** As decisões abertas listadas no README não são
   resolvidas por quem está programando nem pelo assistente de código.

## 2. Requisitos

A lista de requisitos **muda ao longo do projeto**: requisitos entram, saem e são reescritos conforme as
decisões da equipe. Por isso este arquivo não repete a lista. A fonte é sempre a versão atual de
`docs/rastreabilidade.md`, que acompanha o documento de requisitos aprovado.

- **Antes de começar** qualquer tarefa, consulte a versão atual da lista. Não confie em memória, em
  conversa antiga nem em listas copiadas em outros arquivos.
- **Todo código aponta para um requisito.** A docstring de cada arquivo e de cada função pública cita o
  ID (por exemplo, `RFxx` ou `RNFxx`). Código sem requisito não entra.
- **Requisito mudou?** Ajuste o código afetado e a rastreabilidade na mesma tarefa. Se um requisito saiu
  da lista, o código dele sai também.
- **Requisito ambíguo?** Pergunte à equipe antes de interpretar. A interpretação vira parte do requisito,
  não fica só no código.
- **Quem altera a lista** são os pesquisadores, com aprovação da gestão. Analistas e assistentes de
  código não criam nem mudam requisitos, só sugerem.

## 3. Arquitetura modular

O sistema é um **monólito modular**: um único programa Python, dividido em módulos com uma
responsabilidade cada, que conversam só por funções públicas e tipos definidos. Cada módulo corresponde a
uma etapa do fluxo:

```
captura  →  deteccao  →  registro  →  dashboard
   ↑                        ↑
 (vídeo/áudio)           sessao
```

| Módulo | Responsabilidade | Dono |
|---|---|---|
| `captura/` | Abrir vídeo e áudio e entregar quadros e janelas de som | Analistas de vídeo |
| `deteccao/` | Transformar quadros e som em eventos | Analistas de vídeo |
| `registro/` | Gravar e consultar sessões e eventos no banco | Analista de dados |
| `sessao/` | Abrir e encerrar sessões | Analista de dados |
| `dashboard/` | Mostrar os resultados ao usuário | Analista de telas |
| `config.py` | Caminhos, parâmetros e aviso de não diagnóstico | Todos (mudança combinada) |

Quais requisitos cada módulo atende está na rastreabilidade, não aqui.

### Quem pode importar quem

| Módulo | Pode importar | Não pode importar |
|---|---|---|
| `captura` | `config` | qualquer outro módulo do projeto |
| `deteccao` | `config` | `captura`, `registro`, `dashboard` |
| `registro` | `config` | `captura`, `deteccao`, `dashboard` |
| `sessao` | `config`, `registro` | `captura`, `deteccao`, `dashboard` |
| `dashboard` | `config`, `registro` | `captura`, `deteccao`; também não abre o SQLite direto |

Por quê:

- **`deteccao` não importa `captura`.** Ela recebe os quadros como parâmetro. Assim dá para testar a
  detecção com quadros gerados em código, sem precisar de gravação.
- **`dashboard` só lê pelo `registro`.** Se o banco mudar, só o `registro` muda, e as telas continuam
  funcionando.
- **Ninguém importa `dashboard`.** A tela é a ponta do fluxo.

A ligação entre captura, detecção e registro ainda não tem módulo definido. Quando chegar a hora, a equipe decide onde ela fica e atualiza esta seção.

### Contratos entre módulos

Os tipos que passam de um módulo para outro são o "acordo" entre os analistas. Mudar um contrato quebra o
trabalho de outra pessoa, então **só se muda com aviso a quem usa**.

| Saída de | Para | Formato |
|---|---|---|
| `captura.video.ler_quadros()` | `deteccao.movimento` | iterador de `(segundo: float, quadro: numpy.ndarray)`, quadro em escala de cinza, na resolução de `config` |
| `captura.audio.ler_audio()` | `deteccao.som` | iterador de `(segundo: float, janela: numpy.ndarray)` mono, ou `None` se não houver áudio |
| `deteccao.movimento.detectar_movimentos()` | registro | lista de `Movimento` (início, fim, intensidade) |
| `deteccao.som.detectar_eventos_sonoros()` | registro | lista de `EventoSonoro` (início, fim, tipo, nível) |
| `registro.banco` | `dashboard`, `sessao` | funções públicas: `criar_sessao`, `finalizar_sessao`, `registrar_evento`, `listar_sessoes`, `eventos_da_sessao` |

Os nomes e campos exatos estão no código. Em caso de diferença, vale o código, e esta tabela deve ser
corrigida.

## 4. Como escrever o código

- **Funções pendentes** lançam `NotImplementedError("RFxx: implementar até dd/mm")`.
- **Type hints** em toda função pública.
- **Nada de número mágico.** Limiares, resoluções, quadros por segundo e caminhos ficam em `config.py`.
- **Tipos de evento** só entram em `config.TIPOS_EVENTO` com requisito vigente. O banco recusa o resto.
- **Bibliotecas novas** só com acordo da equipe. Antes de adicionar, confira a licença: AGPL
  (Ultralytics/YOLO, Grafana) e uso só acadêmico (OpenPose) precisam ser registrados nas decisões.
- **Simples primeiro.** Para movimento, diferença entre quadros antes de qualquer deep learning, como
  recomenda o levantamento técnico.

## 5. Testes

- Todo código novo vem com teste em `tests/`, com nome `test_<modulo>.py`.
- Testes **não usam gravação real**. Use quadros e sinais gerados em código (por exemplo, matrizes
  `numpy` com e sem diferença) e banco temporário (`tmp_path`).
- `pytest` precisa passar antes de qualquer pedido de revisão.

## 6. Fluxo de trabalho no git

- A branch `main` sempre roda. Ninguém faz commit direto nela.
- Uma branch por tarefa, com o requisito no nome: `rfxx-descricao-curta`.
- Mensagem de commit começa pelo requisito: `RFxx: o que mudou`.
- Para juntar na `main`: pull request revisado por **outro analista**, com `pytest` passando.
- Antes de cada commit, rode `git status` e confira que nada de `dados/`, vídeo, áudio, banco, `.venv`,
  `.idea` ou `.claude/settings.local.json` aparece.

## 7. Quando terminar uma tarefa

1. `pytest` passando.
2. Docstrings citando o requisito atendido, conferido na lista vigente.
3. `docs/rastreabilidade.md` atualizado: situação do requisito, teste que cobre e uma linha no histórico.
4. README atualizado só se mudou como rodar, a estrutura ou uma pendência.
5. Pull request aberto e revisor avisado.

## 8. Regras para assistentes de código

Além de tudo acima, um assistente de código trabalhando neste repositório:

- lê este arquivo, o `README.md` e a versão atual do `docs/rastreabilidade.md` antes de mexer no código;
- confere se a tarefa pedida tem requisito vigente; se não tiver, avisa antes de fazer qualquer coisa;
- só altera o módulo da tarefa pedida; se precisar mexer em outro módulo ou num contrato, para e pergunta;
- não cria função, classe, tabela, tipo de evento, tela ou dependência sem requisito;
- não faz `git commit`, `git push` ou cria branch sem pedido explícito;
- não lê, copia nem envia arquivos de `dados/`;
- quando uma tarefa toca numa pendência, avisa em vez de escolher uma solução;
- no fim, informa quais requisitos foram atendidos e o que mudou na rastreabilidade.