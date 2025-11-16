"""
OpenAI Integration with Cogniz Memory

Complete guide to integrating Cogniz with OpenAI GPT models

Difficulty: Intermediate
Time: 20 minutes

Use Case:
- Add persistent memory to OpenAI ChatGPT
- Build context-aware conversations
- Reduce token usage with smart memory retrieval
- Track conversation history automatically

Prerequisites:
- cogniz>=1.0.0
- openai>=1.0.0
- python>=3.8

Setup:
    pip install cogniz openai
    export COGNIZ_API_KEY="your_api_key_here"
    export OPENAI_API_KEY="your_openai_key_here"
"""

from cogniz import CognizClient
from openai import OpenAI
import os
from typing import List, Dict, Optional
import json


class CognizOpenAI:
    """
    OpenAI + Cogniz integration for memory-powered conversations.

    Combines OpenAI's language capabilities with Cogniz's persistent memory.
    """

    def __init__(
        self,
        cogniz_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        self.cogniz = CognizClient(
            api_key=cogniz_api_key or os.getenv("COGNIZ_API_KEY")
        )
        self.openai = OpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )

    def chat(
        self,
        message: str,
        user_id: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Chat with memory context.

        Pattern:
        1. Retrieve relevant memories
        2. Add memories to system prompt
        3. Call OpenAI
        4. Store conversation
        """
        # Step 1: Retrieve memories
        memories = self.cogniz.memory.search(
            query=message,
            user_id=user_id,
            limit=5
        )

        # Step 2: Build context
        context = self._build_context(memories, system_prompt)

        # Step 3: Call OpenAI
        response = self.openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            temperature=0.7
        )

        result = response.choices[0].message.content

        # Step 4: Store conversation
        self.cogniz.memory.add(
            content=f"User: {message}\nAssistant: {result}",
            user_id=user_id,
            tags=["conversation"]
        )

        return result

    def chat_streaming(
        self,
        message: str,
        user_id: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None
    ):
        """
        Streaming chat with memory context.

        Yields chunks of response as they arrive.
        """
        # Retrieve memories
        memories = self.cogniz.memory.search(
            query=message,
            user_id=user_id,
            limit=5
        )

        # Build context
        context = self._build_context(memories, system_prompt)

        # Stream response
        response = self.openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            stream=True
        )

        # Collect full response for storage
        full_response = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        # Store after streaming completes
        self.cogniz.memory.add(
            content=f"User: {message}\nAssistant: {full_response}",
            user_id=user_id,
            tags=["conversation"]
        )

    def chat_with_functions(
        self,
        message: str,
        user_id: str,
        functions: List[Dict],
        model: str = "gpt-4"
    ) -> Dict:
        """
        Chat with OpenAI function calling + memory.

        Example use: Memory as a function tool.
        """
        # Retrieve memories
        memories = self.cogniz.memory.search(
            query=message,
            user_id=user_id,
            limit=5
        )

        context = self._build_context(memories)

        # Call with functions
        response = self.openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            functions=functions,
            function_call="auto"
        )

        return response.choices[0]

    def _build_context(
        self,
        memories: List[Dict],
        system_prompt: Optional[str] = None
    ) -> str:
        """Build context from memories."""
        context = system_prompt or "You are a helpful assistant with memory of past conversations."

        if memories:
            context += "\n\nRelevant context from past conversations:\n"
            for mem in memories[:3]:
                context += f"- {mem['content']}\n"

        return context


# =============================================================================
# DEMO EXAMPLES
# =============================================================================

def demo_basic_chat():
    """Basic chat with memory"""
    print("\n" + "="*80)
    print("DEMO 1: Basic Chat with Memory")
    print("="*80)

    chat = CognizOpenAI()

    # First conversation
    print("\n--- Conversation 1 ---")
    response1 = chat.chat(
        message="My name is Alex and I'm a software engineer",
        user_id="user_001"
    )
    print(f"User: My name is Alex and I'm a software engineer")
    print(f"AI: {response1}\n")

    # Second conversation - AI remembers
    print("\n--- Conversation 2 (Later) ---")
    response2 = chat.chat(
        message="What's my name and profession?",
        user_id="user_001"
    )
    print(f"User: What's my name and profession?")
    print(f"AI: {response2}")
    print("\n Notice: AI remembers from first conversation!\n")


def demo_streaming():
    """Streaming responses with memory"""
    print("\n" + "="*80)
    print("DEMO 2: Streaming Chat")
    print("="*80)

    chat = CognizOpenAI()

    # Store some context
    chat.cogniz.memory.add(
        content="User loves Python programming and FastAPI",
        user_id="user_002",
        tags=["preference"]
    )

    print("\nUser: Tell me about web frameworks")
    print("AI: ", end="", flush=True)

    # Stream response
    for chunk in chat.chat_streaming(
        message="Tell me about web frameworks",
        user_id="user_002"
    ):
        print(chunk, end="", flush=True)

    print("\n\n Notice: Response is personalized to FastAPI preference!\n")


def demo_function_calling():
    """OpenAI function calling with Cogniz"""
    print("\n" + "="*80)
    print("DEMO 3: Function Calling with Memory")
    print("="*80)

    chat = CognizOpenAI()

    # Define functions
    functions = [
        {
            "name": "store_memory",
            "description": "Store important information to remember",
            "parameters": {
                "type": "object",
                "properties": {
                    "information": {
                        "type": "string",
                        "description": "The information to store"
                    }
                },
                "required": ["information"]
            }
        },
        {
            "name": "recall_memory",
            "description": "Recall stored memories",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to recall"
                    }
                },
                "required": ["query"]
            }
        }
    ]

    # Chat with function calling
    response = chat.chat_with_functions(
        message="Remember that I prefer TypeScript over JavaScript",
        user_id="user_003",
        functions=functions
    )

    print(f"Function called: {response.function_call.name if response.function_call else 'None'}")
    print(f"Arguments: {response.function_call.arguments if response.function_call else 'N/A'}")
    print("\n AI can decide when to store memories!\n")


def demo_complete_integration():
    """Complete integration example"""
    print("\n" + "="*80)
    print("COMPLETE EXAMPLE: Memory-Powered ChatGPT Clone")
    print("="*80)

    class MemoryChatBot:
        def __init__(self, user_id: str):
            self.chat = CognizOpenAI()
            self.user_id = user_id

        def run(self):
            print("\n Chat started (type 'quit' to exit)\n")

            while True:
                message = input("You: ")

                if message.lower() in ['quit', 'exit']:
                    print("Chat ended.\n")
                    break

                print("AI: ", end="", flush=True)

                # Stream response
                for chunk in self.chat.chat_streaming(
                    message=message,
                    user_id=self.user_id
                ):
                    print(chunk, end="", flush=True)

                print("\n")

    # Simulate conversation
    bot = MemoryChatBot(user_id="demo_user")

    # Simulated messages (in real use, user would type)
    simulated_messages = [
        "Hi! I'm building a web app with Next.js",
        "What framework am I using?",  # Tests memory
    ]

    print(" Simulated conversation:\n")
    for msg in simulated_messages:
        print(f"You: {msg}")
        response = bot.chat.chat(msg, bot.user_id)
        print(f"AI: {response}\n")

    print(" In production, this would be an interactive chat!\n")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print(" OPENAI + COGNIZ INTEGRATION DEMO")
    print("="*80)

    demo_basic_chat()
    demo_streaming()
    demo_function_calling()
    demo_complete_integration()

    print("="*80)
    print(" DEMO COMPLETE")
    print("="*80)
    print()
    print("What you learned:")
    print("   Basic chat with memory context")
    print("   Streaming responses with memory")
    print("   Function calling integration")
    print("   Complete chatbot implementation")
    print()
    print("Next steps:")
    print("  1. Add conversation summarization")
    print("  2. Implement memory pruning strategies")
    print("  3. Build web UI with React/Next.js")
    print("  4. Add user authentication")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# PRODUCTION PATTERNS
# =============================================================================

"""
## Advanced Integration Patterns

### 1. Conversation Summarization
```python
def summarize_conversation(self, user_id: str):
    # Get recent conversation
    memories = self.cogniz.memory.get_all(
        user_id=user_id,
        tags=["conversation"],
        limit=20
    )

    # Summarize with OpenAI
    conversation_text = "\\n".join([m['content'] for m in memories])

    summary = self.openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize this conversation concisely"},
            {"role": "user", "content": conversation_text}
        ]
    )

    # Store summary
    self.cogniz.memory.add(
        content=f"Summary: {summary.choices[0].message.content}",
        user_id=user_id,
        tags=["summary"]
    )
```

### 2. Memory Pruning
```python
def prune_old_memories(self, user_id: str, keep_recent: int = 50):
    all_memories = self.cogniz.memory.get_all(user_id=user_id)

    if len(all_memories) > keep_recent:
        # Keep recent + summaries
        recent = all_memories[:keep_recent]
        summaries = [m for m in all_memories if "summary" in m.get('tags', [])]

        # Delete old non-summary memories
        for mem in all_memories[keep_recent:]:
            if "summary" not in mem.get('tags', []):
                self.cogniz.memory.delete(memory_id=mem['id'])
```

### 3. Multi-Turn Conversations
```python
def multi_turn_chat(self, messages: List[Dict], user_id: str):
    # Get memory context
    last_message = messages[-1]['content']
    memories = self.cogniz.memory.search(
        query=last_message,
        user_id=user_id,
        limit=5
    )

    # Build conversation history with memory
    system_context = self._build_context(memories)
    full_messages = [{"role": "system", "content": system_context}] + messages

    # Call OpenAI
    response = self.openai.chat.completions.create(
        model="gpt-4",
        messages=full_messages
    )

    return response.choices[0].message.content
```

### 4. Memory as OpenAI Tool
```python
# Define Cogniz memory as OpenAI function
memory_functions = [
    {
        "name": "cogniz_store",
        "description": "Store information to long-term memory",
        "parameters": {
            "type": "object",
            "properties": {
                "information": {"type": "string"}
            }
        }
    },
    {
        "name": "cogniz_search",
        "description": "Search long-term memory",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        }
    }
]

# Let OpenAI decide when to use memory
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    functions=memory_functions,
    function_call="auto"
)

# Handle function calls
if response.choices[0].function_call:
    func_name = response.choices[0].function_call.name
    func_args = json.loads(response.choices[0].function_call.arguments)

    if func_name == "cogniz_store":
        cogniz.memory.add(func_args['information'], user_id=user_id)
    elif func_name == "cogniz_search":
        results = cogniz.memory.search(func_args['query'], user_id=user_id)
```

### 5. Cost Optimization
```python
def optimized_chat(self, message: str, user_id: str):
    # Use cheaper model for memory search
    cheap_check = self.openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Does this require deep knowledge or simple recall: {message}"
        }]
    )

    needs_memory = "knowledge" in cheap_check.choices[0].message.content.lower()

    if needs_memory:
        # Use expensive model with memory
        return self.chat(message, user_id, model="gpt-4")
    else:
        # Use cheap model without memory
        return self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        ).choices[0].message.content
```

### 6. Rate Limiting with Memory
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1000)
def cached_memory_search(query: str, user_id: str):
    # Cache memory searches for 5 minutes
    return self.cogniz.memory.search(
        query=query,
        user_id=user_id
    )

def rate_limited_chat(self, message: str, user_id: str):
    # Check rate limit in memory
    recent_calls = self.cogniz.memory.search(
        query="api_call",
        user_id=user_id,
        tags=["rate_limit"]
    )

    if len(recent_calls) > 10:
        return "Rate limit exceeded. Please wait."

    # Store API call
    self.cogniz.memory.add(
        content="api_call",
        user_id=user_id,
        tags=["rate_limit"],
        metadata={"timestamp": datetime.now().isoformat()}
    )

    return self.chat(message, user_id)
```

## Web App Integration

### FastAPI Example
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
chat_client = CognizOpenAI()

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = chat_client.chat(
            message=request.message,
            user_id=request.user_id
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        for chunk in chat_client.chat_streaming(
            message=request.message,
            user_id=request.user_id
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

### Next.js Example
```javascript
// app/api/chat/route.ts
export async function POST(request: Request) {
  const { message, userId } = await request.json();

  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, user_id: userId })
  });

  const data = await response.json();
  return Response.json(data);
}
```

## Performance Tips
- Cache memory searches with short TTL (5 min)
- Use gpt-3.5-turbo for simple queries
- Limit memory context to top 3-5 results
- Store summaries instead of full conversations
- Implement memory pruning for long-term users
"""
