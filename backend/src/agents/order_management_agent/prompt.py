from langchain_core.prompts import ChatPromptTemplate


# ── 1. Detect what action the user wants ──────────────────────────────────────

detect_order_action_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are classifying a user's intent for a coffee shop order system.

Classify into one of four actions:
- **create** — user wants to place a new order (no existing order)
- **update** — user wants to add, remove, or modify items in an existing order
- **confirm** — user is confirming / approving the current order to place it
- **cancel** — user wants to cancel the entire order

**Context:**
- Has existing order: {has_existing_order}
- Current order: {existing_order}

**Rules:**
- No existing order + item request → "create"
- Existing order + "add X", "also X", "remove X", "change X" → "update"
- "yes", "yeah", "confirm", "go ahead", "place it", "ok", "sure", "do it", "sounds good", "that's correct" → "confirm"
- "cancel", "nevermind", "forget it", "no", "don't want it", "clear order" → "cancel"
- If the last bot message contains "Shall I confirm" or "confirm this order" and user says yes/sure/ok/please/go ahead → always "confirm"
- When in doubt between confirm/cancel, look at the conversation context

Return ONLY valid JSON with field "action"."""),
    ("human", "Last bot message: {last_bot_message}\n\nUser input: {user_input}\n\nRecent messages: {messages}")
])


# ── 2. Parse a new order ──────────────────────────────────────────────────────

parse_new_order_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are extracting order items from a user's message at a coffee shop.

Extract each product name and quantity the user wants.

**Rules:**
- Default quantity is 1 if not specified
- "a latte" → name: "Latte", quantity: 1
- "2 cappuccinos" → name: "Cappuccino", quantity: 2
- Use Title Case for product names
- Extract only items — ignore modifiers like "hot", "iced", "extra shot"

Return ONLY valid JSON with field "items": list of {{name, quantity}}."""),
    ("human", "User input: {user_input}\n\nRecent messages: {messages}")
])


# ── 3. Parse order updates ────────────────────────────────────────────────────

parse_order_update_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are extracting order modifications from a user's message at a coffee shop.

Current order: {existing_order}

Extract what the user wants to change.

**Rules:**
- "Add 2 lattes" → delta_quantity: +2
- "Remove the cappuccino" / "cancel the cappuccino" → set_quantity: 0
- "Make it 3" / "change to 3" → set_quantity: 3
- "One more" → delta_quantity: +1
- "One less" → delta_quantity: -1
- Use Title Case for product names

Return ONLY valid JSON with field "updates": list of {{name, set_quantity?, delta_quantity?}}."""),
    ("human", "User input: {user_input}\n\nRecent messages: {messages}")
])
