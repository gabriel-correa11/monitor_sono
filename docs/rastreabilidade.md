# Matriz de Rastreabilidade de Requisitos

**Projeto:** Sistema de Monitoramento do Sono por Câmera e Inteligência Artificial
**Disciplina:** Tópicos Especiais em Engenharia de Software
**Versão:** 3.1 (rosto, olhos, cabeça e presença — estudo de caso)

## Para que serve este documento

A matriz liga cada requisito ao ponto do código que o atende e à sua situação atual. Ela tem três usos:

1. **Durante o desenvolvimento**: mostra o que falta e evita código sem requisito (regra da equipe).
2. **Para a documentação**: é a fonte para a documentação técnica e para o documento de requisitos finalizado.
3. **No fim do projeto**: é a base da conferência de requisitos atendidos, que aparece na apresentação.

**Base:** lista de requisitos da *Pesquisa de Viabilidade* (RF01 a RF15, RNF01 a RNF12, RN01 a RN10),
transcrita em `docs/requisitos.md`.

**Atualização:** a cada entrega, quem mexeu no código atualiza a coluna Situação e registra a mudança no
histórico, no fim do documento.

### Legenda de situação

| Situação | Significado |
|---|---|
| Implementado | Funciona e tem teste automatizado (ou verificação manual, quando indicado) |
| Parcial | Funciona para parte do requisito; o que falta está na coluna de observações |
| Estrutura pronta | Funciona parcialmente ou sem teste; base pronta para completar |
| Assinatura definida | Arquivo e função criados, sem implementação (`NotImplementedError`) |
| Aguardando decisão | Depende de uma decisão da equipe antes de ser implementado |
| Não iniciado | Ainda não tem nenhum ponto no código |

Caminhos relativos a `src/monitor_sono/`.

## Requisitos funcionais

| ID | Requisito | Arquivo | Função / elemento | Situação | Teste |
|---|---|---|---|---|---|
| RF01 | Iniciar e encerrar sessão de monitoramento | `pipeline.py`, `registro/banco.py`, `sessao/__init__.py` | `analisar()`, `criar_sessao()`, `finalizar_sessao()` | Implementado | `test_pipeline.py`, `test_registro.py` |
| RF02 | Capturar imagens em tempo real pela câmera | `captura/video.py` | `capturar_quadros()` | Implementado | `test_captura.py` (8 testes) |
| RF03 | Identificar presença de pessoa na área monitorada | `deteccao/presenca.py` | `detectar_presenca()`, `AcompanhamentoPresenca` | Implementado | `test_deteccao.py` |
| RF04 | Detectar a região facial do indivíduo | `deteccao/rosto.py` | `detectar_rosto()`, `mesmo_rosto()` | Implementado | `test_deteccao.py` (cascata simulada) |
| RF05 | Identificar estado dos olhos (abertos, fechados, indeterminado) | `deteccao/olhos.py` | `detectar_estado_olhos()`, `AcompanhamentoOlhos` | Implementado | `test_deteccao.py`, `test_pipeline.py` (detector simulado) |
| RF06 | Detectar movimentos da cabeça | `deteccao/cabeca.py`, `pipeline.py` | `detectar_movimento_cabeca()`, `AcompanhamentoCabeca` | Implementado | `test_deteccao.py`, `test_pipeline.py` |
| RF07 | Identificar movimentos corporais e mudanças de posição | `deteccao/movimento.py` | `analisar_movimento()`, `detectar_movimento_corporal()`, `detectar_mudanca_posicao()` | Implementado | `test_deteccao.py` |
| RF08 | Registrar movimentos com horários | `registro/banco.py`, `pipeline.py` | `registrar_comportamento()`, tabela `comportamentos` | Implementado | `test_registro.py`, `test_pipeline.py` |
| RF09 | Classificar comportamentos conforme critérios | `classificacao/comportamentos.py` | `classificar_comportamentos()`, `periodos_maior_atividade()` | Implementado | `test_classificacao.py`, `test_pipeline.py` |
| RF10 | Estimar estados de sono a partir de características visuais | `classificacao/estados.py` | `estimar_estados()` | Parcial | `test_classificacao.py`, `test_pipeline.py` |
| RF11 | Identificar períodos de movimentação e ausência | `classificacao/periodos.py` | `identificar_periodos()` | Implementado | `test_classificacao.py` |
| RF12 | Armazenar resultados das classificações | `registro/banco.py`, `pipeline.py` | `registrar_estado()`, tabela `estados` | Implementado | `test_registro.py`, `test_pipeline.py` |
| RF13 | Apresentar histórico cronológico de comportamentos e estados | `dashboard/app.py` | seção "Linha do tempo" (Observado e Estimado) | Implementado | `test_dashboard.py` |
| RF14 | Gerar relatório da sessão | `dashboard/app.py` | "Resumo da sessão", "Relatório" (CSV com resumo da sessão antes da lista de eventos) | Implementado | `test_dashboard.py` |
| RF15 | Sinalizar visibilidade insuficiente da câmera | `deteccao/visibilidade.py`, `dashboard/app.py` | `avaliar_visibilidade()`, `considerar_presenca()`, seção "Avisos" | Implementado | `test_deteccao.py`, `test_classificacao.py` |

