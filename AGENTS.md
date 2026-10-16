# AGENTS.md — Regras para IA neste projeto

Este é o **arquivo único de regras** para qualquer IA que trabalhe neste repositório (Claude Code,
Copilot, Cursor, ChatGPT, Codex etc.). Leia o arquivo inteiro antes de qualquer tarefa.

- Projeto da disciplina **Tópicos Especiais em Engenharia de Software**.
- Idioma de respostas, código, comentários, commits e documentação: **português**.
- Em caso de conflito entre um pedido e estas regras, as regras valem. Avise quem pediu.

---

## 1. O projeto e o escopo

**Sistema de Monitoramento do Sono por Câmera e Inteligência Artificial.**

Uma câmera com visão noturna (infravermelho) captura imagens em tempo real de uma pessoa dormindo.
O software processa os quadros, detecta **comportamentos observáveis** (presença, rosto, olhos, movimentos
da cabeça e do corpo), classifica esses comportamentos, estima estados comportamentais e apresenta os
resultados num dashboard.

```
câmera → captura → detecção → classificação → registro → dashboard
```

### O que o sistema não faz (vale para qualquer escopo)

- **Não faz diagnóstico** médico nem interpretação clínica.
- **Não identifica fases do sono** (N1, N2, N3, REM). As fases dependem de sinais elétricos do cérebro
  (EEG, EOG, EMG) que uma câmera não mede.
- **Não substitui** a polissonografia nem qualquer exame.
- A interface sempre mostra o aviso de que os resultados são estimativas comportamentais, não diagnóstico (RNF12).

### Requisitos

A lista vigente está em `docs/requisitos.md`, com rastreabilidade em `docs/rastreabilidade.md`.
Ela muda ao longo do projeto:

- consulte sempre a **versão atual** antes de começar; não use listas de memória ou de conversas antigas;
- todo código aponta para um requisito (a docstring cita o ID, por exemplo `RFxx`);
- quem cria ou muda requisitos são os pesquisadores, com aprovação da gestão. A IA só sugere.

## 2. O que a IA pode fazer

- Ler os arquivos do repositório, exceto mídia e dados pessoais (seção 3).
- Criar e alterar arquivos **dentro da tarefa pedida**.
- Rodar os testes (`pytest`) e o sistema localmente para conferir o próprio trabalho.
- Explicar o código e responder perguntas sobre o projeto.
- Sugerir melhorias, problemas e requisitos que faltam, **sem aplicar** o que não foi pedido.
- Criar o registro da tarefa em `agents-context/` (obrigatório, seção 4).

## 3. O que a IA não pode fazer

**Arquivos e escopo da tarefa**

- Apagar, mover ou renomear arquivos ou pastas sem pedido explícito, nem para "limpar" ou "organizar".
- Mexer fora da tarefa pedida: outro módulo, refatoração não pedida, formatação geral, renomear coisas.
  Se a tarefa exigir isso, pare e pergunte.
- Criar função, classe, tabela, tipo de evento, tela ou dependência sem requisito vigente.
- Instalar ou adicionar biblioteca sem acordo da equipe.
- Decidir pendências listadas no `README.md`. Avise em vez de escolher.
- Alterar ou apagar registros antigos de `agents-context/`.
- Criar `CLAUDE.md` ou `CLAUDE.local.md` no projeto. Se um deles existir, o Claude Code deixa de ler este AGENTS.md.

**Conteúdo**

- Gerar diagnóstico, interpretação clínica, fase do sono ou nome de doença em qualquer lugar: texto da
  tela, relatório, nome de variável, tipo de evento ou comentário.
- Apresentar estimativas comportamentais como identificação clínica dos estágios do sono (RN10, RNF12).

**Privacidade (LGPD: dados de saúde são sensíveis, art. 11)**

- Colocar no repositório vídeo, imagens extraídas das gravações ou o banco de dados.
- Ler, copiar, enviar ou resumir arquivos da pasta compartilhada restrita ou da pasta `dados/`.
- Usar gravação real em testes. Testes usam dados gerados em código.
- Escrever senha, token ou endereço de câmera com usuário e senha (RTSP) no código.
- Alterar o `.gitignore` para liberar mídia ou dados.

**Git**

- Fazer `git commit`, `git push`, criar branch ou fazer merge sem pedido explícito.
- Fazer qualquer commit ou push na branch `main`.

## 4. Registro obrigatório em `agents-context/`

`agents-context/` é o histórico de tudo que a IA fez no projeto.

**Quando:** a cada pedido feito à IA, ela cria **um arquivo novo** ao final da tarefa. Vale também
para tarefa interrompida, parcial ou que falhou.

**Nome do arquivo:** `AAAA-MM-DD_HH-MM_descricao-curta.md`

- Data e hora do **relógio do sistema**, nunca estimadas. Para obter:
  - Windows (PowerShell): `Get-Date -Format "yyyy-MM-dd_HH-mm"`
  - Linux / macOS: `date +%Y-%m-%d_%H-%M`
- Descrição em minúsculas, sem acento, palavras separadas por hífen, até 5 palavras.
- Se já existir um arquivo com o mesmo nome, acrescente `-2`, `-3`.
- Exemplo: `2026-10-15_14-30_cor-de-fundo.md`

**Regras:**

- Nunca edite nem apague um registro antigo. Para corrigir algo, crie um registro novo que cite o antigo.
- Não coloque dados pessoais, trechos de gravação, senhas nem caminhos da pasta compartilhada.
- Seja específico: liste arquivos pelo caminho, não "alguns arquivos".

**Conteúdo do arquivo (modelo):**

