#!/usr/bin/env python3
"""
Test script to demonstrate delete slide functionality
"""
import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_delete_slide():
    """Test the delete slide functionality on climate_test.pptx"""
    base = Path(__file__).resolve().parent / 'client'
    ppt_p = StdioServerParameters(command=sys.executable, args=[str(base/'ppt_mcp_server.py')])
    
    async with stdio_client(ppt_p) as (pt_r, pt_w):
        async with ClientSession(pt_r, pt_w) as ppt:
            await ppt.initialize()
            
            # Open existing presentation
            result = await ppt.call_tool('open_presentation', {
                'file_path': str(Path('savingfolder_output/climate_test.pptx'))
            })
            
            if result.content[0].text:
                data = json.loads(result.content[0].text)
                session_id = data.get('session_id')
                print(f'✅ Opened presentation with Session ID: {session_id}')
                
                # Get current slide info
                info = await ppt.call_tool('get_slide_info', {
                    'session_id': session_id, 
                    'slide_index': -1
                })
                slides_data = json.loads(info.content[0].text)
                print('\n📊 Current slides:')
                for slide in slides_data.get('slides_info', []):
                    print(f'  Slide {slide["index"]}: {slide["title"]}')
                
                # Delete slide 2 (Physiological & Structural Features)
                print('\n🗑️  Deleting slide 2: "Physiological & Structural Features"...')
                delete_result = await ppt.call_tool('delete_slide', {
                    'session_id': session_id, 
                    'slide_index': 2
                })
                delete_data = json.loads(delete_result.content[0].text)
                
                if delete_data.get('ok'):
                    print(f'✅ Successfully deleted slide {delete_data.get("deleted_index")}')
                    print(f'📊 Total slides now: {delete_data.get("slides_total")}')
                else:
                    print(f'❌ Delete failed: {delete_data.get("error")}')
                    return
                
                # Get updated slide info
                info2 = await ppt.call_tool('get_slide_info', {
                    'session_id': session_id, 
                    'slide_index': -1
                })
                slides_data2 = json.loads(info2.content[0].text)
                print('\n📊 Updated slides after deletion:')
                for slide in slides_data2.get('slides_info', []):
                    print(f'  Slide {slide["index"]}: {slide["title"]}')
                
                # Save the modified presentation
                print('\n💾 Saving modified presentation...')
                save_result = await ppt.call_tool('save_presentation', {
                    'session_id': session_id, 
                    'output_path': str(Path('savingfolder_output/climate_test_modified.pptx'))
                })
                save_data = json.loads(save_result.content[0].text)
                
                if save_data.get('ok'):
                    print(f'✅ Saved modified presentation: {save_data.get("output_path")}')
                else:
                    print(f'❌ Save failed: {save_data.get("error")}')
            else:
                print('❌ Failed to open presentation')

if __name__ == "__main__":
    print("🧪 Testing Delete Slide Functionality")
    print("=" * 50)
    asyncio.run(test_delete_slide())
