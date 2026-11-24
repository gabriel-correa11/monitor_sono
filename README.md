# Monitor de Sono

**Sistema de Monitoramento do Sono por Câmera e Inteligência Artificial**

Projeto da disciplina **Tópicos Especiais em Engenharia de Software**.

> Este sistema **monitora e apresenta comportamentos observados e estados estimados**. Ele não faz
> diagnóstico médico, não faz interpretação clínica e não identifica fases do sono. Os resultados não
> substituem a polissonografia nem qualquer exame (RNF12).

> Projeto em construção. O escopo foi definido como estudo de caso. A lista de requisitos vigente está
> em [`docs/requisitos.md`](docs/requisitos.md).

---

## 1. O que é o projeto

Uma câmera com visão noturna (infravermelho) captura imagens em tempo real de uma pessoa dormindo.
O software processa os quadros, detecta **comportamentos observáveis** (presença, estado dos olhos,
movimentos da cabeça e do corpo), classifica esses comportamentos, estima estados comportamentais e
apresenta tudo num painel (dashboard).

```
pessoa dormindo → câmera → captura → detecção → classificação → registro → dashboard / relatório
```

O que o usuário vê no final:

- o histórico cronológico dos comportamentos e estados estimados (RF13);
- um relatório com duração, movimentos e estados (RF14);
- as sessões anteriores (RF14);
- o aviso de que os resultados são estimativas, não diagnóstico (RNF12).

## 2. Por que o escopo é este

O escopo saiu de três documentos produzidos pela equipe antes do código:

| Documento | Conclusão que afeta o software |
|---|---|
| Pesquisa bibliográfica | Monitoramento do sono sem contato, por câmera, é uma linha de pesquisa consolidada. A polissonografia é a referência clínica, então o sistema não pode se apresentar como diagnóstico. A LGPD trata dados de saúde como sensíveis. |
| Pesquisa de viabilidade | O projeto é viável com escopo reduzido: um estudo de caso que detecta, classifica e apresenta comportamentos observáveis. É deste documento que vem a **lista oficial de requisitos**. |
| Levantamento de tecnologia | A câmera mede bem **movimento** (actigrafia por vídeo). Ela não mede as fases do sono, que dependem de sinais elétricos do cérebro. Python é a escolha natural. |

### Regra da equipe

**Nada é implementado fora da lista de requisitos.** Se algo parecer necessário e não estiver na lista,
primeiro vira requisito aprovado, depois vira código. Cada requisito tem seu arquivo, sua data e seu
status em [`docs/rastreabilidade.md`](docs/rastreabilidade.md).

## 3. Situação atual

O sistema funciona de ponta a ponta: lê a câmera ou uma gravação, detecta comportamentos, estima estados,
grava no banco e mostra no dashboard.

| Parte | Situação |
|---|---|
| Pastas, pacote Python e instalação | Pronto |
| Captura de vídeo (câmera ao vivo ou gravação) | Funcionando e testado |
| Detecção de movimento, mudança de posição e visibilidade | Funcionando e testado |
| Detecção de rosto, olhos, cabeça e presença | Funcionando e testado (cascatas Haar do OpenCV 4.x) |
| Classificação (comportamentos, períodos e estados) | Funcionando e testado |
| Pipeline e linha de comando (`analisar`) | Funcionando e testado |
| Banco de dados (sessões, comportamentos e estados) | Funcionando e testado |
| Dashboard (linha do tempo, relatório em CSV, avisos, exclusão) | Funcionando e testado |

Os limiares e tempos de `config.py` são **provisórios**: ainda precisam ser confirmados com um gabarito das
gravações. Os resultados do estudo de caso e as limitações estão em
[`docs/material-documentacao.md`](docs/material-documentacao.md). A situação de cada requisito está em
[`docs/rastreabilidade.md`](docs/rastreabilidade.md).

## 4. Estrutura do projeto