```markdown
# <Título curto da tarefa>

- **Data e hora:** AAAA-MM-DD HH:MM
- **Pedido por:** <nome ou cargo de quem pediu>
- **Ferramenta:** <ex.: Claude Code, Copilot>
- **Requisitos relacionados:** <IDs da lista vigente ou "nenhum">

## Pedido e contexto
O que foi pedido, com as palavras de quem pediu, e por que.

## O que foi feito
- **Criado:** `caminho/arquivo` — o que é
- **Alterado:** `caminho/arquivo` — o que mudou
- **Excluído:** `caminho/arquivo` — motivo (ou "nada")

## Decisões e motivos
- Decisão tomada e por quê. Alternativas descartadas, se houver.

## Verificação
Testes rodados e resultado (ex.: `pytest`: 2 passaram).

## Pendências
O que ficou para depois ou precisa de decisão da equipe (ou "nenhuma").
```

## 5. Estrutura e arquitetura

O sistema é um **monólito modular**: um único programa Python, dividido em módulos com uma
responsabilidade cada, que conversam só por funções públicas.

| Pasta | O que tem | Dono |
|---|---|---|
| `src/monitor_sono/captura/` | Captura de imagens da câmera em tempo real (RF02) | Analistas de vídeo |
| `src/monitor_sono/deteccao/` | Detecção visual: presença, rosto, olhos, cabeça, corpo, visibilidade | Analistas de vídeo |
| `src/monitor_sono/classificacao/` | Classificação de comportamentos e estimativa de estados (RF09–RF11) | Analistas de vídeo |
| `src/monitor_sono/registro/` | Grava e consulta sessões, comportamentos e estados no banco | Analista de dados |
| `src/monitor_sono/sessao/` | Abre e encerra sessões | Analista de dados |
| `src/monitor_sono/dashboard/` | Telas de resultado | Analista de telas |
| `src/monitor_sono/config.py` | Caminhos, parâmetros e aviso de não diagnóstico | Todos (mudança combinada) |
| `tests/` | Testes automatizados | Todos |
| `docs/` | Documentação, requisitos e rastreabilidade | Analistas e documentadores |
| `agents-context/` | Histórico do que a IA fez | IA (só cria arquivos novos) |

### Quem pode importar quem

| Módulo | Pode importar | Não pode importar |
|---|---|---|
| `captura` | `config` | qualquer outro módulo do projeto |
| `deteccao` | `config` | `captura`, `classificacao`, `registro`, `dashboard` |
| `classificacao` | `config` | `captura`, `deteccao`, `registro`, `dashboard` |
| `registro` | `config` | `captura`, `deteccao`, `classificacao`, `dashboard` |
| `sessao` | `config`, `registro` | `captura`, `deteccao`, `classificacao`, `dashboard` |
| `dashboard` | `config`, `registro` | `captura`, `deteccao`, `classificacao`; também não abre o banco direto |

- A detecção recebe os quadros como parâmetro, então pode ser testada sem câmera.
- A classificação recebe listas de comportamentos, não quadros.
- O dashboard só lê pelo `registro`. Se o banco mudar, as telas continuam funcionando.
- O formato que um módulo entrega ao outro é um **contrato**: só muda com aviso a quem usa.
- A ligação entre captura, detecção, classificação e registro (pipeline) ainda não tem módulo definido. A equipe decide.

## 6. Código e testes

- Type hints e docstring citando o requisito em toda função pública.
- Funções pendentes lançam `NotImplementedError("RFxx: a implementar")`.
- Nada de número mágico: limiares, resolução, quadros por segundo e caminhos ficam em `config.py`.
- Comportamentos só entram em `config.COMPORTAMENTOS` com requisito vigente. O banco recusa o resto.
- Simples primeiro: para movimento, diferença entre quadros antes de qualquer deep learning.
- Licenças: Ultralytics/YOLO e Grafana são AGPL-3.0 e OpenPose é só acadêmico. Não use sem registro
  da equipe.
- Todo código novo vem com teste em `tests/test_<modulo>.py`, usando dados gerados em código e banco
  temporário (`tmp_path`). `pytest` precisa passar antes de entregar.

## 7. Fluxo no git (para as pessoas da equipe)

- A `main` é protegida: só recebe código por pull request aprovado por **outro analista**.
- Uma branch por tarefa: `rfxx-descricao-curta`. Commits começam pelo requisito: `RFxx: o que mudou`.
- Antes de cada commit, rode `git status` e confira que não aparece mídia, banco, `dados/`, `.venv`,
  `.idea` ou `.claude/settings.local.json`.
- Os registros de `agents-context/` vão no mesmo commit da mudança que descrevem.

## 8. Ao terminar uma tarefa (checklist da IA)

1. `pytest` passando, se mexeu em código.
2. Docstrings citando o requisito atendido, conferido na lista vigente.
3. `docs/rastreabilidade.md` atualizado, se a situação de algum requisito mudou.
4. Registro criado em `agents-context/`.
5. Resumo para quem pediu: o que mudou, requisitos atendidos e pendências.

## 9. Contexto técnico

- **Linguagem e ferramentas:** Python, OpenCV (vídeo e visão computacional), SQLite (banco local),
  Streamlit (dashboard), pytest (testes). Código em `src/monitor_sono/`, instalação com `pip install -e .`.
- **Entrada:** exclusivamente câmera (RNF01, RN09). Sem áudio.
- **Movimento:** diferença entre quadros na região da cama, a 1 ou 2 quadros por segundo, em 320×240 e
  escala de cinza. Subtração de fundo não serve como método principal, porque uma pessoa parada vira
  "fundo".
- **Postura:** só se um teste com a pessoa coberta funcionar. O cobertor é o maior risco técnico.
- **Gravações:** ficam só na pasta compartilhada restrita da equipe, nunca no repositório.
