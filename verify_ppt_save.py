import asyncio
import json
import sys
import os
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_save():
    log_file = "verify_debug.txt"
    with open(log_file, "w") as f:
        f.write("Starting test...\n")
    
    try:
        base = Path(__file__).resolve().parent
        ppt_p = StdioServerParameters(command=sys.executable, args=[str(base/"ppt_mcp_server.py")])
        
        async with stdio_client(ppt_p) as (pt_r, pt_w):
            async with ClientSession(pt_r, pt_w) as ppt:
                await ppt.initialize()
                
                # Check permissions
                perm_file = str(base / "savingfolder_output" / "perm_test.txt")
                perm_resp = await ppt.call_tool("check_permissions", {"output_path": perm_file})
                with open(log_file, "a") as f:
                    f.write(f"Perm Resp: {perm_resp.content[0].text}\n")
                
                # Create
                init_resp = await ppt.call_tool("create_pptx", {"title": "Test File"})
                init_raw = init_resp.content[0].text
                with open(log_file, "a") as f:
                    f.write(f"Init Raw: {init_raw}\n")
                sid = json.loads(init_raw)["session_id"]
                
                # Save
                out_file = str(base / "savingfolder_output" / "mcp_test_manual.pptx")
                save_resp = await ppt.call_tool("save_presentation", {"session_id": sid, "output_path": out_file})
                with open(log_file, "a") as f:
                    f.write(f"Save Resp: {save_resp.content[0].text}\n")
                    
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"CRASH: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_save())
