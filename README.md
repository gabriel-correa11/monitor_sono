# Monitor de Sono

**Sistema de Monitoramento do Sono por Câmera, Áudio e Inteligência Artificial**

Projeto da disciplina **Tópicos Especiais em Engenharia de Software**.

> Este sistema **monitora e apresenta dados observados**. Ele não faz diagnóstico médico, não faz
> interpretação clínica e não identifica fases do sono. Os resultados não substituem a polissonografia
> nem qualquer exame.

---

## 1. O que é o projeto

Uma câmera com visão noturna (infravermelho), e opcionalmente um microfone, grava uma pessoa dormindo
durante a noite. O software lê essa gravação, detecta **eventos observáveis**, registra cada evento com
data e horário e apresenta tudo num painel (dashboard). Os eventos são movimentos do corpo e,
dependendo do escopo final, alguns sons.

```
pessoa dormindo → câmera / microfone → captura → processamento → eventos → banco → dashboard / relatório
```

O que o usuário vê no final:

- a linha do tempo dos eventos da noite (RF08);
- um resumo da sessão (RF09);
- as sessões anteriores (RF10);
- um relatório dos resultados (RF11).

## 2. Por que o escopo é este

O escopo saiu de três documentos produzidos pela equipe antes do código:

| Documento | Responsáveis | Conclusão que afeta o software |
|---|---|---|
| Pesquisa bibliográfica | Pesquisadores | Monitoramento do sono sem contato, por câmera e áudio, é uma linha de pesquisa consolidada. A polissonografia é a referência clínica, então o sistema não pode se apresentar como diagnóstico. A LGPD trata dados de saúde como sensíveis. |
| Pesquisa de viabilidade | Pesquisadores | O projeto é viável **com escopo reduzido**: um MVP que detecta, registra e mostra eventos observáveis. Treinar uma IA própria, classificar fases do sono e diagnosticar estão fora do prazo. É deste documento que vem a **lista oficial de requisitos**. |
| Levantamento de tecnologia e equipamento | Analistas | A câmera mede bem **movimento** (a "actigrafia por vídeo" já foi validada contra polissonografia). Ela não mede as fases do sono, que dependem de sinais elétricos do cérebro. Python é a escolha natural, porque todas as bibliotecas necessárias têm suporte de primeira linha. |

### Regra da equipe

**Nada é implementado fora da lista de requisitos.** Se algo parecer necessário e não estiver na lista,
primeiro vira requisito aprovado, depois vira código. Isso mantém a documentação consistente com o
software. Cada requisito tem seu arquivo, sua data e seu status em
[`docs/rastreabilidade.md`](docs/rastreabilidade.md).

## 3. Situação atual

**Entrega de 08/10: estrutura inicial do software.**

Pelo cronograma, esta entrega é a base do projeto montada, com as pastas e as partes principais
preparadas para receber o código. Ela ainda não analisa gravações.

| Parte | Situação |
|---|---|
| Pastas, pacote Python e instalação | Pronto |
| Banco de dados (sessões e eventos) | Funcionando e testado |
| Controle de sessão (iniciar e encerrar) | Funcionando sobre o banco |
| Linha de comando | Funcionando (`--help` e listagem de sessões) |
| Dashboard | Esqueleto com as seções e o aviso de não diagnóstico |
| Leitura de vídeo e áudio | Assinatura definida, implementação em 15/10 |
| Detecção de movimento e som | Assinatura definida, implementação a partir de 22/10 |

Funções ainda não implementadas lançam `NotImplementedError` com o requisito e a data prevista. Assim,
fica claro no próprio código o que falta e quando.

## 4. Estrutura do projeto

```
monitor_sono/
├── README.md                    Este arquivo
├── pyproject.toml               Pacote, dependências e configuração do pytest
├── requirements.txt             Dependências
├── .gitignore                   Mantém gravações, banco e ambiente fora do git
├── docs/
│   └── rastreabilidade.md       Requisito → arquivo → função → entrega → status
├── tests/
│   └── test_registro.py         Testes do banco (RF01, RF02, RF07, RF10)
└── src/
    └── monitor_sono/
        ├── __init__.py          Versão do pacote
        ├── __main__.py          Linha de comando
        ├── config.py            Pastas, parâmetros e aviso de não diagnóstico
        ├── sessao/              RF01, RF02   iniciar e encerrar sessão
        ├── captura/
        │   ├── video.py         RF03         receber imagens
        │   └── audio.py         RF04         receber áudio, quando houver
        ├── deteccao/
        │   ├── movimento.py     RF05         identificar movimentos
        │   └── som.py           RF06         identificar eventos sonoros do escopo
        ├── registro/
        │   └── banco.py         RF07, RF10   registrar eventos e consultar sessões
        └── dashboard/
            └── app.py           RF08, RF09, RF11   linha do tempo, resumo e relatório
```

