# Matriz de Rastreabilidade de Requisitos

**Projeto:** Sistema de Monitoramento do Sono por Câmera, Áudio e Inteligência Artificial
**Disciplina:** Tópicos Especiais em Engenharia de Software
**Versão:** 1.0 (estrutura inicial do software)

## Para que serve este documento

A matriz liga cada requisito ao ponto do código que o atende, à entrega em que ele deve ficar pronto e
à sua situação atual. Ela tem três usos:

1. **Durante o desenvolvimento**: mostra o que falta e evita código sem requisito (regra da equipe).
2. **Para a documentação**: é a fonte para a documentação técnica (22/10) e para o documento de
   requisitos finalizado (05/11).
3. **No fim do projeto**: é a base da conferência de requisitos atendidos (19/11), que aparece na
   apresentação.

**Base:** lista de requisitos da *Pesquisa de Viabilidade* (RF01 a RF11, RNF01 a RNF08). A *Pesquisa
Bibliográfica* tem uma lista anterior com numeração diferente (RF01 a RF09). Ela serve como
fundamentação, mas **os IDs válidos são os desta matriz**.

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

| ID | Requisito | Arquivo | Função / elemento | Entrega | Situação | Teste |
|---|---|---|---|---|---|---|
| RF01 | Permitir iniciar uma sessão de monitoramento | `sessao/__init__.py` | `iniciar_sessao()` | 08/10 | Estrutura pronta | Indireto, via `banco.criar_sessao` |
| RF02 | Permitir encerrar uma sessão de monitoramento | `sessao/__init__.py` | `encerrar_sessao()` | 08/10 | Estrutura pronta | Indireto, via `banco.finalizar_sessao` |
| RF03 | Receber imagens da câmera durante a sessão | `captura/video.py` | `ler_quadros()` | 15/10 | Assinatura definida | — |
| RF04 | Receber áudio durante o monitoramento, quando disponível | `captura/audio.py` | `ler_audio()` | 15/10 | Assinatura definida | — |
| RF05 | Identificar movimentos durante a sessão | `deteccao/movimento.py` | `detectar_movimentos()` | 22/10 | Assinatura definida | — |
| RF06 | Identificar eventos sonoros definidos no escopo | `deteccao/som.py` | `detectar_eventos_sonoros()` | após 22/10 | Aguardando decisão | — |
| RF07 | Registrar eventos com data e horário | `registro/banco.py` | `registrar_evento()`, tabela `eventos` | 08/10 | Implementado | `test_sessao_e_evento`, `test_rejeita_tipo_fora_dos_requisitos` |
| RF08 | Apresentar uma linha do tempo dos eventos | `dashboard/app.py` | seção "Linha do tempo" | 15/10 | Assinatura definida | — |
| RF09 | Apresentar um resumo dos resultados da sessão | `dashboard/app.py` | seção "Resumo da sessão" | 15/10 | Assinatura definida | — |
| RF10 | Permitir consultar sessões anteriores | `registro/banco.py`, `dashboard/app.py`, `__main__.py` | `listar_sessoes()`, `eventos_da_sessao()`, comando `sessoes` | 08/10 (dados), 15/10 (tela) | Estrutura pronta | `test_sessao_e_evento` |
| RF11 | Permitir visualizar ou gerar relatório dos resultados | `dashboard/app.py` | seção "Relatório" | 29/10 | Assinatura definida | — |

### Observações

- **RF01 e RF02**: hoje uma sessão é aberta e fechada com data e hora. Ainda falta decidir se a sessão
  corresponde a uma gravação ao vivo ou à importação de um arquivo já gravado. A estrutura atende os
  dois casos, porque o campo `origem` aceita tanto câmera quanto arquivo.
- **RF06**: a função existe só para reservar o lugar no código. Nenhum tipo de som é classificado até a
  definição de 22/10.
- **RF07**: o banco **recusa** tipos de evento que não estão nos requisitos. Hoje só aceita `movimento`
  (RF05) e `som` (RF06). Isso impede, por exemplo, registrar "fase do sono", que está fora do escopo.

## Requisitos não funcionais

