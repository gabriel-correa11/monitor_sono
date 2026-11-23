# Implementar captura de vídeo (RF02)

- **Data e hora:** 2026-11-23 11:50
- **Pedido por:** Pedro Motta (analista)
- **Ferramenta:** Claude
- **Requisitos relacionados:** RF02, RNF01, RNF08

## Pedido e contexto
Finalizar a parte de captura, que estava com a assinatura definida e `NotImplementedError`.

## O que foi feito
- **Alterado:** `src/monitor_sono/captura/video.py` — implementada `capturar_quadros()`: abre a fonte com `cv2.VideoCapture`, lê continuamente, entrega (segundo, quadro) a cada `1/fps_analise` s, redimensiona para `config.RESOLUCAO_ANALISE` e libera a câmera ao terminar.
- **Criado:** `tests/test_captura.py` — 4 testes com vídeo sintético gerado em código e relógio simulado.
- **Alterado:** `docs/rastreabilidade.md` — RF02 como Implementado, resumo e histórico.
- **Excluído:** nada.

## Decisões e motivos
- Assinatura original mantida (contrato com os outros módulos).
- `segundo` é o tempo desde o início da captura.
- Quadro entregue em BGR; a conversão para escala de cinza fica com a detecção.
- A mensagem de erro não mostra a fonte, que pode conter usuário e senha (RTSP).
- Nenhuma dependência nova.

## Verificação
`pytest`: 8 passaram (4 novos + 4 existentes).

## Pendências
- Testar com câmera real e com a gravação da equipe, localmente, por quem tem acesso à pasta restrita.
- Em ambientes sem tela (Codespaces, CI), o `opencv-python` exige o pacote de sistema `libgl1`. A equipe pode avaliar o `opencv-python-headless`.