```
monitor_sono/
├── README.md                    Este arquivo
├── iniciar.bat                  Windows: menu com clique duplo (prepara, analisa, abre o dashboard, testa)
├── AGENTS.md                    Regras para IA
├── pyproject.toml               Pacote, dependências e configuração do pytest
├── requirements.txt             Dependências
├── .gitignore                   Mantém gravações, banco e ambiente fora do git
├── .gitattributes               Mantém o iniciar.bat com fim de linha do Windows
├── agents-context/              Histórico do que a IA fez
├── docs/
│   ├── requisitos.md            Lista de requisitos (RF, RNF, RN)
│   ├── rastreabilidade.md       Requisito → arquivo → função → status
│   └── material-documentacao.md Uso, resultados do estudo de caso, parâmetros e limitações
├── tests/
│   ├── test_captura.py          Testes da captura (RF02, RNF08)
│   ├── test_deteccao.py         Testes da detecção (RF03 a RF07, RF15)
│   ├── test_classificacao.py    Testes da classificação (RF09 a RF11, RN01 a RN07)
│   ├── test_dashboard.py        Testes do dashboard (RF13, RF14, RNF10, RNF12)
│   ├── test_pipeline.py         Teste de ponta a ponta com vídeo sintético e linha de comando
│   └── test_registro.py         Testes do banco (RF01, RF08, RF12, RNF05, RNF10)
└── src/
    └── monitor_sono/
        ├── __init__.py          Versão do pacote
        ├── __main__.py          Linha de comando (python -m monitor_sono analisar)
        ├── config.py            Caminhos, parâmetros e aviso de não diagnóstico
        ├── tipos.py             Formatos dos dados trocados entre os módulos
        ├── pipeline.py          Liga captura → detecção → classificação → registro
        ├── sessao/              RF01         iniciar e encerrar sessão
        ├── captura/
        │   └── video.py         RF02         capturar imagens em tempo real
        ├── deteccao/
        │   ├── presenca.py      RF03         detectar presença
        │   ├── rosto.py         RF04         detectar rosto
        │   ├── olhos.py         RF05         estado dos olhos
        │   ├── cabeca.py        RF06         movimentos da cabeça
        │   ├── movimento.py     RF07         movimentos corporais
        │   └── visibilidade.py  RF15         visibilidade insuficiente
        ├── classificacao/
        │   ├── comportamentos.py RF09        classificar comportamentos
        │   ├── estados.py       RF10         estimar estados
        │   └── periodos.py      RF11         períodos de atividade/inatividade
        ├── registro/
        │   └── banco.py         RF08, RF12   registrar comportamentos e estados
        └── dashboard/
            └── app.py           RF13, RF14   histórico, relatório e visibilidade
```

A pasta `dados/` é criada automaticamente na primeira execução. Ela guarda o banco e **nunca vai para
o git**.

### Por que cada parte é separada

Cada pasta corresponde a uma etapa do fluxo. Isso permite que os analistas trabalhem em paralelo:

| Analista | Pastas |
|---|---|
| Tratamento do vídeo (2) | `captura/`, `deteccao/`, `classificacao/` |
| Organização dos dados (1) | `registro/`, `sessao/` |
| Telas (1) | `dashboard/` |

## 5. Tecnologias

| Ferramenta | Uso | Licença |
|---|---|---|
| Python 3.11+ | Linguagem | PSF |
| OpenCV 4.x | Captura de vídeo e visão computacional (o 5.x não traz as cascatas Haar de rosto e olhos) | Apache 2.0 |
| SQLite | Banco local em um único arquivo, sem servidor | Domínio público |
| Streamlit | Dashboard | Apache 2.0 |
| pandas | Organização dos dados para o dashboard | BSD |
| Altair | Gráficos da linha do tempo no dashboard | BSD |
| pytest | Testes | MIT |

Todas as licenças são permissivas. O levantamento técnico alerta que Ultralytics (YOLO) e Grafana são
AGPL-3.0, e OpenPose é só para uso acadêmico. Se alguma delas entrar no projeto, isso precisa ser
registrado nas decisões.

## 6. Como rodar

O uso tem duas etapas:

1. **Analisar** uma gravação (ou a câmera ao vivo). O resultado vira uma **sessão** salva no banco
   `dados/monitor_sono.db`.
2. **Abrir o dashboard** no navegador para ver as sessões: linha do tempo, resumo e relatório em CSV.

Antes de tudo, instale o **Python 3.11 ou mais novo** pelo site <https://www.python.org/downloads/>. No
Windows, marque a opção **"Add python.exe to PATH"** na primeira tela do instalador.

### 6.1 Jeito mais fácil (Windows): clique duplo no `iniciar.bat`

1. Baixe o projeto: no GitHub, **Code → Download ZIP**, e extraia a pasta (ou use `git clone`).
2. Abra a pasta do projeto e dê **dois cliques em `iniciar.bat`**.
   - Na **primeira vez**, ele prepara tudo sozinho: cria a pasta `.venv` e instala as bibliotecas. Precisa
     de internet e leva alguns minutos. Nas outras vezes, o menu abre direto.
   - Se o Windows mostrar "O Windows protegeu o computador", clique em **Mais informações → Executar assim
     mesmo**. Isso acontece com qualquer arquivo `.bat` baixado da internet.
3. Escolha uma opção apertando o número:

