import os
import logging
from mem0 import Memory, MemoryClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Mem0Manager:
    def __init__(self):
        self.mem0_api_key = os.getenv("MEM0_API_KEY")
        self.memory = None
        
        if not self.mem0_api_key:
            logger.warning("MEM0_API_KEY not found in environment. Mem0 will operate in MOCK MODE.")
            return

        try:
            logger.info("Initializing Mem0 in Cloud Mode using MemoryClient")
            self.memory = MemoryClient(api_key=self.mem0_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Mem0 Cloud Client: {e}")
            self.memory = None

    def add_memory(self, text: str, user_id: str, metadata: dict = None):
        """Add context to the user's long-term semantic memory."""
        if not self.memory:
            logger.debug(f"Mem0 MOCK: Adding memory for {user_id}: {text[:30]}...")
            return

        try:
            # MemoryClient (Cloud v2) expects a list of messages
            messages = [{"role": "user", "content": text}]
            self.memory.add(messages=messages, user_id=user_id, metadata=metadata)
            logger.info(f"Added memory to Mem0 for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to add memory to Mem0: {e}")

    def search_memories(self, query: str, user_id: str, limit: int = 5):
        """Retrieve the most relevant semantic memories for the current turn."""
        if not self.memory:
            return ""
        
        try:
            # Mem0 Cloud v2 API via MemoryClient requires explicit filters
            response = self.memory.search(query, filters={"user_id": user_id}, limit=limit)
            
            # MemoryClient returns a dictionary: {"results": [...]}
            results = response.get("results", [])
            if not results:
                return ""
            
            memories = []
            for m in results:
                # Results typically have 'memory' or 'text'
                m_text = m.get("memory") or m.get("text")
                if m_text:
                    memories.append(m_text)
            
            if not memories:
                return ""
                
            return "\n".join([f"- {m}" for m in memories])
        except Exception as e:
            logger.error(f"Failed to search memories in Mem0: {e}")
            return ""

# Global instance
mem0_manager = Mem0Manager()
