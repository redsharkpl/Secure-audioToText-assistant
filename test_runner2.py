import asyncio
from main import workflow, State
from google.adk.agents.context import Context

async def test():
    state = State(input_path="test.txt")
    ctx = Context(state=state.model_dump())
    
    async for event in workflow.run(ctx=ctx, node_input=None):
        pass
    
    print("Final state:", ctx.state)

if __name__ == "__main__":
    asyncio.run(test())
