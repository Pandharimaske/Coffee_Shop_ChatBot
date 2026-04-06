import asyncio
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(URL, KEY)

SESSIONS_TABLE = "coffee_shop_sessions"
TEST_SID = "stress_test_session_999"

async def append_message_simulated(msg_text):
    # This simulates the current Python logic: Read -> Modify -> Write
    print(f"Starting save for: {msg_text}")
    
    # 1. READ
    res = supabase.table(SESSIONS_TABLE).select("messages").eq("session_id", TEST_SID).execute()
    existing = res.data[0]["messages"] if res.data else []
    
    # 2. DELAY (Simulates network/processing lag)
    await asyncio.sleep(1)
    
    # 3. MODIFY
    updated = existing + [{"role": "user", "content": msg_text}]
    
    # 4. WRITE
    supabase.table(SESSIONS_TABLE).upsert({
        "session_id": TEST_SID,
        "messages": updated,
        "user_email": "stress@test.com"
    }, on_conflict="session_id").execute()
    print(f"Finished save for: {msg_text}")

async def run_test():
    # Cleanup
    supabase.table(SESSIONS_TABLE).delete().eq("session_id", TEST_SID).execute()
    
    # Run two saves simultaneously
    await asyncio.gather(
        append_message_simulated("MESSAGE ONE"),
        append_message_simulated("MESSAGE TWO")
    )
    
    # Check result
    res = supabase.table(SESSIONS_TABLE).select("messages").eq("session_id", TEST_SID).execute()
    messages = res.data[0]["messages"]
    print(f"\nFINAL MESSAGES IN DB: {len(messages)}")
    for m in messages:
        print(f"- {m['content']}")
    
    if len(messages) < 2:
        print("\n❌ RACE CONDITION CONFIRMED: One message was overwritten!")
    else:
        print("\n✅ NO RACE CONDITION FOUND.")

if __name__ == "__main__":
    asyncio.run(run_test())
