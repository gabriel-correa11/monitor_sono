# Rosto e olhos — fase 1: plano

- **Data e hora:** 2026-11-23 15:04
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF03, RF04, RF05, RF06, RF15, RN06, RN07 (plano)

## Pedido e contexto
Tarefa "finalizar o código (rosto e olhos) e preparar a revisão da equipe", em fases com paradas para
aprovação. Decisão de quem pediu: usar OpenCV 4.x, que traz as cascatas Haar. Fase 0: commitar
`docs/rastreabilidade.md` e `docs/material-documentacao.md` se estivessem modificados. Fase 1: plano
para versão do OpenCV, resolução, desempenho, regra de "olhos fechados", presença, cabeça e
visibilidade.

## O que foi feito
- Fase 0: nada a fazer. Os dois arquivos já estavam no commit `9e3da4c` e não aparecem modificados.
- `opencv-python==4.11.0.86` instalado **numa pasta temporária fora do projeto** (o `.venv` não foi
  alterado). Com ela na frente do caminho do Python: `cv2.CascadeClassifier` existe, e
  `cv2.data.haarcascades` tem `haarcascade_frontalface_default.xml`, `haarcascade_profileface.xml` e
  `haarcascade_eye.xml`, entre outras. `pytest`: 36 passaram.
- Custo das cascatas medido com **imagens sintéticas** (ruído desfocado gerado em código), por um
  script temporário fora do repositório. Com fator de escala 1,2 e rosto mínimo de 120 px na imagem
  original: 960×540 com frontal e perfil dos dois lados, 38 ms por quadro; só frontal, 19 ms; janela
  ao redor do último rosto, 7 ms; olhos num recorte de 240 px, 4 ms.
- **Criado:** `agents-context/2026-11-23_15-04_rosto-olhos-fase1-plano.md` — este registro
- **Alterado:** nada
- **Excluído:** nada

## Decisões e motivos
Nenhuma. As propostas foram apresentadas para aprovação.

## Verificação
`pytest` com OpenCV 4.11 numa pasta temporária: 36 passaram.

## Pendências
- Aprovação do plano.
- `agents-context/2026-11-23_14-57_commit-docs-horario-gravacao.md`, da tarefa anterior, continua
  fora do git, à espera da decisão de quem pediu.
