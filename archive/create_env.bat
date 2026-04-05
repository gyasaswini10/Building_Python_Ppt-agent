# AutoPPT Environment Setup
echo Creating environment configuration...

# Create .env file
echo # AutoPPT Environment Configuration > .env
echo OPENROUTER_API_KEY_1=your_openrouter_key_here >> .env
echo OPENROUTER_API_KEY_2=backup_openrouter_key >> .env
echo HF_TOKENS=hf_token1,hf_token2,hf_token3 >> .env
echo PYTHON_PATH=%CD% >> .env
echo PYTHON_EXECUTABLE=%PYTHON_EXECUTABLE% >> .env
echo DEBUG=true >> .env
echo .env file created successfully!

# Set environment variables for current session
set PYTHON_PATH=%CD%
set OPENROUTER_API_KEY_1=your_openrouter_key_here
set OPENROUTER_API_KEY_2=backup_openrouter_key
set HF_TOKENS=hf_token1,hf_token2,hf_token3
set DEBUG=true

echo Environment configured!
echo PYTHON_PATH: %PYTHON_PATH%
echo PYTHON_EXECUTABLE: %PYTHON_EXECUTABLE%

# Test basic imports
echo Testing Python environment...
%PYTHON_EXECUTABLE% -c "import sys; sys.path.append(r'%PYTHON_PATH%'); print('✅ Environment set successfully!')"

echo.
echo Setup complete! Now you can run:
echo   1. Test standalone: %PYTHON_EXECUTABLE% simple_autoppt.py "test presentation"
echo   2. Start MCP server: %PYTHON_EXECUTABLE% working_autoppt_mcp.py
echo   3. Configure Claude with claude_final_config.json
echo.
pause
