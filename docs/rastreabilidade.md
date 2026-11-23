# Matriz de Rastreabilidade de Requisitos

**Projeto:** Sistema de Monitoramento do Sono por Câmera e Inteligência Artificial
**Disciplina:** Tópicos Especiais em Engenharia de Software
**Versão:** 3.0 (sistema funcionando de ponta a ponta — estudo de caso)

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
| RF02 | Capturar imagens em tempo real pela câmera | `captura/video.py` | `capturar_quadros()` | Implementado | `test_captura.py` (7 testes) |
| RF03 | Identificar presença de pessoa na área monitorada | `deteccao/presenca.py` | `detectar_presenca()` | Aguardando decisão | — |
| RF04 | Detectar a região facial do indivíduo | `deteccao/rosto.py` | `detectar_rosto()` | Aguardando decisão | — |
| RF05 | Identificar estado dos olhos (abertos, fechados, indeterminado) | `deteccao/olhos.py` | `detectar_estado_olhos()` | Aguardando decisão | — |
| RF06 | Detectar movimentos da cabeça | `deteccao/cabeca.py` | `detectar_movimento_cabeca()` | Aguardando decisão | — |
| RF07 | Identificar movimentos corporais e mudanças de posição | `deteccao/movimento.py` | `analisar_movimento()`, `detectar_movimento_corporal()`, `detectar_mudanca_posicao()` | Implementado | `test_deteccao.py` |
| RF08 | Registrar movimentos com horários | `registro/banco.py`, `pipeline.py` | `registrar_comportamento()`, tabela `comportamentos` | Implementado | `test_registro.py`, `test_pipeline.py` |
| RF09 | Classificar comportamentos conforme critérios | `classificacao/comportamentos.py` | `classificar_comportamentos()`, `periodos_maior_atividade()` | Parcial | `test_classificacao.py` |
| RF10 | Estimar estados de sono a partir de características visuais | `classificacao/estados.py` | `estimar_estados()` | Parcial | `test_classificacao.py` |
| RF11 | Identificar períodos de movimentação e ausência | `classificacao/periodos.py` | `identificar_periodos()` | Implementado | `test_classificacao.py` |
| RF12 | Armazenar resultados das classificações | `registro/banco.py`, `pipeline.py` | `registrar_estado()`, tabela `estados` | Implementado | `test_registro.py`, `test_pipeline.py` |
| RF13 | Apresentar histórico cronológico de comportamentos e estados | `dashboard/app.py` | seção "Linha do tempo" (Observado e Estimado) | Implementado | Verificação manual do dashboard |
| RF14 | Gerar relatório da sessão | `dashboard/app.py` | "Resumo da sessão", "Relatório" (CSV) | Implementado | Verificação manual do dashboard |
| RF15 | Sinalizar visibilidade insuficiente da câmera | `deteccao/visibilidade.py`, `dashboard/app.py` | `avaliar_visibilidade()`, seção "Avisos" | Parcial | `test_deteccao.py`, `test_classificacao.py` |

### Observações

- **RF01**: a sessão pode vir da câmera ao vivo ou de uma gravação feita pela câmera (estudo de caso), pelo comando
  `python -m monitor_sono analisar <fonte> --autorizado`. Com gravação, o tempo vem do próprio vídeo; a data e hora
  real de início pode ser informada com `--inicio`.
- **RF02**: corrigida a perda de quadros com câmera a 5 fps (a versão anterior entregava 3.000 quadros por hora em
  vez de 3.600) e acrescentada a tolerância a falhas de leitura (RNF08).
- **RF03 a RF06**: o OpenCV 5, usado no projeto, não traz mais detector de rosto e olhos pronto (as cascatas Haar
  saíram da biblioteca principal). Implementar exige decidir um modelo ou uma biblioteca nova (ver decisões
  pendentes). As funções continuam com `NotImplementedError` explicando o motivo.
- **RF09**: classifica movimento corporal, mudança de posição (RN05), ausência de movimento, maior atividade motora
  (RN04) e visibilidade insuficiente. Olhos abertos/fechados e movimento da cabeça dependem de RF05 e RF06.
- **RF10**: as regras RN01, RN02, RN03, RN06 e RN07 estão implementadas e testadas com dados simulados. Sem a
  detecção de olhos (RF05), o resultado nas gravações reais é sempre "indeterminado", como mandam RN03 e RN06.
- **RF15**: detecta imagem escura ou sem contraste. Pessoa fora do enquadramento depende de RF03 e RF04.

## Requisitos não funcionais

