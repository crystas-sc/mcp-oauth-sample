import asyncio
import json
from fastmcp import Client
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# ---- Setup Gemini ----
# Set your API key in a secure way (e.g., environment variable)
# The SDK automatically picks up the GOOGLE_API_KEY environment variable.
# For demonstration purposes, you can also pass it directly: genai.configure(api_key="your_api_key")
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")
genai.configure(api_key=api_key)




async def run_llm(history: list, observation: str = None, toolList: str = None) -> str:
    """Send conversation + observation to Gemini."""
    system_prompt = f"""
    You are a ReAct agent. 
    Here is a list of available tools you can use to take actions:
    {toolList}
    
    """ + """
    Format responses as either:
    - Thought: <reasoning>
    - Action: {"tool": "...", "args": {...}}
    or
    - Final Answer: {"result": "<answer to user>"}
    """
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_prompt
    )
 
    if observation:
        history.append({"role": "user","parts": [{ "text": f"Observation: {observation}"}]})

    response = model.generate_content(history)

    return response.text.strip()

async def agent(prompt: str):
    history = [{"role": "user" ,"parts": [{"text": prompt}]}]

    async with Client("http://localhost:8000/mcp/", auth="oauth") as client:
        tool_list = await client.list_tools()
        print("Available tools:", tool_list)
        print("✅ Connected to MCP server")

        while True:
            # Step 1: LLM generates reasoning or action
            llm_output = await run_llm(history, toolList=tool_list)
            print(f"\nLLM:\n{llm_output}")
            history.append({"role": "model","parts": [{ "text": llm_output}]})

            # Step 2: If it's final answer → stop
            if llm_output.startswith("Final Answer:"):
                final_answer = json.loads(llm_output.replace("Final Answer:", "").strip())
                print("\n🎯 Agent Final Answer:", final_answer["result"])
                break

            # Step 3: If it's an action → parse + call MCP tool
            if llm_output.startswith("Action:"):
                try:
                    action = json.loads(llm_output.replace("Action:", "").strip())
                    tool = action["tool"]
                    args = action.get("args", {})
                    print(f"⚙️ Calling tool {tool} with {args}")
                    result = await client.call_tool(tool, args)
                    # result = await client.call_tool("get_user_info")
                    # Feed observation back to LLM
                    observation = f"Tool {tool} returned: {result.content[0].text}"
                    print(f"📝 Observation:\n{observation}")
                    history.append({"role": "user","parts": [{ "text": observation}]})
                except Exception as e:
                    history.append({"role": "user","parts": [{ "text": f"Observation: ERROR {e}"}]})


def main():
    prompt = "Get the email id of the authenticated Google user."
    asyncio.run(agent(prompt))


if __name__ == "__main__":
    main()
