@echo off
echo ========================================
echo AUTOMATYZACJA TESTOW PI CALCULATOR
echo ========================================
echo.

rem --- Dostosuj tu, jeśli Twoja instalacja ma inną ścieżkę ---
set "VSROOT=D:\Microsoft Visual Studio\2022\Comunity"
rem ----------------------------------------------------------------

rem Najpierw spróbuj wywołać vcvarsall z ustawionego VSROOT
set "VCVARS=%VSROOT%\VC\Auxiliary\Build\vcvarsall.bat"

if exist "%VCVARS%" (
    echo Wywolanie: "%VCVARS%" x64
    call "%VCVARS%" x64
) else (
    echo Nie znaleziono "%VCVARS%". Sprobuję znalezc vswhere aby zlokalizowac instalacje VS...
    where "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" >nul 2>&1
    if %errorlevel%==0 (
        for /f "usebackq delims=" %%p in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSROOT_FOUND=%%p"
        if defined VSROOT_FOUND (
            set "VCVARS2=%VSROOT_FOUND%\VC\Auxiliary\Build\vcvarsall.bat"
            if exist "%VCVARS2%" (
                echo Wywolanie: "%VCVARS2%" x64
                call "%VCVARS2%" x64
            ) else (
                echo Nie znaleziono vcvarsall w: "%VCVARS2%"
                echo Sprawdz instalacje Visual Studio lub popraw VSROOT w tym skrypcie.
                pause
                exit /b 1
            )
        ) else (
            echo vswhere nie zwrocil sciezki instalacji Visual Studio.
            echo Sprawdz instalacje lub recznie ustaw VSROOT w skrypcie.
            pause
            exit /b 1
        )
    ) else (
        echo vswhere.exe nie znaleziony. Upewnij sie, ze Visual Studio jest zainstalowane.
        echo Mozesz recznie ustawic zmienna VSROOT w tym skrypcie.
        pause
        exit /b 1
    )
)

rem Sprawdzamy czy cl.exe jest teraz dostepny
where cl >nul 2>&1
if errorlevel 1 (
    echo Nie znaleziono kompilatora cl.exe po ustawieniu srodowiska.
    echo Upewnij sie, ze VSROOT jest poprawny i ze wywolano vcvarsall.bat.
    pause
    exit /b 1
)

echo 1. Kompilacja programu...
cl /EHsc /O2 /MD /std:c++14 /D_CRT_SECURE_NO_WARNINGS pi_integral.cpp /Fe:pi_integral.exe
if errorlevel 1 (
    echo Blad kompilacji!
    pause
    exit /b 1
)

rem --- Ustalamy pelna sciezke do Python (uzyj podanej sciezki) ---
set "PYTHON_EXE=C:\Users\simon\AppData\Local\Programs\Python\Python314\python.exe"

if exist "%PYTHON_EXE%" (
    echo Uzywam Pythona: "%PYTHON_EXE%"
) else (
    echo Podana sciezka do python.exe nie istnieje: "%PYTHON_EXE%"
    echo Sprobuję znalezc 'py' lub 'python' w PATH...
    set "PYTHON_EXE="
    where py >nul 2>&1
    if %errorlevel%==0 set "PYTHON_EXE=py"
    if not defined PYTHON_EXE (
        where python >nul 2>&1
        if %errorlevel%==0 set "PYTHON_EXE=python"
    )
    if not defined PYTHON_EXE (
        echo Python nie zostal znaleziony. Zainstaluj Pythona lub popraw sciezke PYTHON_EXE w tym skrypcie.
        pause
        exit /b 1
    ) else (
        echo Znaleziono: %PYTHON_EXE%
    )
)

echo 2. Testowanie z roznymi parametrami (dynamic)...
if not exist "tools\run_bench.py" (
    echo Nie znaleziono tools\run_bench.py
    pause
    exit /b 1
)
"%PYTHON_EXE%" "tools\run_bench.py" --exe "pi_integral.exe" --steps 100000000 1000000000 --max-threads 16 --repeats 2 --mode dynamic

echo 3. Testowanie trybu static...
"%PYTHON_EXE%" "tools\run_bench.py" --exe "pi_integral.exe" --steps 100000000 --mode static --max-threads 16 --repeats 2

echo 4. Generowanie raportu (wyswietlenie CSV)...
echo.
echo OSTATECZNE WYNIKI (z bench_results.csv):
if exist "bench_results.csv" (
    type "bench_results.csv"
) else (
    echo Plik bench_results.csv nie zostal znaleziony.
)

echo.
echo ========================================
echo TESTY ZAKONCZONE
echo ========================================
pause
