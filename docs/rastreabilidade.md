# Matriz de Rastreabilidade de Requisitos

**Projeto:** Sistema de Monitoramento do Sono por Câmera e Inteligência Artificial
**Disciplina:** Tópicos Especiais em Engenharia de Software
**Versão:** 2.0 (alinhamento à nova lista de requisitos — estudo de caso)

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
| Implementado | Funciona e tem teste automatizado |
| Estrutura pronta | Funciona parcialmente ou sem teste; base pronta para completar |
| Assinatura definida | Arquivo e função criados, sem implementação (`NotImplementedError`) |
| Aguardando decisão | Depende de uma decisão da equipe antes de ser implementado |
| Não iniciado | Ainda não tem nenhum ponto no código |

Caminhos relativos a `src/monitor_sono/`.

## Requisitos funcionais

| ID | Requisito | Arquivo | Função / elemento | Situação | Teste |
|---|---|---|---|---|---|
| RF01 | Iniciar e encerrar sessão de monitoramento | `sessao/__init__.py` | `iniciar_sessao()`, `encerrar_sessao()` | Estrutura pronta | Indireto, via `banco.criar_sessao` |
| RF02 | Capturar imagens em tempo real pela câmera | `captura/video.py` | `capturar_quadros()` | Assinatura definida | — |
| RF03 | Identificar presença de pessoa na área monitorada | `deteccao/presenca.py` | `detectar_presenca()` | Assinatura definida | — |
| RF04 | Detectar a região facial do indivíduo | `deteccao/rosto.py` | `detectar_rosto()` | Assinatura definida | — |
| RF05 | Identificar estado dos olhos (abertos, fechados, indeterminado) | `deteccao/olhos.py` | `detectar_estado_olhos()` | Assinatura definida | — |
| RF06 | Detectar movimentos da cabeça | `deteccao/cabeca.py` | `detectar_movimento_cabeca()` | Assinatura definida | — |
| RF07 | Identificar movimentos corporais e mudanças de posição | `deteccao/movimento.py` | `detectar_movimento_corporal()`, `detectar_mudanca_posicao()` | Assinatura definida | — |
| RF08 | Registrar movimentos com horários | `registro/banco.py` | `registrar_comportamento()`, tabela `comportamentos` | Implementado | `test_sessao_e_comportamento` |
| RF09 | Classificar comportamentos conforme critérios | `classificacao/comportamentos.py` | `classificar_comportamentos()` | Assinatura definida | — |
| RF10 | Estimar estados de sono a partir de características visuais | `classificacao/estados.py` | `estimar_estado()` | Assinatura definida | — |
| RF11 | Identificar períodos de movimentação e ausência | `classificacao/periodos.py` | `identificar_periodos()` | Assinatura definida | — |
| RF12 | Armazenar resultados das classificações | `registro/banco.py` | `registrar_estado()`, tabela `estados` | Implementado | `test_registrar_estado` |
| RF13 | Apresentar histórico cronológico de comportamentos e estados | `dashboard/app.py` | seções "Resumo", "Comportamentos", "Estados" | Assinatura definida | — |
| RF14 | Gerar relatório da sessão | `dashboard/app.py` | seções "Sessões anteriores", "Relatório" | Assinatura definida | — |
| RF15 | Sinalizar visibilidade insuficiente da câmera | `deteccao/visibilidade.py`, `dashboard/app.py` | `verificar_visibilidade()`, seção "Visibilidade" | Assinatura definida | — |

### Observações

- **RF01**: a sessão é ao vivo (câmera em tempo real). O campo `origem` foi removido porque não há mais
  importação de gravações.
- **RF05**: três estados possíveis — abertos, fechados, indeterminado (RN06).
- **RF08/RF12**: o banco separa comportamentos observados (tabela `comportamentos`) e estados estimados
  (tabela `estados`) para atender o RNF07.
- **RF09/RF10/RF11**: dependem de limiares e critérios que a equipe ainda não definiu (RN01–RN05).
  Assinatura pronta, implementação aguarda.

## Requisitos não funcionais

| ID | Requisito | Como é atendido hoje | Situação | Falta |
|---|---|---|---|---|
| RNF01 | Utilizar exclusivamente câmera | Módulo `captura/` só tem `video.py`; áudio removido | Estrutura pronta | — |
| RNF02 | Processamento automático por visão computacional | Módulos `deteccao/` e `classificacao/` | Assinatura definida | Implementar detecções |
| RNF03 | Funcionar sem interação constante do usuário | — | Não iniciado | Depende do pipeline de monitoramento |
| RNF04 | Precisão temporal de no mínimo um segundo | `banco.py`: `isoformat(timespec="seconds")` | Implementado | — |
| RNF05 | Preservar integridade dos registros | Chaves estrangeiras com `PRAGMA foreign_keys = ON` | Implementado | — |
| RNF06 | Proteção contra acessos não autorizados | `dados/` fora do git; tudo fica no computador local | Estrutura pronta | Controle de acesso (pendência) |
| RNF07 | Distinguir observações visuais de estados estimados | Tabelas separadas: `comportamentos` e `estados`; dashboard com seções distintas | Estrutura pronta | — |
| RNF08 | Monitoramento contínuo durante a sessão | `config.py`: 1 qps, 320×240 | Estrutura pronta | Medir com câmera real |
| RNF09 | Registrar classificações não confiáveis | `banco.py`: coluna `confiavel` na tabela `estados` | Implementado | — |
| RNF10 | Permitir exclusão de dados da sessão | `banco.py`: `excluir_sessao()` com CASCADE | Implementado | — |
| RNF11 | Autorização LGPD para tratamento de imagens | — | Não iniciado | Termo de consentimento |
| RNF12 | Informar que resultados não são diagnóstico | `config.AVISO_NAO_DIAGNOSTICO`, exibido no dashboard e na linha de comando | Implementado | — |

