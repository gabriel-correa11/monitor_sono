# Material técnico para a equipe de documentação

Material de apoio preparado pelos analistas. A redação final (README, estudo de caso, apresentação) fica com os
documentadores. Situação detalhada de cada requisito: [`rastreabilidade.md`](rastreabilidade.md).

## Como usar o sistema

Requisito: Python 3.11 ou mais novo.

**Instalação (uma vez):**

```powershell
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -e .
```

**Analisar uma gravação ou a câmera:**

```powershell
python -m monitor_sono analisar "caminho\da\gravacao.mp4" --autorizado
python -m monitor_sono analisar "caminho\da\gravacao.mp4" --inicio "2026-11-20 22:30" --autorizado
python -m monitor_sono analisar 0 --autorizado     # câmera ao vivo; Ctrl+C encerra a sessão
```

- `--autorizado` confirma que a pessoa monitorada assinou o termo de consentimento (RNF11). Sem ele, o comando
  não roda.
- `--inicio` é a data e hora real em que a gravação começou. Sem ele, usa o momento da análise.
- O resultado é gravado no banco local `dados/monitor_sono.db`, que nunca vai para o repositório.

**Abrir o dashboard:**

```powershell
streamlit run src/monitor_sono/dashboard/app.py
```

**Rodar os testes:** `pytest` (67 testes).

## Como o sistema funciona

```
câmera ou gravação → captura → detecção → classificação → banco → dashboard
```

1. **Captura (RF02):** pega 1 quadro por segundo da câmera ou da gravação.
2. **Detecção (RF07, RF15):** compara cada quadro com o anterior e mede quanto da imagem mudou. Acima de 0,5% é
   movimento; acima de 10% é mudança brusca de posição. Imagem escura ou sem contraste é aviso de visibilidade.
   Quando mais da metade da imagem muda de uma vez, é troca de iluminação, não movimento.
   **Rosto, olhos, cabeça e presença (RF03 a RF06):** procura o rosto com as cascatas Haar do OpenCV 4.x (de frente
   e de perfil), avalia os olhos só em rosto de frente, grande e nítido, compara a posição do rosto entre quadros
   e considera a pessoa presente se houve rosto ou movimento nos últimos 30 min.
3. **Classificação (RF09, RF10, RF11):** junta os movimentos em períodos, identifica ausência de movimento,
   períodos de maior atividade motora (RN04) e estima os estados aplicando as regras de negócio.
4. **Banco (RF08, RF12):** grava o que foi **observado** (comportamentos) separado do que foi **estimado**
   (estados), com horário em segundos.
5. **Dashboard (RF13, RF14):** resumo, linha do tempo com faixas "Observado" e "Estimado", avisos, relatório em
   CSV e exclusão da sessão.

## Resultados do estudo de caso

Duas gravações feitas pela câmera da equipe, analisadas localmente. Nenhuma imagem foi extraída ou salva.

| | Gravação 1 | Gravação 2 |
|---|---|---|
| Início (horário da câmera) | 09/11/2026 03:22:48 | 10/11/2026 04:23:21 |
| Duração | 2 h 39 min | 3 h 52 min |
| Câmera | 2304x1296, cerca de 5 quadros por segundo | 2304x1296, 5 quadros por segundo |
| Quadros analisados (1 por segundo) | 9.485 | 13.948 |
| Períodos de movimento | 291 (42 min no total) | 428 (60 min no total) |
| Mudanças bruscas de posição | 347 | 394 |
| Períodos de maior atividade motora (RN04) | 218 (38 min no total) | 323 (55 min no total) |
| Ausência de movimento (períodos de 1 min ou mais) | 16 períodos, 76 min (48% da sessão) | 29 períodos, 98 min (42% da sessão) |
| Maior período sem movimento | 20 min | 15 min |
| Ausências prolongadas (5 min ou mais, RN03) | 6 | 8 |
| Quadros com rosto (RF04) | 402 (4,2%): 145 de frente, 257 de perfil | 1.372 (9,8%): 1.322 de frente, 50 de perfil |
| Rostos aproveitáveis para os olhos (de frente, 120 px ou mais, nítidos) | 41 (0,4%) | 156 (1,1%) |
| Olhos determinados (RF05) | 7 (0,1%): 7 abertos, 0 fechados | 8 (0,1%): 8 abertos, 0 fechados |
| Movimentos da cabeça (RF06) | 11 | 11 |
| Avisos de visibilidade insuficiente (inclui "sem presença") | 0 | 0 |
| Estado estimado | 100% indeterminado | 100% indeterminado |
| Tempo de processamento | 7,4 min | 10,3 min |

Os números de movimento mudaram em relação à análise anterior, que foi feita em partes, em outro ambiente e com
OpenCV 5; os desta tabela, com OpenCV 4.x, são os oficiais. Segundos com movimento e trocas de iluminação não foram
medidos nesta análise. O início das sessões foi informado como 03:22 e 04:23, porque o comando aceita hora e minuto.

**Leitura dos resultados:**

- O sistema registrou períodos de movimento em cerca de um quarto do tempo e ausência de movimento em 42% a 48% do
  tempo, com períodos de até 20 minutos parado.
- **Conclusão do estudo de caso:** com esta câmera infravermelha a distância, o sistema mede movimento com
  confiança, mas o rosto aparece em menos de 10% do tempo e os olhos são determinados em só 0,1% dos quadros. Por
  isso o estado fica **indeterminado** o tempo todo, como mandam RN06 e RN07: sem evidência dos olhos, a falta de
  movimento sozinha não basta para estimar sono (RN03). O sistema não "chuta" um estado sem evidência.
