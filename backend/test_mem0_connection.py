import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the path
sys.path.append(os.path.join(os.getcwd()))

from src.memory.mem0_manager import mem0_manager

def test_mem0_connection():
    load_dotenv()
    print("--- TESTING MEM0 CONNECTION ---")
    user_id = "test_user_ai"
    # Simple store
    print(f"Adding memory for {user_id}...")
    mem0_manager.add_memory("I love strong espresso with no sugar.", user_id=user_id)
    
    # Simple search
    print(f"Searching memory for {user_id}...")
    results = mem0_manager.search_memories("How do I like my coffee?", user_id=user_id)
    
    if results:
        print(f"SUCCESS! Retrieved context: {results}")
    else:
        print("FAILED: No context retrieved.")

if __name__ == "__main__":
    test_mem0_connection()