| Tecla | O que faz |
|---|---|
| **1** | Abre o dashboard no navegador (<http://localhost:8501>). Deixe a janela preta aberta enquanto usa; para fechar, aperte `Ctrl+C` nela ou feche a janela. |
| **2** | Pergunta se a pessoa gravada assinou o termo de consentimento (RNF11), abre uma janela para escolher o vídeo (dá para escolher mais de um) e analisa. No fim, oferece abrir o dashboard. |
| **3** | Roda os testes automáticos. |
| **4** | Sai. |

**Atalho:** arraste um ou mais vídeos para cima do `iniciar.bat`. Ele analisa os vídeos direto, sem passar
pelo menu.

### 6.2 Passo a passo pelo terminal (Windows, Linux e macOS)

**1. Abra um terminal na pasta do projeto.** No Windows, abra a pasta no Explorador de Arquivos, clique na
barra de endereço, digite `cmd` e aperte Enter.

**2. Crie o ambiente do projeto (só na primeira vez).** O comando cria a pasta `.venv`, com um Python
separado só para este projeto:

```bat
python -m venv .venv
```

No Linux e no macOS, use `python3` no lugar de `python`.

**3. Ative o ambiente (toda vez que abrir um terminal novo).** Depois disso, a linha do terminal começa
com `(.venv)`.

| Terminal | Comando |
|---|---|
| Prompt de Comando (cmd) | `.venv\Scripts\activate` |
| PowerShell | `.venv\Scripts\Activate.ps1` |
| Git Bash | `source .venv/Scripts/activate` |
| Linux / macOS | `source .venv/bin/activate` |

**4. Instale o projeto e as bibliotecas (só na primeira vez).**

```bat
pip install -e .
```

A instalação precisa ser **editável** (`-e`). O `config.py` acha a pasta `dados/` a partir do local do
código-fonte, e uma instalação normal colocaria o pacote em outro lugar. Quem já tinha o `.venv` com o
OpenCV 5 precisa rodar este comando de novo, porque o projeto exige `opencv-python>=4.9,<5`.

**5. Analise uma gravação.** Use aspas quando o caminho tiver espaços:

```bat
python -m monitor_sono analisar "C:\caminho\da\gravacao.mp4" --autorizado
```

- `--autorizado` confirma que a pessoa gravada assinou o termo de consentimento (RNF11). Sem ele, o comando
  não roda.
- Uma noite de cerca de 4 horas leva de 10 a 15 minutos num notebook comum. Não feche o terminal até a linha
  de comando voltar. No fim, aparece um resumo: início e fim, comportamentos encontrados e interrupções da
  gravação.
- Os horários vêm da data e hora que a câmera grava no canto da imagem. Isso corrige o relógio do vídeo e
  marca como "câmera sem visão" os trechos em que a câmera parou de gravar.
- `--inicio "2026-11-20 22:30"` só é usado quando a câmera não grava data e hora legíveis na imagem. Sem
  ele, a sessão começa no momento da análise.
- Para usar a câmera ao vivo, troque o caminho pelo número da câmera: `analisar 0 --autorizado`. `Ctrl+C`
  encerra a sessão.
- Cada análise cria uma sessão nova. Analisar a mesma gravação duas vezes deixa a sessão repetida no
  dashboard, e ela pode ser excluída por lá.

**6. Abra o dashboard.**

```bat
streamlit run src/monitor_sono/dashboard/app.py
```

O navegador abre em <http://localhost:8501>; se não abrir, digite o endereço. Escolha a sessão na lista do
topo. Deixe o terminal aberto enquanto usa; `Ctrl+C` fecha o dashboard. Análise e dashboard rodam em
processos separados (o dashboard só lê o banco), então dá para deixar o dashboard aberto num terminal e
analisar em outro. Depois de uma análise nova, aperte `F5` no navegador.

**7. Rode os testes (opcional).**

```bat
pip install pytest
pytest --basetemp .pytest-tmp
```

O `--basetemp` evita um erro de permissão do Windows quando o pytest apaga os arquivos temporários.

### 6.3 Problemas comuns

| O que aparece | O que fazer |
|---|---|
| `'python' não é reconhecido como um comando` | O Python não está instalado ou não está no PATH. Reinstale marcando "Add python.exe to PATH", ou use `py` no lugar de `python`. |
| `No module named monitor_sono` ou `No module named streamlit` | O ambiente não está ativado (passo 3) ou a instalação não foi feita (passo 4). |
| PowerShell: "a execução de scripts foi desabilitada neste sistema" | Use o Prompt de Comando (cmd), ou rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| O dashboard abre em outra porta (8502, 8503...) | Já existe um dashboard aberto em outra janela. Use aquele, ou feche a outra janela. |
| A análise para com uma mensagem sobre a câmera ou o caminho | Confira o caminho do vídeo (com aspas) ou o número da câmera. |
| `PermissionError` no fim do `pytest` | Rode com `--basetemp .pytest-tmp`, como no passo 7. |

## 7. Privacidade e LGPD

Filmar uma pessoa dormindo e gerar informação sobre a saúde dela envolve **dados pessoais sensíveis**
(LGPD, art. 11). Por isso:

- a pessoa gravada assina um termo de consentimento específico antes de qualquer gravação (RNF11);
- gravações e banco ficam só no computador local, sem nuvem de terceiros;
- a pasta `dados/` está no `.gitignore` e nunca é enviada ao repositório;
- endereços de câmera com usuário e senha (RTSP) não podem ficar escritos no código.

## 8. Pendências

- Confirmar os limiares e tempos provisórios de `config.py` com um gabarito das gravações (RF03 a RF07,
  RF09 a RF11, RN01–RN05) — pesquisadores e analistas.
- Confirmar os estados provisórios: vigília, possível sono e indeterminado (RF10, RN07) — pesquisadores e
  gestão.
- Rever a regra de "olhos fechados" com um gabarito (RF05, RN02, RN06) — pesquisadores e analistas.
- Controle de acesso e termo de consentimento (RNF06, RNF11) — pesquisadores e gestão.
