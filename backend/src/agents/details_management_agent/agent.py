"""Details Agent - Handles product and shop information queries."""

import logging
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command
from langgraph.graph import END

from src.utils.util import llm
from src.tools import COFFEE_SHOP_TOOLS
from src.agents.details_management_agent.prompt import details_prompt
from src.graph.state import CoffeeAgentState

logger = logging.getLogger(__name__)

# Bind tools to LLM once at module level
_llm_with_tools = llm.bind_tools(COFFEE_SHOP_TOOLS)

# Tool name → function map for execution
_TOOL_MAP = {tool.name: tool for tool in COFFEE_SHOP_TOOLS}


async def details_management_agent(state: CoffeeAgentState) -> Command:
    """
    Handles product and shop information queries using tool calling.

    Flow:
    1. Invoke LLM with tools bound
    2. If LLM calls tools → execute them, feed results back, loop
    3. Once LLM gives final text response → return it
    """
    messages = list(state.messages)

    chain = details_prompt | _llm_with_tools

    try:
        logger.info(f"Details agent processing: {state.user_input[:50]}...")

        # Agentic loop - keep going until LLM stops calling tools
        MAX_ITERATIONS = 5
        for i in range(MAX_ITERATIONS):
            response = await chain.ainvoke({"messages": messages})

            # No tool calls — we have the final answer
            if not response.tool_calls:
                logger.info(f"Details agent completed in {i + 1} iteration(s)")
                return Command(
                    update={
                        "response_message": response.content,
                        "messages": [AIMessage(content=response.content)],
                    },
                    goto=END
                )

            # Execute each tool call
            logger.info(f"Details agent calling {len(response.tool_calls)} tool(s)")
            messages.append(response)  # Add AIMessage with tool_calls to history

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id   = tool_call["id"]

                tool = _TOOL_MAP.get(tool_name)
                if not tool:
                    tool_result = f"Tool '{tool_name}' not found."
                    logger.warning(f"Unknown tool requested: {tool_name}")
                else:
                    try:
                        tool_result = tool.invoke(tool_args)
                        logger.debug(f"Tool '{tool_name}' returned result")
                    except Exception as e:
                        tool_result = f"Tool '{tool_name}' failed: {str(e)}"
                        logger.error(f"Tool execution error for '{tool_name}': {e}")

                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))

        # Exceeded max iterations — return last response content if any
        logger.warning("Details agent exceeded max tool iterations")
        final_content = response.content or "I found some information but had trouble formatting it. Please try again."
        return Command(
            update={
                "response_message": final_content,
                "messages": [AIMessage(content=final_content)],
            },
            goto=END
        )

    except Exception as e:
        logger.error(f"Details agent failed: {e}", exc_info=True)
        return Command(
            update={
                "response_message": "I'm having trouble retrieving that information right now. Please try again.",
            },
            goto=END
        )