### Observações

- **RF01**: a sessão pode vir da câmera ao vivo ou de uma gravação feita pela câmera (estudo de caso), pelo comando
  `python -m monitor_sono analisar <fonte> --autorizado`. Com gravação, o tempo vem do próprio vídeo; a data e hora
  real de início pode ser informada com `--inicio`.
- **RF02**: corrigida a perda de quadros com câmera a 5 fps (a versão anterior entregava 3.000 quadros por hora em
  vez de 3.600) e acrescentada a tolerância a falhas de leitura (RNF08).
- **RF03 a RF06**: decisão da equipe: usar o OpenCV 4.x (`opencv-python>=4.9,<5`), que traz as cascatas Haar de
  rosto e olhos em `cv2.data.haarcascades`. O OpenCV 5 não traz mais essas cascatas.
- **RF03**: há presença se houve rosto ou movimento nos últimos 30 min (`config.JANELA_PRESENCA_S`). A janela é longa
  porque uma pessoa dormindo parada não gera movimento e muitas vezes não mostra o rosto.
- **RF04**: cascatas frontal e de perfil (dos dois lados), com histograma equalizado, numa cópia de 960 px de
  largura do quadro original. Quando há rosto no quadro anterior, a busca começa ao redor dele.
- **RF05**: um quadro sozinho só dá "abertos" ou "indeterminado". "Fechados" exige rosto de frente, com pelo menos
  120 px e nítido, acompanhado entre quadros, com olhos já vistos abertos nesse acompanhamento e sumidos por 5
  quadros seguidos (RN06). **Limitação:** se o rosto some por mais que a folga (3 quadros), o acompanhamento
  reinicia e "fechados" só volta depois de os olhos serem vistos abertos de novo. Por isso o "possível sono" tende a
  aparecer só logo depois de a pessoa fechar os olhos.
- **RF06**: deslocamento do centro do rosto de pelo menos 0,25 largura de rosto entre quadros na mesma orientação,
  ou troca de frente para perfil (ou o contrário) mantida por 2 quadros seguidos. O detector alterna entre frente e
  perfil no mesmo rosto parado; sem essa confirmação, a alternância viraria movimento falso.
- **RF09**: classifica todos os comportamentos da seção 4: olhos abertos e fechados (RF05), movimento da cabeça
  (RF06), movimento corporal, mudança de posição (RN05), ausência de movimento, maior atividade motora (RN04) e
  visibilidade insuficiente.
- **RF10**: as regras RN01, RN02, RN03, RN06 e RN07 estão implementadas e testadas com dados simulados, e o teste de
  ponta a ponta mostra os olhos chegando até "vigília" e "possível sono" no banco. **Continua Parcial:** nas duas
  gravações do estudo de caso, com a câmera infravermelha a distância, o rosto aparece em menos de 10% do tempo e os
  olhos são determinados em 0,1% dos quadros. Por isso o estado fica 100% "indeterminado", como mandam RN06 e RN07.
  Ver `material-documentacao.md`.
- **RF15**: imagem escura ou sem contraste, e "sem presença" (nenhum rosto nem movimento por 30 min), que cobre
  pessoa fora do enquadramento ou câmera virada.

## Requisitos não funcionais

