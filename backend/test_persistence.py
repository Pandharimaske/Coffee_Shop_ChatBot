import os
from dotenv import load_dotenv
load_dotenv()

from src.sessions.session_manager import save_messages, load_messages
from src.memory.memory_manager import save_user_memory, get_user_memory
from src.memory.schemas import UserMemory

def test_chat_persistence():
    print("--- Testing Chat Persistence ---")
    session_id = "test_persistence_session_" + os.urandom(4).hex()
    email = "test@example.com"
    
    print(f"1. Saving message to session: {session_id}")
    save_messages(session_id, email, "Hi bot", "Hello human")
    
    print("2. Loading messages back...")
    msgs = load_messages(session_id)
    if msgs and len(msgs) == 2:
        print("✅ SUCCESS: Chat messages persisted correctly.")
    else:
        print(f"❌ FAILURE: Messages lost. Returned: {msgs}")

def test_memory_persistence():
    print("\n--- Testing Memory Persistence ---")
    email = "test@example.com"
    
    print("1. Fetching current memory...")
    mem = get_user_memory(email)
    
    print("2. Adding a test allergy 'peanut'...")
    mem.allergies.append("peanut")
    save_user_memory(email, mem)
    
    print("3. Fetching back to verify...")
    mem2 = get_user_memory(email)
    if "peanut" in mem2.allergies:
        print("✅ SUCCESS: Memory allergy saved.")
        
        print("4. Testing fuzzy removal of 'PEANUT'...")
        from src.memory.memory_manager import remove_from_memory
        mem2 = remove_from_memory({"allergies": ["PEANUT"]}, mem2)
        save_user_memory(email, mem2)
        
        mem3 = get_user_memory(email)
        if "peanut" not in mem3.allergies:
            print("✅ SUCCESS: Fuzzy removal worked.")
        else:
            print(f"❌ FAILURE: Fuzzy removal failed. Allergies: {mem3.allergies}")
    else:
        print(f"❌ FAILURE: Memory save/load failed. Allergies: {mem2.allergies}")

if __name__ == "__main__":
    try:
        test_chat_persistence()
        test_memory_persistence()
    except Exception as e:
        print(f"🔥 UNEXPECTED ERROR: {e}")