## Regras de negócio

| ID | Regra | Onde se aplica | Situação |
|---|---|---|---|
| RN01 | Olhos abertos contínuos → evidência de vigília | `classificacao/estados.py` | Assinatura definida |
| RN02 | Olhos fechados contínuos + outros comportamentos → possível sono | `classificacao/estados.py` | Assinatura definida |
| RN03 | Ausência prolongada de movimentos → contribui para possível sono, mas não basta isoladamente | `classificacao/estados.py`, `classificacao/periodos.py` | Assinatura definida |
| RN04 | Movimentos frequentes → períodos de maior atividade motora | `classificacao/periodos.py` | Assinatura definida |
| RN05 | Mudanças bruscas de posição → eventos de movimentação corporal | `classificacao/periodos.py` | Assinatura definida |
| RN06 | Olhos não visíveis → não classificar como fechados | `deteccao/olhos.py` | Assinatura definida |
| RN07 | Informações visuais insuficientes → estado indeterminado | `deteccao/visibilidade.py`, `classificacao/estados.py` | Assinatura definida |
| RN08 | Classificações associadas a horário ou intervalo | `registro/banco.py`: colunas `inicio` e `fim` | Implementado |
| RN09 | Classificações baseadas exclusivamente em informações visuais da câmera | Arquitetura: sem módulo de áudio | Estrutura pronta |
| RN10 | Não apresentar estimativas como identificação clínica | `config.AVISO_NAO_DIAGNOSTICO`, `dashboard/app.py` | Implementado |

## Itens fora do escopo

| Item | Onde aparece | Motivo |
|---|---|---|
| Identificação das fases do sono (N1, N2, N3, REM) | Cronograma, descrição de cargo | Fases são definidas por sinais elétricos (EEG, EOG, EMG) que a câmera não mede. |
| Diagnóstico de distúrbios do sono | Pesquisa de viabilidade | Fora do escopo do estudo de caso. Exige validação clínica (RNF12). |
| Treinamento de IA própria | Pesquisa de viabilidade | Exige dataset, rotulagem e validação incompatíveis com o prazo. |
| Captura e análise de áudio | Lista anterior de requisitos | Removido na nova lista. O sistema usa exclusivamente câmera (RNF01, RN09). |
| Classificação de postura | Levantamento de tecnologia | Não está na lista. Depende de teste com pessoa coberta. |

## Decisões pendentes

| Decisão | Requisitos afetados | Responsáveis | Prazo |
|---|---|---|---|
| Limiares e critérios de classificação de comportamentos | RF09, RN01–RN05 | Analistas, pesquisadores | A definir |
| Estados comportamentais válidos (vigília, possível sono, indeterminado?) | RF10, RN07 | Pesquisadores, gestão | A definir |
| Módulo pipeline que liga captura → detecção → classificação → registro | RF02, RF03–RF07, RF08 | Analistas, gestão | A definir |
| Descarte do vídeo bruto e prazo de guarda | RNF06, RNF11 | Pesquisadores, gestão | A definir |
| Controle de acesso e criptografia | RNF06 | Analistas, gestão | A definir |
| Termo de consentimento LGPD | RNF11 | Pesquisadores, gestão | A definir |

## Resumo da situação

| Situação | RF | RNF | RN |
|---|---|---|---|
| Implementado | 2 (RF08, RF12) | 5 (RNF04, RNF05, RNF09, RNF10, RNF12) | 2 (RN08, RN10) |
| Estrutura pronta | 1 (RF01) | 4 (RNF01, RNF06, RNF07, RNF08) | 1 (RN09) |
| Assinatura definida | 10 (RF02–RF07, RF09–RF11, RF13–RF15) | 1 (RNF02) | 7 (RN01–RN07) |
| Não iniciado | — | 2 (RNF03, RNF11) | — |
| **Total** | **15** | **12** | **10** |

## Histórico de alterações

| Data | Versão | Alteração | Responsável |
|---|---|---|---|
| 08/10/2026 | 1.0 | Criação da matriz junto com a estrutura inicial do software | Analistas |
| 15/10/2026 | 2.0 | Reescrita completa para alinhar à nova lista de requisitos (estudo de caso). Removido áudio. Adicionados módulos classificacao/ e novas detecções. Banco reescrito com tabelas separadas. | Analistas |