| ID | Requisito | Como é atendido hoje | Situação | Falta |
|---|---|---|---|---|
| RNF01 | Utilizar exclusivamente câmera | Só existe captura de imagem (`captura/video.py`); áudio removido | Implementado | — |
| RNF02 | Processamento automático por visão computacional | OpenCV: diferença entre quadros (`deteccao/movimento.py`) e análise da imagem (`deteccao/visibilidade.py`) | Implementado | Detecção de rosto e olhos |
| RNF03 | Funcionar sem interação constante do usuário | `analisar` roda sozinho até o fim da gravação ou até Ctrl+C na câmera | Implementado | — |
| RNF04 | Precisão temporal de no mínimo um segundo | Horários gravados em segundos (`isoformat(timespec="seconds")`) | Implementado | — |
| RNF05 | Preservar integridade dos registros | Chaves estrangeiras com `PRAGMA foreign_keys = ON` | Implementado | — |
| RNF06 | Proteção contra acessos não autorizados | Banco local em `dados/`, fora do git; nada vai para a nuvem | Estrutura pronta | Controle de acesso e criptografia |
| RNF07 | Distinguir observações visuais de estados estimados | Tabelas `comportamentos` e `estados`; dashboard com faixas "Observado" e "Estimado" | Implementado | — |
| RNF08 | Monitoramento contínuo durante a sessão | Tolerância a falhas de leitura (`config.FALHAS_LEITURA_MAX`); 1 quadro analisado por segundo | Implementado | Medir com câmera ao vivo por uma noite inteira |
| RNF09 | Registrar classificações não confiáveis | Coluna `confiavel` na tabela `estados`; "indeterminado" é sempre não confiável | Implementado | — |
| RNF10 | Permitir exclusão de dados da sessão | `excluir_sessao()` com CASCADE; botão no dashboard com confirmação | Implementado | — |
| RNF11 | Autorização LGPD para tratamento de imagens | `analisar` só roda com `--autorizado`, que confirma o termo assinado | Parcial | Termo de consentimento em si |
| RNF12 | Informar que resultados não são diagnóstico | `config.AVISO_NAO_DIAGNOSTICO` no dashboard, na linha de comando e no relatório CSV | Implementado | — |

## Regras de negócio

| ID | Regra | Onde se aplica | Situação |
|---|---|---|---|
| RN01 | Olhos abertos contínuos → evidência de vigília | `classificacao/estados.py` | Implementado (depende de RF05 para dados reais) |
| RN02 | Olhos fechados contínuos + outros comportamentos → possível sono | `classificacao/estados.py` | Implementado (depende de RF05 para dados reais) |
| RN03 | Ausência prolongada de movimentos → contribui, mas não basta isoladamente | `classificacao/estados.py`, `classificacao/periodos.py` | Implementado |
| RN04 | Movimentos frequentes → períodos de maior atividade motora | `classificacao/comportamentos.py` | Implementado |
| RN05 | Mudanças bruscas de posição → eventos de movimentação corporal | `deteccao/movimento.py`, `classificacao/comportamentos.py` | Implementado |
| RN06 | Olhos não visíveis → não classificar como fechados | `tipos.EstadoOlhos`, `classificacao/estados.py` | Implementado na classificação; detecção pendente (RF05) |
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
| Detector de rosto e olhos: modelo YuNet do OpenCV (licença MIT, sem pacote novo, mas exige baixar o arquivo do modelo) ou MediaPipe (Apache 2.0, pacote novo) | RF03 a RF06, RF10 | Analistas |
| Confirmar os estados provisórios: vigília, possível sono, indeterminado | RF10 | Pesquisadores, gestão |
| Confirmar os parâmetros provisórios de `config.py` (limiares e tempos das regras) com um gabarito das gravações | RF07, RF09 a RF11, RN01 a RN05 | Pesquisadores, analistas |
| Data e hora real de início das gravações do estudo de caso (`--inicio`) | RF08, RNF04 | Pesquisadores |
| Descarte do vídeo bruto e prazo de guarda | RNF06, RNF11 | Pesquisadores, gestão |
| Controle de acesso e criptografia | RNF06 | Analistas, gestão |
| Termo de consentimento LGPD | RNF11 | Pesquisadores, gestão |

## Resumo da situação

| Situação | RF | RNF | RN |
|---|---|---|---|
| Implementado | 8 (RF01, RF02, RF07, RF08, RF11, RF12, RF13, RF14) | 10 (RNF01 a RNF05, RNF07 a RNF10, RNF12) | 10 (RN01 a RN10) |
| Parcial | 3 (RF09, RF10, RF15) | 1 (RNF11) | — |
| Estrutura pronta | — | 1 (RNF06) | — |
| Aguardando decisão | 4 (RF03 a RF06) | — | — |
| **Total** | **15** | **12** | **10** |

## Histórico de alterações

| Data | Versão | Alteração | Responsável |
|---|---|---|---|
| 08/10/2026 | 1.0 | Criação da matriz junto com a estrutura inicial do software | Analistas |
| 15/10/2026 | 2.0 | Reescrita completa para alinhar à nova lista de requisitos (estudo de caso). Removido áudio. Adicionados módulos classificacao/ e novas detecções. Banco reescrito com tabelas separadas. | Analistas |
| 23/11/2026 | 2.1 | RF02 implementado: `capturar_quadros()` com OpenCV, entrega quadros a `fps_analise` e redimensiona para `RESOLUCAO_ANALISE`. Testes com vídeo sintético. | Pedro Motta |
| 23/11/2026 | 3.0 | Sistema de ponta a ponta: correção do RF02 (perda de quadros e tolerância a falhas), detecção de movimento e visibilidade, classificação com as regras RN01 a RN07, pipeline com o comando `analisar`, dashboard e análise das duas gravações do estudo de caso. RF03 a RF06 aguardam decisão sobre o detector de rosto. | Gabriel Correa |
