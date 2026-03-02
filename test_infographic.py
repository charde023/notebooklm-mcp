import asyncio
import json
import sys
from pathlib import Path

# Fix Windows asyncio bug
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from notebooklm.client import NotebookLMClient
from notebooklm.auth import extract_cookies_from_storage, fetch_tokens, AuthTokens

async def test_infographic():
    storage_path = Path.home() / ".notebooklm" / "storage_state.json"
    if not storage_path.exists():
        print("Not logged in.")
        return
        
    state = json.loads(storage_path.read_text())
    cookies = extract_cookies_from_storage(state)
    csrf, session_id = await fetch_tokens(cookies)
    auth = AuthTokens(cookies=cookies, csrf_token=csrf, session_id=session_id)
    client = NotebookLMClient(auth)

    async with client:
        nbs = await client.notebooks.list()
        if not nbs:
            print("No notebooks found.")
            return
            
        nb = nbs[0]
        print(f"Testing infographic on notebook: {nb.id}")
        
        try:
            status = await client.artifacts.generate_infographic(nb.id, language="ko")
            print(f"Success! Status ID: {status.task_id if hasattr(status, 'task_id') else status}")
        except Exception as e:
            import traceback
            print(f"FAILED!\nError type: {type(e)}\n{e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_infographic())
