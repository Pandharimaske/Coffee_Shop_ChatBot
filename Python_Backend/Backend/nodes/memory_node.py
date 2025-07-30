class MemoryNode:
    def __call__(self, state, config):
        if not state["memory_node"]:
            return state
        
        user_id = config["configurable"]["user_id"]
        user_input = state["user_input"]

        from Backend.memory.extractor import MemoryUpdateAgent
        agent = MemoryUpdateAgent()
        memory_intent = agent.extract_memory_action(user_input)

        to_add = memory_intent.add_or_update or {}
        to_remove = memory_intent.remove or {}

        from Backend.utils.memory_manager import (
            merge_and_update_memory, save_user_memory, remove_from_memory
        )

        # memory = get_user_memory(user_id)
        memory = state["user_memory"]
        if to_add:
            memory = merge_and_update_memory(updates=to_add , existing=memory)
        if to_remove:
            memory = remove_from_memory(existing=memory, to_remove=to_remove)

        state["response_message"] = "Got it. I’ve updated your preferences."
        state["user_memory"] = memory
        save_user_memory(user_id=user_id , memory=state["user_memory"])
        return state
    