def load_memory(user_id):
    from src.memory.memory_manager import get_user_memory
    memory = get_user_memory(user_id)
    print("\n🧠 Memory for user_id =", user_id)
    print(memory.model_dump_json(indent=2))
    