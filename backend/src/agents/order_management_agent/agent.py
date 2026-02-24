"""Order Management Agent - Handles order creation, updates, confirmation and cancellation."""

import logging
from typing import List
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.graph import END

from src.utils.util import llm
from src.graph.state import CoffeeAgentState, ProductItem
from src.agents.order_management_agent.schema import (
    OrderInput, OrderUpdateState, OrderAction, ActionDecision
)
from src.agents.order_management_agent.prompt import (
    parse_new_order_prompt,
    parse_order_update_prompt,
    detect_order_action_prompt,
)
from langchain_core.runnables import RunnableConfig
from src.rag.retriever import get_product_by_name
from src.orders import save_order, confirm_order, cancel_order

logger = logging.getLogger(__name__)

_action_llm    = llm.with_structured_output(ActionDecision)
_new_order_llm = llm.with_structured_output(OrderInput)
_update_llm    = llm.with_structured_output(OrderUpdateState)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _lookup_price(name: str) -> float:
    result = get_product_by_name(name)
    if result.get("found"):
        return float(result.get("price") or result.get("metadata", {}).get("price", 0.0))
    return 0.0


def _format_order_summary(order: List[ProductItem], final_price: float) -> str:
    lines = [f"  • {item.name} x{item.quantity} @ ₹{item.per_unit_price:.2f} = ₹{item.total_price:.2f}" for item in order]
    return f"Here's your order:\n" + "\n".join(lines) + f"\n\n🧾 Total: ₹{final_price:.2f}\n\nShall I confirm this order?"


def _mock_receipt(order: List[ProductItem], final_price: float) -> str:
    lines = [f"  • {item.name} x{item.quantity} = ₹{item.total_price:.2f}" for item in order]
    return (
        f"✅ Order confirmed! Here's your receipt:\n" + "\n".join(lines) +
        f"\n\n🧾 Total: ₹{final_price:.2f}\n\n"
        f"📧 A receipt has been sent to your email.\n"
        f"💳 Complete your payment here: https://merrysway.coffee/pay/mock-txn-1234"
    )


# ── Main agent ────────────────────────────────────────────────────────────────

