@echo off
echo Setting up AutoPPT environment...
echo.

REM Set Python path
set PYTHON_PATH=C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT
set PYTHON_EXECUTABLE=C:\Users\gyasu\AppData\Local\Programs\Python\Python313\python.exe

REM Load environment configuration
if exist config.env (
    echo Loading configuration from config.env...
    for /f "tokens=1 delims=" %%a in (type config.env delims^=^") do (
        set "%%a"
    )
) else (
    echo config.env not found, using defaults...
    set PYTHON_PATH=C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT
    set PYTHON_EXECUTABLE=C:\Users\gyasu\AppData\Local\Programs\Python\Python313\python.exe
)

echo.
echo Environment configured:
echo   PYTHON_PATH: %PYTHON_PATH%
echo   PYTHON_EXECUTABLE: %PYTHON_EXECUTABLE%
echo.

echo Testing AutoPPT components...
"%PYTHON_EXECUTABLE%" -c "import sys; sys.path.append(r'%PYTHON_PATH%'); from simple_autoppt import SimpleAutoPPT; print('Import test successful!')"

echo.
echo Testing standalone agent...
"%PYTHON_EXECUTABLE%" simple_autoppt.py "Create a 3-slide presentation on setup test" --output "setup_test.pptx"

echo.
echo If tests passed, you can now:
echo   1. Run: python working_autoppt_mcp.py
echo   2. Configure Claude Desktop with the JSON from claude_final_config.json
echo   3. Use create_presentation tool in Claude
echo.
echo Setup complete!
pause
