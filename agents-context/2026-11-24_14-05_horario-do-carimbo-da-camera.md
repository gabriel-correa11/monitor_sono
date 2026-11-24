# Horário de cada quadro lido do carimbo da câmera

- **Data e hora:** 2026-11-24 14:05
- **Pedido por:** dono do repositório
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF02, RF15, RNF04, RN07, RN08

## Pedido e contexto
"test with the video", depois "use the hour on the video, its better", e por fim "make sure the project is ready
... finish for me, do not put on the git yet". A equipe autorizou ignorar as regras do `AGENTS.md` por causa do
prazo (inclusive ler quadros das gravações e mexer em `dados/`).

Ao comparar o carimbo de data e hora gravado pela câmera com o tempo do vídeo, a IA encontrou três problemas:
- o vídeo corre cerca de 2,5% mais rápido que o relógio;
- a gravação 1 tem 78 min sem gravação (03:50:57 a 05:05:08) e outros 3 trechos de cerca de 1 min;
- as duas gravações têm trechos de alguns segundos gravados duas vezes (o carimbo volta, ex.: 03:33:13 → 03:32:02).

Resultado: a gravação 1 aparecia com 2 h 39 min em vez de 3 h 52 min, e o buraco contava como ausência de movimento.

## O que foi feito
- **Criado:** `src/monitor_sono/captura/carimbo.py` — `ler_carimbo()` lê os 14 dígitos do carimbo só com OpenCV
  (componentes conectados + comparação com modelos), e `RelogioCarimbo` converte o tempo do vídeo em tempo real:
  corrige o relógio, aceita um salto para a frente só depois de confirmado pelo quadro seguinte e ignora trechos
  repetidos.
- **Criado:** `src/monitor_sono/captura/digitos_carimbo.npz` — modelos dos dígitos 0 a 9 (média de 336 dígitos
  de 24 carimbos lidos a olho). Contém só o desenho dos dígitos, nenhuma outra parte da imagem.
- **Alterado:** `src/monitor_sono/pipeline.py` — usa o carimbo; depois de uma interrupção, não compara com o quadro
  anterior e reinicia os acompanhamentos de rosto, olhos, cabeça e presença. A sessão só é criada no banco depois
  da captura, então o `except` que excluía a sessão vazia saiu.
- **Alterado:** `src/monitor_sono/classificacao/periodos.py` — uma interrupção da gravação quebra a ausência de
  movimento (RN07).
- **Alterado:** `src/monitor_sono/classificacao/comportamentos.py` — `lacunas_gravacao()`: interrupção da gravação
  vira `visibilidade_insuficiente` (RF15).
- **Alterado:** `src/monitor_sono/config.py` — parâmetros do carimbo e `LACUNA_GRAVACAO_S` (10 s).
- **Alterado:** `src/monitor_sono/__main__.py` — mostra a origem dos horários, as interrupções e os quadros
  ignorados; `--inicio` vira reserva para câmeras sem carimbo.
- **Alterado:** `pyproject.toml` — o `.npz` entra como dado do pacote.
- **Alterado:** `.gitignore` — `.pytest-tmp/`.
- **Criado:** `tests/conftest.py` — desenha carimbos sintéticos a partir dos modelos (sem imagem de gravação).
- **Alterado:** `tests/test_captura.py` (+12), `tests/test_classificacao.py` (+3), `tests/test_pipeline.py` (+1).
- **Alterado:** `README.md`, `docs/material-documentacao.md` (uso, funcionamento, tabela de resultados, leitura,
  limitações) e `docs/rastreabilidade.md` (RNF04 e versão 3.3).
- **Alterado (fora do git):** `dados/monitor_sono.db` — as sessões 3 e 4 (horários do relógio do vídeo) foram
  substituídas pelas sessões 5 e 6, analisadas com o carimbo. Cópia de segurança do banco anterior:
  `dados/monitor_sono.backup-2026-11-24.db`.

## Decisões e motivos
- Leitura do carimbo com OpenCV, sem OCR externo (Tesseract, EasyOCR): o carimbo tem fonte, cor e posição fixas,
  e assim não entra nenhuma dependência nova.
- O carimbo tem prioridade sobre o `--inicio`, que só vale quando nenhum carimbo é lido.
- O trecho repetido é ignorado, e não contado duas vezes, para o tempo nunca voltar.
- A origem da sessão só fica fixa depois de dois carimbos coerentes seguidos, para que um primeiro carimbo mal lido não desloque a sessão inteira nem faça descartar os quadros seguintes.
- Interrupção = mais de 10 s sem quadros. Com 1 quadro por segundo, o intervalo normal é de cerca de 1 s.

## Verificação
- Leitura do carimbo em 1.200 quadros que não foram usados para montar os modelos: 1.200 lidos, nenhum ilegível.
  Os desvios em relação ao esperado vieram da própria câmera (interrupções e trechos repetidos), conferidos a olho
  em 11 quadros. Leitura: cerca de 6 ms por quadro.
- Análise completa das duas gravações. Início e fim batem com o carimbo: 03:22:48 a 07:14:41 e 04:23:20 a
  08:10:34. As interrupções detectadas na gravação 1 são as mesmas vistas a olho.
- `pytest`: 97 passaram.
- Dashboard com o executor de testes do Streamlit no banco real: sessões 5 e 6 sem erro, com duração de
  3 h 52 min e 3 h 47 min. O servidor `streamlit run` sobe e responde.

## Pendências
- Commit e push na branch `correcoes-dashboard-pipeline` a pedido do dono do repositório, entrando no PR #3.
  Falta a revisão da equipe antes do merge.
- Os modelos dos dígitos valem para esta câmera. Outra câmera precisa de modelos novos, ou a leitura não acontece
  e o sistema volta ao relógio do vídeo.