async def order_management_agent(state: CoffeeAgentState, config: RunnableConfig = {}) -> Command:
    user_input = state.user_input
    existing_order = list(state.order)
    messages = list(state.messages)
    user_id: str = config.get("configurable", {}).get("user_id", "anonymous")

    try:
        # ── LLM classifies all intent ─────────────────────────────────────────
        # Get last bot message for context (helps confirm detection)
        last_bot_msg = ""
        for m in reversed(messages):
            if m.__class__.__name__ == "AIMessage":
                last_bot_msg = m.content[:200]
                break

        action_decision: ActionDecision = await (detect_order_action_prompt | _action_llm).ainvoke({
            "user_input": user_input,
            "has_existing_order": bool(existing_order),
            "existing_order": [f"{i.name} x{i.quantity}" for i in existing_order],
            "messages": messages,
            "last_bot_message": last_bot_msg,
        })
        action = action_decision.action
        logger.info(f"order_management_agent: action={action} for input='{user_input}'")

        # Safety: existing order + CREATE → treat as UPDATE
        if existing_order and action == OrderAction.CREATE:
            logger.warning("LLM picked CREATE with existing order — overriding to UPDATE")
            action = OrderAction.UPDATE

        # ── CONFIRM ───────────────────────────────────────────────────────────
        if action == OrderAction.CONFIRM:
            if not existing_order:
                msg = "You don't have anything in your order yet. Want to start one?"
                return Command(update={"response_message": msg, "messages": [AIMessage(content=msg)]}, goto=END)

            receipt = _mock_receipt(existing_order, state.final_price)
            if user_id != "anonymous":
                confirm_order(user_id, existing_order, state.final_price)
            return Command(
                update={"response_message": receipt, "messages": [AIMessage(content=receipt)], "order": [], "final_price": 0.0},
                goto=END
            )

        # ── CANCEL ────────────────────────────────────────────────────────────
        elif action == OrderAction.CANCEL:
            msg = "Your order has been cancelled. Let me know if you'd like to start a new one!"
            if user_id != "anonymous":
                cancel_order(user_id)
            return Command(
                update={"response_message": msg, "messages": [AIMessage(content=msg)], "order": [], "final_price": 0.0},
                goto=END
            )

        # ── CREATE ────────────────────────────────────────────────────────────
        elif action == OrderAction.CREATE or (action == OrderAction.UPDATE and not existing_order):
            parsed: OrderInput = await (parse_new_order_prompt | _new_order_llm).ainvoke({
                "user_input": user_input,
                "messages": messages,
            })

            new_order, total, unavailable = [], 0.0, []
            for item in parsed.items:
                price = _lookup_price(item.name)
                if price > 0:
                    line_total = round(price * item.quantity, 2)
                    new_order.append(ProductItem(name=item.name, quantity=item.quantity, per_unit_price=price, total_price=line_total))
                    total += line_total
                else:
                    unavailable.append(item.name)

            total = round(total, 2)

            if not new_order:
                msg = f"Sorry, I couldn't find any of those items on our menu: {', '.join(unavailable)}. Try browsing our menu first!"
                return Command(update={"response_message": msg, "messages": [AIMessage(content=msg)]}, goto=END)

            summary = _format_order_summary(new_order, total)
            if unavailable:
                summary += f"\n\n⚠️ Skipped (not on menu): {', '.join(unavailable)}"
            if user_id != "anonymous":
                save_order(user_id, new_order, total)

            return Command(
                update={"order": new_order, "final_price": total, "response_message": summary, "messages": [AIMessage(content=summary)]},
                goto=END
            )

        # ── UPDATE ────────────────────────────────────────────────────────────
        elif action == OrderAction.UPDATE:
            parsed: OrderUpdateState = await (parse_order_update_prompt | _update_llm).ainvoke({
                "user_input": user_input,
                "existing_order": [f"{i.name} x{i.quantity}" for i in existing_order],
                "messages": messages,
            })

            order_dict = {item.name.lower(): item for item in existing_order}

            for update in parsed.updates:
                key = update.name.lower()
                price = _lookup_price(update.name)

                if update.set_quantity is not None:
                    if update.set_quantity <= 0:
                        order_dict.pop(key, None)
                    else:
                        order_dict[key] = ProductItem(
                            name=update.name, quantity=update.set_quantity,
                            per_unit_price=price, total_price=round(price * update.set_quantity, 2)
                        )
                elif update.delta_quantity is not None:
                    if key in order_dict:
                        new_qty = order_dict[key].quantity + update.delta_quantity
                        if new_qty <= 0:
                            order_dict.pop(key)
                        else:
                            order_dict[key] = ProductItem(
                                name=order_dict[key].name, quantity=new_qty,
                                per_unit_price=price, total_price=round(price * new_qty, 2)
                            )
                    elif update.delta_quantity > 0:
                        order_dict[key] = ProductItem(
                            name=update.name, quantity=update.delta_quantity,
                            per_unit_price=price, total_price=round(price * update.delta_quantity, 2)
                        )

            updated_order = list(order_dict.values())
            total = round(sum(i.total_price or 0 for i in updated_order), 2)

            if not updated_order:
                msg = "Your order is now empty. Let me know if you'd like to order something!"
                if user_id != "anonymous":
                    cancel_order(user_id)
                return Command(
                    update={"order": [], "final_price": 0.0, "response_message": msg, "messages": [AIMessage(content=msg)]},
                    goto=END
                )

            summary = _format_order_summary(updated_order, total)
            if user_id != "anonymous":
                save_order(user_id, updated_order, total)

            return Command(
                update={"order": updated_order, "final_price": total, "response_message": summary, "messages": [AIMessage(content=summary)]},
                goto=END
            )

    except Exception as e:
        logger.error(f"order_management_agent failed: {e}", exc_info=True)
        msg = "Sorry, I ran into an issue processing your order. Please try again."
        return Command(update={"response_message": msg, "messages": [AIMessage(content=msg)]}, goto=END)
