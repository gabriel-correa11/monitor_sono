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

A base do projeto está montada, com as pastas e as partes principais preparadas para receber o código.
Ela ainda não processa imagens da câmera.

| Parte | Situação |
|---|---|
| Pastas, pacote Python e instalação | Pronto |
| Banco de dados (sessões, comportamentos e estados) | Funcionando e testado |
| Controle de sessão (iniciar e encerrar) | Funcionando sobre o banco |
| Linha de comando | Funcionando (`--help`) |
| Dashboard | Esqueleto com seções e aviso de não diagnóstico |
| Captura de vídeo (câmera em tempo real) | Assinatura definida |
| Detecção (presença, rosto, olhos, cabeça, corpo, visibilidade) | Assinatura definida |
| Classificação (comportamentos, estados, períodos) | Assinatura definida |

Funções ainda não implementadas lançam `NotImplementedError` com o requisito. Assim, fica claro no
próprio código o que falta.

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
│   └── rastreabilidade.md       Requisito → arquivo → função → status
├── tests/
│   └── test_registro.py         Testes do banco (RF01, RF08, RF12, RNF10)
└── src/
    └── monitor_sono/
        ├── __init__.py          Versão do pacote
        ├── __main__.py          Linha de comando
        ├── config.py            Caminhos, parâmetros e aviso de não diagnóstico
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
| OpenCV | Captura de vídeo e visão computacional | Apache 2.0 |
| SQLite | Banco local em um único arquivo, sem servidor | Domínio público |
| Streamlit | Dashboard | Apache 2.0 |
| pandas | Organização dos dados para o dashboard | BSD |
| pytest | Testes | MIT |

Todas as licenças são permissivas. O levantamento técnico alerta que Ultralytics (YOLO) e Grafana são
AGPL-3.0, e OpenPose é só para uso acadêmico. Se alguma delas entrar no projeto, isso precisa ser
registrado nas decisões.

## 6. Como rodar

Requisito: Python 3.11 ou mais novo.

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
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

Depois de instalado:

```bash
pytest                                              # roda os testes
python -m monitor_sono --help                       # confere a linha de comando
streamlit run src/monitor_sono/dashboard/app.py     # abre o dashboard no navegador
```

## 7. Privacidade e LGPD

Filmar uma pessoa dormindo e gerar informação sobre a saúde dela envolve **dados pessoais sensíveis**
(LGPD, art. 11). Por isso:

- a pessoa gravada assina um termo de consentimento específico antes de qualquer gravação (RNF11);
- gravações e banco ficam só no computador local, sem nuvem de terceiros;
- a pasta `dados/` está no `.gitignore` e nunca é enviada ao repositório;
- endereços de câmera com usuário e senha (RTSP) não podem ficar escritos no código.

## 8. Pendências

- Limiares e critérios de classificação (RF09, RN01–RN05) — equipe decide.
- Lista confirmada de estados comportamentais válidos (RF10, RN07) — pesquisadores decidem.
- Módulo pipeline que liga captura → detecção → classificação → registro — equipe decide.
- Controle de acesso e termo de consentimento (RNF06, RNF11) — pesquisadores e gestão.
