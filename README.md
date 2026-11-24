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
| Dashboard (linha do tempo, relatório em CSV, avisos, exclusão) | Funcionando (verificação manual) |

Os limiares e tempos de `config.py` são **provisórios**: ainda precisam ser confirmados com um gabarito das
gravações. Os resultados do estudo de caso e as limitações estão em
[`docs/material-documentacao.md`](docs/material-documentacao.md). A situação de cada requisito está em
[`docs/rastreabilidade.md`](docs/rastreabilidade.md).

## 4. Estrutura do projeto

```
monitor_sono/
├── README.md                    Este arquivo
├── AGENTS.md                    Regras para IA
├── pyproject.toml               Pacote, dependências e configuração do pytest
├── requirements.txt             Dependências
├── .gitignore                   Mantém gravações, banco e ambiente fora do git
├── agents-context/              Histórico do que a IA fez
├── docs/
│   ├── requisitos.md            Lista de requisitos (RF, RNF, RN)
│   ├── rastreabilidade.md       Requisito → arquivo → função → status
│   └── material-documentacao.md Uso, resultados do estudo de caso, parâmetros e limitações
├── tests/
│   ├── test_captura.py          Testes da captura (RF02, RNF08)
│   ├── test_deteccao.py         Testes da detecção (RF03 a RF07, RF15)
│   ├── test_classificacao.py    Testes da classificação (RF09 a RF11, RN01 a RN07)
│   ├── test_pipeline.py         Teste de ponta a ponta com vídeo sintético
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
| pytest | Testes | MIT |

Todas as licenças são permissivas. O levantamento técnico alerta que Ultralytics (YOLO) e Grafana são
AGPL-3.0, e OpenPose é só para uso acadêmico. Se alguma delas entrar no projeto, isso precisa ser
registrado nas decisões.

## 6. Como rodar

Requisito: Python 3.11 ou mais novo.

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

**Windows (Git Bash)**

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -e .
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

A instalação precisa ser **editável** (`-e`). O `config.py` localiza a pasta `dados/` a partir do local
do código-fonte, e uma instalação normal colocaria o pacote em outro lugar.

Quem já tinha o `.venv` com o OpenCV 5 precisa rodar `pip install -e .` de novo: o projeto agora exige
`opencv-python>=4.9,<5`.

Depois de instalado:

```bash
pytest                                              # roda os testes
python -m monitor_sono analisar 0 --autorizado      # câmera ao vivo; Ctrl+C encerra a sessão
python -m monitor_sono analisar "caminho/da/gravacao.mp4" --inicio "2026-11-20 22:30" --autorizado
streamlit run src/monitor_sono/dashboard/app.py     # abre o dashboard no navegador
```

- `--autorizado` confirma que a pessoa monitorada assinou o termo de consentimento (RNF11). Sem ele, o
  comando não roda.
- `--inicio` é a data e hora real em que a gravação começou. Sem ele, usa o momento da análise.
- Análise e dashboard rodam em processos separados: o dashboard só lê o banco.

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
