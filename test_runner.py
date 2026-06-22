from google.adk.workflow import Workflow
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from main import State
import asyncio
from typing import Any

def test_node(ctx: Any):
    print("ctx.state type:", type(ctx.state))
    print("'input_path' in ctx.state:", "input_path" in ctx.state)
    print("ctx.state.get('input_path'):", getattr(ctx.state, 'get', lambda x: None)('input_path'))
    return {"raw_text": "hello"}

test_wf = Workflow(name="test_wf", state_schema=State, edges=[("START", test_node)])

async def main():
    session_service = InMemorySessionService()
    runner = Runner(node=test_wf, session_service=session_service, auto_create_session=True)
    await session_service.create_session(user_id="user1", session_id="sess1", app_name="test_app", state={"input_path": "test.txt"})
    async for event in runner.run_async(user_id="user1", session_id="sess1"):
        pass
        
    session = await session_service.get_session(user_id="user1", session_id="sess1", app_name="test_app")
    print("Final State:", session.state)
    print("Final State:", session.state)

if __name__ == "__main__":
    asyncio.run(main())
