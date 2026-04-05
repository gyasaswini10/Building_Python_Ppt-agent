#!/usr/bin/env python3
"""
Minimal Test Script
"""

try:
    print("Testing AutoPPT components...")
    import sys
    sys.path.append(r"C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT")
    from simple_autoppt import SimpleAutoPPT
    print("✅ Import successful!")
    
    agent = SimpleAutoPPT("Test presentation", "minimal_test.pptx")
    print("✅ Agent created!")
    
    import asyncio
    result = asyncio.run(agent.execute())
    print(f"✅ Result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("🎯 Test completed!")
