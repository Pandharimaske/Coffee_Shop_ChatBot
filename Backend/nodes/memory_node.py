class MemoryNode:
    def __call__(self, state, config):
        if not state["memory_node"]:
            return state
        
        user_id = config["configurable"]["user_id"]
        user_input = state["user_input"]

        from Backend.memory.extractor import MemoryUpdateAgent
        agent = MemoryUpdateAgent()
        memory_intent = agent.extract_memory_action(user_input)
        print(memory_intent)

        to_add = memory_intent.add_or_update or {}
        to_remove = memory_intent.remove or {}

        from Backend.utils.memory_manager import (
            get_user_memory, merge_and_update_memory, save_user_memory, remove_from_memory
        )

        memory = get_user_memory(user_id)
        if to_add:
            print("Starting to_add")
            memory = merge_and_update_memory(user_id, to_add)
        if to_remove:
            print("Starting to_remove")
            memory = remove_from_memory(memory, to_remove)
            save_user_memory(user_id, memory)

        state["response_message"] = "Got it. I’ve updated your preferences."
        state["user_memory"] = memory
        return state