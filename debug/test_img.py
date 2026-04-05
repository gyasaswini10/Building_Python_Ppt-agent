import httpx
import asyncio
import re

async def test_img():
    subject_key = "frog"
    slide_key = "tadpole"
    tags = f"{subject_key},{slide_key}"
    url = f"https://source.unsplash.com/featured/800x600/?{tags}"
    print(f"Testing URL: {url}")
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        r = await client.get(url)
        print(f"Status: {r.status_code}")
        print(f"Content Length: {len(r.content)}")
        with open("test_img.jpg", "wb") as f:
            f.write(r.content)
        print("Written to test_img.jpg")

if __name__ == "__main__":
    asyncio.run(test_img())
