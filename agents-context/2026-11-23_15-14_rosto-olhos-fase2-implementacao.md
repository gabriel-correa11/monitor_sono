# Rosto e olhos — fase 2: implementação

- **Data e hora:** 2026-11-23 15:14
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF02, RF03, RF04, RF05, RF06, RF15, RN06, RN07

## Pedido e contexto
Implementar o plano aprovado na fase 1 (`agents-context/2026-11-23_15-04_rosto-olhos-fase1-plano.md`),
com os valores provisórios propostos (120 px, folga de 3 quadros, 5 quadros, 30 min, 0,25, 1,5) e as
mudanças de assinatura. Ajustes pedidos na aprovação:
1. RF06: troca de frente para perfil (ou o contrário) só conta como movimento se a nova orientação se
   mantiver por pelo menos 2 quadros seguidos (parâmetro em `config.py`).
2. Olhos fechados: manter a regra e registrar a limitação do reinício do acompanhamento na
   rastreabilidade e no material de documentação (fica para a fase 4, que mexe nesses documentos).
3. Incluir `agents-context/2026-11-23_14-57_commit-docs-horario-gravacao.md` no primeiro commit.

## O que foi feito
- **Alterado:** `requirements.txt`, `pyproject.toml` — `opencv-python>=4.9,<5`. `.venv` reinstalado com
  `pip install -e .` (instalou OpenCV 4.14.0, com `cv2.CascadeClassifier` e as cascatas Haar).
- **Alterado:** `src/monitor_sono/captura/video.py` — parâmetro `resolucao` (padrão
  `config.RESOLUCAO_ANALISE`; `None` = quadro original). Quem chama sem o parâmetro não muda.
- **Alterado:** `src/monitor_sono/config.py` — só parâmetros novos: `RESOLUCAO_ROSTO`,
  `FATOR_ESCALA_ROSTO`, `VIZINHOS_ROSTO`, `TAMANHO_BUSCA_ROSTO`, `TAMANHO_MINIMO_HAAR`,
  `MARGEM_BUSCA_ROSTO`, `DISTANCIA_MESMO_ROSTO`, `TAMANHO_MINIMO_ROSTO`, `CONTRASTE_MINIMO_ROSTO`,
  `LARGURA_RECORTE_OLHOS`, `VIZINHOS_OLHOS`, `FATOR_ESCALA_OLHOS`, `TAMANHO_MINIMO_OLHO`,
  `ALTURA_REGIAO_OLHOS`, `FOLGA_ROSTO_QUADROS`, `QUADROS_OLHOS_FECHADOS`, `DESLOCAMENTO_CABECA`,
  `RAZAO_TAMANHO_ROSTO_MAX`, `QUADROS_NOVA_ORIENTACAO` e `JANELA_PRESENCA_S`. Os que são limiares estão
  marcados como PROVISÓRIO.
- **Alterado:** `src/monitor_sono/tipos.py` — tipo novo `Rosto`; comentário de `Visibilidade.motivo`
  passa a citar o valor novo `"sem_presenca"`.
- **Alterado:** `src/monitor_sono/deteccao/rosto.py` (RF04) — `detectar_rosto(quadro, anterior)`
  devolve `Rosto | None`; cascatas frontal e de perfil (dos dois lados), equalização de histograma,
  busca em 960 px de largura, janela ao redor do rosto anterior; `cascata()`, `cinza()`, `centro()`,
  `razao_tamanho()` e `mesmo_rosto()`.
- **Alterado:** `src/monitor_sono/deteccao/olhos.py` (RF05, RN06) — `detectar_estado_olhos(quadro, rosto,
  segundo)` devolve `EstadoOlhos` e nunca "fechados"; `rosto_adequado_para_olhos()`, `contar_olhos()` e
  `AcompanhamentoOlhos`, que só diz "fechados" com rosto de frente, grande e nítido, acompanhado, com
  olhos já vistos e sumidos por 5 quadros seguidos.
- **Alterado:** `src/monitor_sono/deteccao/cabeca.py` (RF06) — `detectar_movimento_cabeca(rosto_anterior,
  rosto_atual)` e `AcompanhamentoCabeca`, com a troca de orientação confirmada por
  `QUADROS_NOVA_ORIENTACAO` (ajuste 1).
- **Alterado:** `src/monitor_sono/deteccao/presenca.py` (RF03) — `detectar_presenca(segundo,
  ultima_evidencia)` e `AcompanhamentoPresenca`.
- **Alterado:** `src/monitor_sono/deteccao/visibilidade.py` (RF15) — `considerar_presenca()`: sem presença,
  visibilidade insuficiente com motivo `"sem_presenca"`.
- **Alterado:** `src/monitor_sono/pipeline.py` — captura com `resolucao=None`; movimento e visibilidade
  numa cópia em `RESOLUCAO_ANALISE` (mesmo resultado de antes); rosto, olhos, cabeça e presença a cada
  quadro; olhos passados a `classificar_comportamentos()` e `estimar_estados()`; intervalos de
  `movimento_cabeca` registrados; `Resultado` com `quadros_com_rosto` e `quadros_olhos_determinaveis`.
- **Alterado:** `tests/test_captura.py` (1 teste novo), `tests/test_deteccao.py` (28 testes novos),
  `tests/test_pipeline.py` (1 teste novo de ponta a ponta com detector simulado).
- **Excluído:** nada.

## Decisões e motivos
- Dois parâmetros que não estavam no plano: `DISTANCIA_MESMO_ROSTO` (1 largura de rosto), que define o
  "perto da última posição" do item 4 do plano, e os de busca da cascata de olhos (escala, tamanho
  mínimo, fração de cima do rosto), para não deixar números no código.
- Rosto pequeno com olho achado também fica "indeterminado", e não "abertos": a cascata em rosto pequeno
  confunde narinas e sombras com olhos.
- O deslocamento da cabeça só é comparado entre detecções na mesma orientação, porque a caixa de frente e
  a de perfil não são comparáveis. Isso evita que a alternância do detector vire movimento.
- Quadros em que não dá para avaliar os olhos (perfil, rosto pequeno ou borrado, rosto sumido dentro da
  folga) não zeram nem avançam a contagem de quadros sem olhos.
- Nenhum arquivo de `classificacao/` foi alterado.

## Verificação
`pytest`: 67 passaram (eram 36).

## Pendências
- Fase 3: análise das gravações.
- Registrar a limitação do reinício do acompanhamento dos olhos nos documentos (fase 4).
- O `__main__.py` não está na lista de arquivos desta tarefa, então o terminal ainda não mostra
  `quadros_com_rosto` e `quadros_olhos_determinaveis`. Fica como sugestão para a equipe.