| ID | Requisito | Como é atendido hoje | Situação | Falta |
|---|---|---|---|---|
| RNF01 | Utilizar exclusivamente câmera | Só existe captura de imagem (`captura/video.py`); áudio removido | Implementado | — |
| RNF02 | Processamento automático por visão computacional | OpenCV: diferença entre quadros (`deteccao/movimento.py`), análise da imagem (`deteccao/visibilidade.py`) e cascatas Haar de rosto e olhos (`deteccao/rosto.py`, `deteccao/olhos.py`) | Implementado | — |
| RNF03 | Funcionar sem interação constante do usuário | `analisar` roda sozinho até o fim da gravação ou até Ctrl+C na câmera | Implementado | — |
| RNF04 | Precisão temporal de no mínimo um segundo | Horários gravados em segundos (`isoformat(timespec="seconds")`); horário de cada quadro lido do carimbo da câmera (`captura/carimbo.py`: `ler_carimbo()`, `RelogioCarimbo`) | Implementado | `test_captura.py`, `test_pipeline.py` |
| RNF05 | Preservar integridade dos registros | Chaves estrangeiras com `PRAGMA foreign_keys = ON` | Implementado | — |
| RNF06 | Proteção contra acessos não autorizados | Banco local em `dados/`, fora do git; nada vai para a nuvem | Estrutura pronta | Controle de acesso e criptografia |
| RNF07 | Distinguir observações visuais de estados estimados | Tabelas `comportamentos` e `estados`; dashboard com faixas "Observado" e "Estimado" | Implementado | — |
| RNF08 | Monitoramento contínuo durante a sessão | Tolerância a falhas de leitura (`config.FALHAS_LEITURA_MAX`); 1 quadro analisado por segundo | Implementado | Medir com câmera ao vivo por uma noite inteira |
| RNF09 | Registrar classificações não confiáveis | Coluna `confiavel` na tabela `estados`; "indeterminado" é sempre não confiável; coluna "Confiável" no CSV e tempo não confiável em "Estados estimados" (`dashboard/app.py`) | Implementado | `test_dashboard.py` |
| RNF10 | Permitir exclusão de dados da sessão | `excluir_sessao()` com CASCADE; botão no dashboard com confirmação | Implementado | — |
| RNF11 | Autorização LGPD para tratamento de imagens | `analisar` só roda com `--autorizado`, que confirma o termo assinado | Parcial | Termo de consentimento em si |
| RNF12 | Informar que resultados não são diagnóstico | `config.AVISO_NAO_DIAGNOSTICO` no dashboard, na linha de comando e no relatório CSV | Implementado | — |

## Regras de negócio

| ID | Regra | Onde se aplica | Situação |
|---|---|---|---|
| RN01 | Olhos abertos contínuos → evidência de vigília | `classificacao/estados.py`, `deteccao/olhos.py` | Implementado (nas gravações, olhos quase nunca determinados) |
| RN02 | Olhos fechados contínuos + outros comportamentos → possível sono | `classificacao/estados.py`, `deteccao/olhos.py` | Implementado (nas gravações, olhos quase nunca determinados) |
| RN03 | Ausência prolongada de movimentos → contribui, mas não basta isoladamente | `classificacao/estados.py`, `classificacao/periodos.py` | Implementado |
| RN04 | Movimentos frequentes → períodos de maior atividade motora | `classificacao/comportamentos.py` | Implementado |
| RN05 | Mudanças bruscas de posição → eventos de movimentação corporal | `deteccao/movimento.py`, `classificacao/comportamentos.py` | Implementado |
| RN06 | Olhos não visíveis → não classificar como fechados | `deteccao/olhos.py`, `tipos.EstadoOlhos`, `classificacao/estados.py` | Implementado |
| RN07 | Informações visuais insuficientes → estado indeterminado | `classificacao/estados.py`, `classificacao/periodos.py` | Implementado |
| RN08 | Classificações associadas a horário ou intervalo | Colunas `inicio` e `fim`; tipos com início e fim | Implementado |
| RN09 | Classificações baseadas exclusivamente em informações visuais | Toda entrada vem de quadros da câmera | Implementado |
| RN10 | Não apresentar estimativas como identificação clínica | `config.ESTADOS` sem estágios clínicos; o banco recusa outros estados | Implementado |

## Itens fora do escopo

| Item | Onde aparece | Motivo |
|---|---|---|
| Identificação das fases do sono (N1, N2, N3, REM) | Cronograma, descrição de cargo | Fases são definidas por sinais elétricos (EEG, EOG, EMG) que a câmera não mede. |
| Diagnóstico de distúrbios do sono | Pesquisa de viabilidade | Fora do escopo do estudo de caso. Exige validação clínica (RNF12). |
| Treinamento de IA própria | Pesquisa de viabilidade | Exige dataset, rotulagem e validação incompatíveis com o prazo. |
| Captura e análise de áudio | Lista anterior de requisitos | Removido na nova lista. O sistema usa exclusivamente câmera (RNF01, RN09). |
| Classificação de postura | Levantamento de tecnologia | Não está na lista. Depende de teste com pessoa coberta. |