A pasta `dados/` é criada automaticamente na primeira execução. Ela guarda as gravações e o banco e
**nunca vai para o git** (RNF01, RNF02).

### Por que cada parte é separada

Cada pasta corresponde a uma etapa do fluxo da seção 1. Isso permite que os quatro analistas trabalhem
em paralelo sem mexer no código um do outro:

| Analista | Pastas | Próxima entrega |
|---|---|---|
| Tratamento do vídeo (2) | `captura/`, `deteccao/` | 15/10: leitura das imagens (RF03) |
| Organização dos dados (1) | `registro/`, `sessao/` | Apoio às duas frentes com o banco |
| Telas (1) | `dashboard/` | 15/10: dashboard com dados de exemplo (RF08 a RF11) |

Cada analista testa o código de outro, nunca o próprio.

## 5. Tecnologias

| Ferramenta | Uso | Licença |
|---|---|---|
| Python 3.11+ | Linguagem | PSF |
| OpenCV | Leitura de vídeo e detecção de movimento | Apache 2.0 |
| librosa | Leitura e análise de áudio | ISC |
| SQLite | Banco local em um único arquivo, sem servidor | Domínio público |
| Streamlit | Dashboard | Apache 2.0 |
| pandas | Organização dos dados para o dashboard | BSD |
| pytest | Testes | MIT |

Todas as licenças são permissivas. O levantamento técnico alerta que Ultralytics (YOLO) e Grafana são
AGPL-3.0, e OpenPose é só para uso acadêmico. Se alguma delas entrar no projeto, isso precisa ser
registrado nas decisões.

### Orientações técnicas que vêm do levantamento

- **Movimento**: diferença entre quadros (frame differencing) dentro da região da cama. A subtração de
  fundo não serve como método principal, porque uma pessoa parada por muito tempo passa a ser tratada
  como fundo.
- **Desempenho**: analisar 1 ou 2 quadros por segundo em 320x240 e escala de cinza. Movimento no sono
  dura segundos, então isso basta e reduz o trabalho em cerca de 30 vezes (RNF05).
- **Áudio**: WAV mono a 16 kHz. Só analisar os trechos com energia acima do ruído de fundo do quarto.
- **Postura**: só entra se um teste piloto com a pessoa coberta funcionar. O cobertor é o maior risco
  técnico do projeto.

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
python -m monitor_sono sessoes                      # lista as sessões registradas
streamlit run src/monitor_sono/dashboard/app.py     # abre o dashboard no navegador
```

## 7. Privacidade e LGPD

Filmar uma pessoa dormindo e gerar informação sobre a saúde dela envolve **dados pessoais sensíveis**
(LGPD, art. 11). Por isso:

- a pessoa gravada assina um termo de consentimento específico antes de qualquer gravação;
- gravações e banco ficam só no computador local, sem nuvem de terceiros;
- a pasta `dados/` está no `.gitignore` e nunca é enviada ao repositório;
- endereços de câmera com usuário e senha (RTSP) não podem ficar escritos no código.

O descarte do vídeo bruto e o prazo de guarda ainda estão em aberto (RNF03, RNF04).

## 8. Pendências que dependem da equipe

Estas decisões não cabem aos analistas sozinhos. Até serem tomadas, o código não as implementa.

| Pendência | Requisito | Quem decide | Quando |
|---|---|---|---|
| Quais eventos sonoros entram (ronco? ruído?) | RF06 | Analistas, pesquisadores e gestão | 22/10 |
| Sessão ao vivo ou importação de gravação já feita | RF01, RF02 | Analistas e gestão | Antes de 15/10 |
| O que conta como movimento (limiar e duração mínima) | RF05 | Analistas, com a gravação real | 22/10 |
| Descarte do vídeo bruto e prazo de guarda | RNF03, RNF04 | Pesquisadores e gestão | A definir |
| Controle de acesso e criptografia | RNF01, RNF02 | Analistas e gestão | A definir |
| Equipamento de captura definitivo | RF03, RF04 | Analistas e pesquisadores | A confirmar |