- Prováveis motivos de os olhos quase não aparecerem: a pessoa fica de lado ou coberta (na gravação 1, a maioria dos
  rostos achados é de perfil); com o rosto em cerca de 150 px, o olho fica com 25 a 30 px, perto do limite do
  detector; a cascata de olhos foi treinada com fotos comuns, não com imagem infravermelha; e a regra de "olhos
  fechados" é conservadora (exige olhos vistos abertos antes, no mesmo acompanhamento do rosto).
- O número de mudanças bruscas de posição (mais de 300 por gravação) parece alto para uma noite de sono. É provável
  que o limite de 10% da imagem esteja baixo para esta câmera. O valor é provisório e precisa ser confirmado com um
  gabarito.
- O processamento continua rápido: cerca de 3 minutos por hora de gravação, já com a detecção de rosto e olhos.

## Parâmetros usados (todos provisórios)

Ficam em `src/monitor_sono/config.py`.

| Parâmetro | Valor | Para quê |
|---|---|---|
| Quadros analisados por segundo | 1 | Captura (RF02) |
| Diferença mínima de intensidade de um pixel | 20 (de 0 a 255) | Movimento (RF07) |
| Fração da imagem para movimento | 0,5% | Movimento (RF07) |
| Fração da imagem para mudança brusca de posição | 10% | RN05 |
| Fração da imagem para troca de iluminação | 50% | Não confundir luz com movimento |
| Brilho mínimo | 30 (de 0 a 255) | Visibilidade (RF15) |
| Menor ausência de movimento registrada | 1 min | RF11 |
| Ausência prolongada | 5 min | RN03 |
| Movimentos frequentes | 10 segundos com movimento em 1 min | RN04 |
| Período contínuo de olhos abertos ou fechados | 1 min | RN01, RN02 |
| Largura da cópia em que o rosto é procurado | 960 px | Rosto (RF04) |
| Menor rosto procurado | 60 px da imagem original | Rosto (RF04) |
| Menor rosto em que os olhos são avaliados | 120 px da imagem original | Olhos (RF05, RN06) |
| Contraste mínimo do rosto (desvio padrão) | 20 | Olhos (RF05, RN06) |
| Quadros seguidos sem olhos para "fechados" | 5 | Olhos (RF05, RN06) |
| Quadros sem rosto tolerados no acompanhamento | 3 | Olhos e cabeça (RF05, RF06) |
| Deslocamento do rosto para movimento da cabeça | 0,25 da largura do rosto | Cabeça (RF06) |
| Razão máxima de tamanho entre dois rostos | 1,5 | Cabeça (RF06) |
| Quadros na nova orientação (frente/perfil) | 2 | Cabeça (RF06) |
| Janela de presença (rosto ou movimento) | 30 min | Presença (RF03), visibilidade (RF15) |

## Limitações

- **A gravação 1 tem um buraco:** a câmera marca 3h51 de noite (03:22:48 a 07:14:21), mas o vídeo tem 2h39. Cerca
  de 1h15 não foi gravada, provavelmente perto dos 5 minutos de vídeo, onde o sistema detectou uma troca brusca de
  toda a imagem. Os horários da gravação 1 depois desse ponto ficam adiantados em relação à câmera. Além disso, os
  dois arquivos marcam o tempo cerca de 2,5% mais devagar que o relógio da câmera.
- **Rosto e olhos quase não são observados com esta câmera:** o rosto aparece em menos de 10% do tempo e os olhos
  em 0,1% dos quadros (pessoa de lado ou coberta, olho com 25 a 30 px, cascata não treinada para infravermelho).
  Sem olhos, o estado fica sempre indeterminado (RN06, RN07). O sistema mede movimento com confiança, mas não estima
  vigília nem possível sono nestas gravações.
- **Regra de "olhos fechados" conservadora:** "fechados" só vale num rosto acompanhado em que os olhos já foram vistos
  abertos. Se o acompanhamento do rosto reinicia (o rosto sumiu por mais de 3 quadros), "fechados" só volta depois de
  os olhos serem vistos abertos de novo. Por isso o "possível sono" tende a aparecer só logo depois de a pessoa
  fechar os olhos.
- **Parâmetros sem validação:** foram calibrados olhando só a distribuição dos dados, sem gabarito do que realmente
  aconteceu nas gravações.
- **Movimento da imagem inteira:** qualquer mudança na cena conta, inclusive de outra pessoa ou objeto no quarto.
- **Visibilidade:** detecta imagem escura ou sem contraste e "sem presença" (nenhum rosto nem movimento por 30 min).
  Uma pessoa parada e coberta por mais de 30 min também seria marcada como "sem presença".

## O que ficou pronto e o que é trabalho futuro

**Pronto:** captura de câmera e gravação, detecção de movimento e mudança de posição, detecção de rosto, estado dos
olhos, movimento da cabeça e presença, avisos de visibilidade,
períodos de movimento e de ausência, maior atividade motora, regras de estimativa de estado, banco, comando de
análise, dashboard com relatório e exclusão de sessão, aviso de não diagnóstico.

**Trabalho futuro:**

1. Medir a distribuição do contraste dos rostos detectados para recalibrar `CONTRASTE_MINIMO_ROSTO`.
2. Rever a regra de "olhos fechados" com um gabarito, para ver se a exigência de olhos vistos antes pode ser
   relaxada sem violar a RN06.
3. Testar a câmera mais perto do rosto, para o olho ter mais pixels.
4. Gabarito das gravações, feito por uma pessoa assistindo e anotando os horários, para validar os parâmetros.
5. Termo de consentimento, controle de acesso e criptografia (RNF06, RNF11).
6. Teste com a câmera ao vivo por uma noite inteira (RNF08).