| ID | Requisito | Como é atendido hoje | Situação | Falta |
|---|---|---|---|---|
| RNF01 | Privacidade: dados acessíveis só a usuários autorizados | `dados/` fora do git; tudo fica no computador local | Estrutura pronta | Controle de acesso (pendência) |
| RNF02 | Segurança: proteção na transmissão e no armazenamento | Banco SQLite local, sem nuvem, sem transmissão pela rede | Estrutura pronta | Criptografia (pendência) |
| RNF03 | Minimização: avaliar a necessidade de guardar vídeo/áudio completos | — | Aguardando decisão | Definir se o vídeo bruto é descartado após a análise |
| RNF04 | Retenção: definir por quanto tempo os dados são mantidos | — | Aguardando decisão | Definir o prazo de guarda |
| RNF05 | Desempenho: processamento em tempo adequado | `config.py`: 1 quadro por segundo, resolução 320x240 | Estrutura pronta | Medir com a gravação real |
| RNF06 | Usabilidade: resultados simples e compreensíveis | `dashboard/app.py`: seções separadas por assunto | Estrutura pronta | Testes dos apresentadores (12/11) |
| RNF07 | Limitação clínica: resultados não são apresentados como diagnóstico | `config.AVISO_NAO_DIAGNOSTICO`, exibido no dashboard e na linha de comando | Implementado | — |
| RNF08 | Disponibilidade: sistema operacional durante a sessão | — | Não iniciado | Depende da decisão sobre sessão ao vivo ou importação |

## Itens fora do escopo

Itens que aparecem em documentos do projeto mas **não serão implementados**, com o motivo. Registrar
isso evita que alguém cobre essas funções depois.

| Item | Onde aparece | Motivo |
|---|---|---|
| Identificação das fases do sono (N1, N2, N3, REM) | Cronograma, descrição do cargo de analista | Não está em nenhum requisito. As fases são definidas por sinais elétricos (EEG, EOG, EMG) que a câmera não mede, e N2, N3 e REM são fisicamente parados. |
| Diagnóstico de distúrbios do sono | Pesquisa de viabilidade | Fora do escopo do MVP. Exige validação clínica (RNF07). |
| Treinamento de IA própria | Pesquisa de viabilidade | Exige dataset, rotulagem e validação incompatíveis com o prazo. |
| Tempo total de sono, eficiência, latência e despertares estimados | Levantamento de tecnologia | Não estão na lista de requisitos. Só entram se forem aprovados como novos requisitos. |
| Classificação de postura | Levantamento de tecnologia | Não está na lista. Depende de teste piloto com a pessoa coberta. |

## Decisões pendentes

| Decisão | Requisitos afetados | Responsáveis | Prazo |
|---|---|---|---|
| Quais eventos sonoros entram | RF06 | Analistas, pesquisadores, gestão | 22/10 |
| Sessão ao vivo ou importação de gravação | RF01, RF02, RNF08 | Analistas, gestão | Antes de 15/10 |
| Limiar e duração mínima de movimento | RF05 | Analistas | 22/10 |
| Descarte do vídeo bruto e prazo de guarda | RNF03, RNF04 | Pesquisadores, gestão | A definir |
| Controle de acesso e criptografia | RNF01, RNF02 | Analistas, gestão | A definir |
| Equipamento de captura | RF03, RF04 | Analistas, pesquisadores | A confirmar |

## Resumo da situação

| Situação | RF | RNF |
|---|---|---|
| Implementado | 1 (RF07) | 1 (RNF07) |
| Estrutura pronta | 3 (RF01, RF02, RF10) | 4 (RNF01, RNF02, RNF05, RNF06) |
| Assinatura definida | 6 (RF03, RF04, RF05, RF08, RF09, RF11) | — |
| Aguardando decisão | 1 (RF06) | 2 (RNF03, RNF04) |
| Não iniciado | — | 1 (RNF08) |
| **Total** | **11** | **8** |

## Histórico de alterações

| Data | Versão | Alteração | Responsável |
|---|---|---|---|
| 08/10/2026 | 1.0 | Criação da matriz junto com a estrutura inicial do software | Analistas |
