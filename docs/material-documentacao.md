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

**Rodar os testes:** `pytest` (36 testes).

## Como o sistema funciona

```
câmera ou gravação → captura → detecção → classificação → banco → dashboard
```

1. **Captura (RF02):** pega 1 quadro por segundo da câmera ou da gravação.
2. **Detecção (RF07, RF15):** compara cada quadro com o anterior e mede quanto da imagem mudou. Acima de 0,5% é
   movimento; acima de 10% é mudança brusca de posição. Imagem escura ou sem contraste é aviso de visibilidade.
   Quando mais da metade da imagem muda de uma vez, é troca de iluminação, não movimento.
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
| Quadros analisados (1 por segundo) | 9.486 | 13.949 |
| Segundos com movimento | 1.020 (10,8%) | 1.280 (9,2%) |
| Períodos de movimento | 227 | 512 |
| Mudanças bruscas de posição | 236 | 222 |
| Períodos de maior atividade motora (RN04) | 103 (26 min no total) | 286 (17 min no total) |
| Ausência de movimento (períodos de 1 min ou mais) | 16 períodos, 84 min (53% da sessão) | 32 períodos, 111 min (48% da sessão) |
| Maior período sem movimento | 21 min | 22 min |
| Ausências prolongadas (5 min ou mais, RN03) | 6 | 8 |
| Avisos de visibilidade insuficiente | 0 | 0 |
| Trocas de iluminação detectadas | 1 | 24 |
| Estado estimado | 100% indeterminado | 100% indeterminado |
| Tempo de processamento | cerca de 3 min | cerca de 3,5 min |

**Leitura dos resultados:**

- O sistema registrou movimento em cerca de 10% do tempo e ausência de movimento em cerca de metade do tempo, com
  períodos de até 22 minutos parado.
- O estado ficou **indeterminado** o tempo todo porque esta versão ainda não detecta os olhos. Pelas regras RN02,
  RN03 e RN06, a falta de movimento sozinha não basta para estimar sono. Esse comportamento é o esperado e mostra
  que o sistema não "chuta" um estado sem evidência.
- O número de mudanças bruscas de posição (mais de 200 por gravação) parece alto para uma noite de sono. É provável
  que o limite de 10% da imagem esteja baixo para esta câmera. O valor é provisório e precisa ser confirmado com um
  gabarito.
- As 24 trocas de iluminação da gravação 2 merecem verificação: podem ser luz do ambiente ou o ajuste automático do
  infravermelho da câmera.
- O processamento é rápido: cerca de 1 minuto por hora de gravação.

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

## Limitações

- **A gravação 1 tem um buraco:** a câmera marca 3h51 de noite (03:22:48 a 07:14:21), mas o vídeo tem 2h39. Cerca
  de 1h15 não foi gravada, provavelmente perto dos 5 minutos de vídeo, onde o sistema detectou uma troca brusca de
  toda a imagem. Os horários da gravação 1 depois desse ponto ficam adiantados em relação à câmera. Além disso, os
  dois arquivos marcam o tempo cerca de 2,5% mais devagar que o relógio da câmera.
- **Rosto, olhos, cabeça e presença (RF03 a RF06) não foram implementados.** O OpenCV 5, usado no projeto, não
  traz mais detector de rosto pronto. Implementar exige um modelo à parte ou uma biblioteca nova, o que depende de
  decisão da equipe.
- **Sem olhos, não há estimativa de sono:** o estado fica sempre indeterminado.
- **Parâmetros sem validação:** foram calibrados olhando só a distribuição dos dados, sem gabarito do que realmente
  aconteceu nas gravações.
- **Movimento da imagem inteira:** qualquer mudança na cena conta, inclusive de outra pessoa ou objeto no quarto.
- **Visibilidade:** detecta imagem escura ou sem contraste, mas não pessoa fora do enquadramento.

## O que ficou pronto e o que é trabalho futuro

**Pronto:** captura de câmera e gravação, detecção de movimento e mudança de posição, avisos de visibilidade,
períodos de movimento e de ausência, maior atividade motora, regras de estimativa de estado, banco, comando de
análise, dashboard com relatório e exclusão de sessão, aviso de não diagnóstico.

**Trabalho futuro:**

1. Detector de rosto e olhos (RF03 a RF06), que libera a estimativa de vigília e de possível sono.
2. Gabarito das gravações, feito por uma pessoa assistindo e anotando os horários, para validar os parâmetros.
3. Termo de consentimento, controle de acesso e criptografia (RNF06, RNF11).
4. Teste com a câmera ao vivo por uma noite inteira (RNF08).
