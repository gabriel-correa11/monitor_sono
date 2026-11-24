@echo off
chcp 65001 >nul
setlocal EnableExtensions
title Monitor de Sono
cd /d "%~dp0"

rem Monitor de Sono: clique duplo para abrir o menu.
rem Arrastar um ou mais vídeos para cima deste arquivo analisa direto.
rem Na primeira vez, cria o ambiente .venv e instala as bibliotecas (precisa de internet).

set "PYV=%~dp0.venv\Scripts\python.exe"

call :preparar || goto :falha

if not "%~1"=="" (
    call :consentimento || goto :fim
    for %%F in (%*) do call :analisar "%%~F"
    goto :perguntar_dashboard
)

:menu
cls
echo ==================================================
echo   Monitor de Sono
echo ==================================================
echo.
echo   1 - Abrir o dashboard (ver os resultados)
echo   2 - Analisar uma gravação de vídeo
echo   3 - Rodar os testes automáticos
echo   4 - Sair
echo.
choice /c 1234 /n /m "Aperte o número da opção: "
if errorlevel 255 goto :fim
if errorlevel 4 goto :fim
if errorlevel 3 goto :testes
if errorlevel 2 goto :escolher
if errorlevel 1 goto :dashboard
goto :fim


:escolher
call :consentimento || goto :menu
echo.
echo Escolha a gravação na janela que abriu. Dá para escolher mais de uma.
set "ESCOLHEU="
for /f "usebackq delims=" %%F in (`powershell -NoProfile -STA -Command "[Console]::OutputEncoding = [Text.Encoding]::UTF8; Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.OpenFileDialog; $d.Title = 'Escolha a gravação'; $d.Filter = 'Vídeos|*.mp4;*.avi;*.mkv;*.mov|Todos os arquivos|*.*'; $d.Multiselect = $true; $d.InitialDirectory = [Environment]::GetFolderPath('MyVideos'); if ($d.ShowDialog() -eq 'OK') { $d.FileNames }"`) do (
    set "ESCOLHEU=1"
    call :analisar "%%F"
)
if not defined ESCOLHEU (
    echo Nenhum arquivo escolhido.
    pause
    goto :menu
)
goto :perguntar_dashboard


:perguntar_dashboard
echo.
choice /c SN /m "Abrir o dashboard agora para ver o resultado"
if errorlevel 2 goto :menu
goto :dashboard


:dashboard
cls
echo Abrindo o dashboard no navegador: http://localhost:8501
echo.
echo Deixe esta janela aberta enquanto usa o dashboard.
echo Para fechar: aperte Ctrl+C aqui ou feche a janela.
echo.
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://localhost:8501'"
"%PYV%" -m streamlit run src\monitor_sono\dashboard\app.py --server.headless true --browser.gatherUsageStats false
goto :fim


:testes
cls
"%PYV%" -c "import pytest" >nul 2>&1 || (
    echo Instalando o pytest...
    "%PYV%" -m pip install --quiet pytest || goto :falha
)
"%PYV%" -m pytest --basetemp .pytest-tmp
echo.
pause
goto :menu


rem ---------- Sub-rotinas ----------

:consentimento
echo.
echo RNF11: a pessoa gravada precisa ter assinado o termo de consentimento.
choice /c SN /m "A pessoa gravada assinou o termo de consentimento"
if errorlevel 2 (
    echo Sem o termo assinado, a gravação não pode ser analisada.
    pause
    exit /b 1
)
exit /b 0


:analisar
echo.
echo ==================================================
echo   Analisando: %~nx1
echo   Pode levar vários minutos. Não feche esta janela.
echo ==================================================
"%PYV%" -m monitor_sono analisar "%~1" --autorizado
if errorlevel 1 echo A análise de "%~nx1" falhou. Veja a mensagem acima.
exit /b 0


:preparar
if exist "%PYV%" (
    "%PYV%" -c "import monitor_sono, cv2, streamlit, altair" >nul 2>&1 && exit /b 0
    goto :instalar
)
call :achar_python || exit /b 1
echo Criando o ambiente do projeto. Só acontece na primeira vez.
%PYBASE% -m venv .venv || exit /b 1
:instalar
echo Instalando as bibliotecas do projeto. Só acontece na primeira vez e precisa de internet.
"%PYV%" -m pip install --quiet --upgrade pip
"%PYV%" -m pip install --quiet -e . || exit /b 1
exit /b 0


:achar_python
set "PYBASE="
py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1 && set "PYBASE=py -3"
if not defined PYBASE python -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1 && set "PYBASE=python"
if defined PYBASE exit /b 0
echo.
echo Não encontrei o Python 3.11 ou mais novo.
echo Instale pelo site https://www.python.org/downloads/ e marque "Add python.exe to PATH".
echo Depois abra este arquivo de novo.
exit /b 1


:falha
echo.
echo Algo deu errado. Leia a mensagem acima.
pause
exit /b 1


:fim
endlocal
exit /b 0