## Decisões pendentes

| Decisão | Requisitos afetados | Responsáveis |
|---|---|---|
| Regra de "olhos fechados": rever com um gabarito se a exigência de olhos vistos antes pode ser relaxada sem violar a RN06 | RF05, RF10, RN02, RN06 | Pesquisadores, analistas |
| Confirmar os estados provisórios: vigília, possível sono, indeterminado | RF10 | Pesquisadores, gestão |
| Confirmar os parâmetros provisórios de `config.py` (limiares e tempos das regras, incluindo `CONTRASTE_MINIMO_ROSTO`) com um gabarito das gravações | RF03 a RF07, RF09 a RF11, RN01 a RN05 | Pesquisadores, analistas |
| Descarte do vídeo bruto e prazo de guarda | RNF06, RNF11 | Pesquisadores, gestão |
| Controle de acesso e criptografia | RNF06 | Analistas, gestão |
| Termo de consentimento LGPD | RNF11 | Pesquisadores, gestão |

## Resumo da situação

| Situação | RF | RNF | RN |
|---|---|---|---|
| Implementado | 14 (RF01 a RF09, RF11 a RF15) | 10 (RNF01 a RNF05, RNF07 a RNF10, RNF12) | 10 (RN01 a RN10) |
| Parcial | 1 (RF10) | 1 (RNF11) | — |
| Estrutura pronta | — | 1 (RNF06) | — |
| **Total** | **15** | **12** | **10** |

## Histórico de alterações

| Data | Versão | Alteração | Responsável |
|---|---|---|---|
| 08/10/2026 | 1.0 | Criação da matriz junto com a estrutura inicial do software | Analistas |
| 15/10/2026 | 2.0 | Reescrita completa para alinhar à nova lista de requisitos (estudo de caso). Removido áudio. Adicionados módulos classificacao/ e novas detecções. Banco reescrito com tabelas separadas. | Analistas |
| 23/11/2026 | 2.1 | RF02 implementado: `capturar_quadros()` com OpenCV, entrega quadros a `fps_analise` e redimensiona para `RESOLUCAO_ANALISE`. Testes com vídeo sintético. | Pedro Motta |
| 23/11/2026 | 3.0 | Sistema de ponta a ponta: correção do RF02 (perda de quadros e tolerância a falhas), detecção de movimento e visibilidade, classificação com as regras RN01 a RN07, pipeline com o comando `analisar`, dashboard e análise das duas gravações do estudo de caso. RF03 a RF06 aguardam decisão sobre o detector de rosto. | Gabriel Correa |
| 23/11/2026 | 3.1 | RF03 a RF06 implementados com as cascatas Haar do OpenCV 4.x (dependência limitada a `<5`): presença, rosto, estado dos olhos com regra conservadora (RN06) e movimento da cabeça, ligados no pipeline. RF09 e RF15 passam a Implementado. RF10 continua Parcial: nas gravações do estudo de caso, os olhos são determinados em 0,1% dos quadros. | Gabriel Correa |
| 24/11/2026 | 3.2 | Correções: o dashboard não quebra mais com sessão sem registros nem com sessão sem encerramento (RF14), e a duração do resumo deixou de arredondar as horas para cima. Uma análise que falha ao abrir a fonte não deixa mais sessão vazia no banco (RF01). A linha de comando mostra uma mensagem curta para fonte inválida e para `--inicio` fora do formato. RF13 e RF14 passam a ter teste automatizado (`test_dashboard.py`). | Gabriel Correa |
| 24/11/2026 | 3.3 | RNF04: o horário de cada quadro passa a vir do carimbo de data e hora que a câmera grava na imagem (`captura/carimbo.py`). Corrige o relógio do vídeo (cerca de 2,5% adiantado) e as interrupções da gravação 1. Interrupções da gravação viram visibilidade insuficiente (RF15) e interrompem a ausência de movimento (RN07, `classificacao/`); trechos gravados duas vezes são ignorados. `--inicio` vira reserva para câmeras sem carimbo. | Gabriel Correa |
| 25/11/2026 | 3.4 | RF14: o CSV do relatório começa com um resumo (sessão, início, fim, duração, movimentos, mudanças de posição, movimentos da cabeça, tempo sem movimento e tempo em cada estado estimado), depois da linha do aviso (RNF12). RNF09: coluna "Confiável" nos estados estimados do CSV e tempo não confiável na seção "Estados estimados". | Gabriel Correa |
