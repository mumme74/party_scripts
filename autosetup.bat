@echo off
setlocal enabledelayedexpansion

:: find the python command
call :find_python PYCMD
if %PYCMD% == "" (
    echo "Python was not found or paths not corretly setup, please install first"
    exit 1
)
echo "using python command '%PYCMD%'"

:: find the pip command
call :find_pip PIPCMD
if %PIPCMD% == "" (
    echo "Pip was not found, please intall first!"
    exit 1
)
echo "using pip command '%PIPCMD%'"

set VENVCMD=venv\Scripts\activate.bat

:: create venv and install requirements
if not exist venv\ (
    echo "Creating virtual environment..."
    set cmd="%PYCMD% -m venv venv"
    echo "cmd=!cmd!"
    for /f %%i in ('!cmd!') do set output=%%i
    echo "!output!"

    echo "Installing requirements..."
    set cmd="venv\Scripts\%PIPCMD% install -r requirements.txt"
    for /f %%i in ('!cmd!') do set output=%%i
    echo "!output!!"
)

:: run main program
set cmd="venv\Scripts\python main.py %~1"
echo !cmd!
for /f %%i in ('!cmd!') do set output=%%i
echo "!output!"

endlocal
goto :eof

:find_python (
    setlocal enabledelayedexpansion
    for %%p in ("python3" "python" "py") do (
        :: run command and get output
        set cmd="%%~p --version"
        set output=
        for /f %%i in ('!cmd!') do set output=%%i

        if "!output:~0,6!" == "Python" (
            set ret=%%~p
            goto :end
        )
    )

    :end
    (endlocal & set %1=%ret%)
    goto :eof
)

:find_pip (
    setlocal enabledelayedexpansion
    for %%p in ("pip3" "pip") do (
        :: run command and get output
        set cmd="%%~p --version"
        set output=
        for /f %%i in ('!cmd!') do set output=%%i

       if "!output:~0,3!" == "pip" goto :end
    )

    :end
    (endlocal & set %1=%output%)
    goto :eof
)

:strlen (
    setlocal enabledelayedexpansion
    set /A len=0
    if "%~1" == "" goto :end
    :strlen_loop
    if not "!%1:~%len%!"=="" set /A len+=1 & goto :strlen_loop

    :end
    @echo on
    (endlocal & set /A %2=%len%)
    goto :eof
)