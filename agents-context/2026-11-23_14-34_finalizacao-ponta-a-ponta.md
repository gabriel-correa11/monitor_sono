# Finalização: sistema de ponta a ponta e análise das gravações

- **Data e hora:** 2026-11-23 14:34
- **Pedido por:** Gabriel Correa (analista)
- **Ferramenta:** Claude
- **Requisitos relacionados:** RF01, RF02, RF07 a RF15, RNF01 a RNF12, RN01 a RN10

## Pedido e contexto
Deixar o sistema funcionando de ponta a ponta para a apresentação: corrigir a captura, implementar detecção,
classificação, pipeline e dashboard, e analisar as duas gravações do estudo de caso. O Gabriel autorizou rodar o
código sobre as gravações localmente, no computador dele, sem abrir, salvar ou descrever imagens e sem copiar os
vídeos. Só números agregados saíram da análise.

## O que foi feito
- **Alterado:** `src/monitor_sono/captura/video.py` — corrigida a perda de quadros (`proximo += intervalo`); com
  gravação, o tempo vem do próprio vídeo; tolerância a falhas de leitura (RNF08); quadros não usados só são lidos
  com `grab()`.
- **Criado:** `src/monitor_sono/tipos.py` — contratos entre módulos (dataclasses).
- **Alterado:** `src/monitor_sono/config.py` — parâmetros de movimento, visibilidade e regras (marcados como
  PROVISÓRIO), lista de estados, `maior_atividade_motora` em `COMPORTAMENTOS` (RN04).
- **Alterado:** `src/monitor_sono/deteccao/movimento.py` e `visibilidade.py` — implementados (RF07, RF15).
- **Alterado:** `src/monitor_sono/deteccao/rosto.py`, `olhos.py`, `cabeca.py`, `presenca.py` — mensagem do
  `NotImplementedError` explica por que não foram implementados.
- **Alterado:** `src/monitor_sono/classificacao/periodos.py`, `comportamentos.py`, `estados.py` — implementados
  com as regras RN01 a RN07.
- **Criado:** `src/monitor_sono/pipeline.py` — liga captura, detecção, classificação e registro.
- **Alterado:** `src/monitor_sono/__main__.py` — comando `analisar <fonte> [--inicio] --autorizado`.
- **Alterado:** `src/monitor_sono/registro/banco.py` — recusa estados fora de `config.ESTADOS`.
- **Alterado:** `src/monitor_sono/dashboard/app.py` — resumo, linha do tempo (Observado e Estimado), estados,
  avisos de visibilidade, relatório CSV, exclusão de sessão.
- **Criado:** `tests/test_deteccao.py`, `tests/test_classificacao.py`, `tests/test_pipeline.py`.
- **Alterado:** `tests/test_captura.py` (câmera simulada, 5 fps, falhas, tempo do vídeo) e `tests/test_registro.py`
  (nomes de estados válidos e teste de estado fora do escopo).
- **Alterado:** `AGENTS.md` — `tipos.py` e `pipeline.py` na arquitetura e nas regras de importação.
- **Alterado:** `docs/rastreabilidade.md` — versão 3.0.
- **Criado:** `docs/material-documentacao.md` — material técnico para a equipe de documentação.
- **Gerado fora do git:** `dados/monitor_sono.db` com as duas sessões do estudo de caso.
- **Excluído:** nada.

## Decisões e motivos
- **RF03 a RF06 não implementados:** o OpenCV 5 instalado no projeto não traz mais as cascatas Haar de rosto e
  olhos. As alternativas exigem um modelo baixado à parte ou uma biblioteca nova, o que é decisão da equipe.
- **Estados provisórios** `vigilia`, `possivel_sono` e `indeterminado`, tirados de RN01, RN02 e RN07, porque a
  lista de requisitos não traz a tabela de estados.
- **Parâmetros provisórios** calibrados com uma amostra das gravações (brilho e fração da imagem alterada entre
  quadros). Precisam de gabarito para serem confirmados.
- **Troca de iluminação não conta como movimento:** quando mais da metade da imagem muda de uma vez, é luz acesa
  ou apagada.
- **Trechos sem informação visual interrompem a ausência de movimento** (RN07): não se afirma que a pessoa ficou
  parada quando a cena não podia ser observada.
- **Sem detecção de olhos, o estado fica sempre indeterminado**, seguindo RN02, RN03 e RN06: a ausência de
  movimento sozinha não basta para estimar sono.
- **RNF11:** o comando `analisar` só roda com `--autorizado`, para lembrar que o termo de consentimento é
  obrigatório antes de tratar imagens.
- **Análise das gravações em partes:** cada comando no ambiente usado tinha limite de 3 minutos, então cada vídeo
  foi processado em trechos com as mesmas funções de detecção e classificação, e o banco foi gerado ao fim. No
  computador da equipe, o comando `analisar` processa a gravação inteira de uma vez.
- **Horário das sessões do estudo de caso:** a data e hora real de início das gravações não é conhecida; as sessões
  foram gravadas com o horário da análise. Para corrigir, basta rodar de novo com `--inicio`.

## Verificação
`pytest`: 36 passaram. Dashboard verificado com dados de exemplo (navegador sem tela) e com as sessões reais no
banco do projeto.

## Pendências
- Decidir o detector de rosto e olhos (RF03 a RF06).
- Confirmar estados e parâmetros provisórios com um gabarito das gravações.
- Informar a data e hora real de início das gravações.
- Termo de consentimento (RNF11), controle de acesso e criptografia (RNF06).
