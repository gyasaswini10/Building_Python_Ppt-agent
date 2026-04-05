@echo off
echo Setting up AutoPPT...
cd /d "C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT"

if exist config.env (
    echo Found config.env
) else (
    echo Creating default config...
    echo # AutoPPT Environment Configuration > config.env
    echo. >> config.env
    echo # API Keys - add your keys here >> config.env
    echo OPENROUTER_API_KEY_1=your_openrouter_key_here >> config.env
    echo OPENROUTER_API_KEY_2=backup_openrouter_key >> config.env
    echo HF_TOKENS=hf_token1,hf_token2,hf_token3 >> config.env
    echo. >> config.env
    echo # Python Configuration >> config.env
    echo PYTHON_PATH=C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT >> config.env
    echo PYTHON_EXECUTABLE=C:\Users\gyasu\AppData\Local\Programs\Python\Python313\python.exe >> config.env
    echo. >> config.env
    echo # Development Settings >> config.env
    echo DEBUG=true >> config.env
    echo LOG_LEVEL=INFO >> config.env
    echo Config created successfully!
)

echo.
echo Testing imports...
python -c "import sys; sys.path.append(r'C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT'); from simple_autoppt import SimpleAutoPPT; print('✅ Import successful!')"

echo.
echo Testing standalone agent...
python simple_autoppt.py "Create a 3-slide presentation on setup test" --output "setup_test.pptx"

echo.
echo Setup complete! Now you can:
echo   1. Start MCP server: python working_autoppt_mcp.py
echo   2. Configure Claude Desktop with claude_final_config.json
echo   3. Use create_presentation tool in Claude
echo.
pause
