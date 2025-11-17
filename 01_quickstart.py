"""
Quickstart: Your First Cogniz App

Build a memory-powered chatbot in 5 minutes

Difficulty: Beginner
Time: 5 minutes

Prerequisites:
- cogniz>=1.0.0
- python>=3.8

Setup:
    pip install cogniz
    export COGNIZ_API_KEY="your_api_key_here"
"""

from cogniz import Client
import os

# Initialize Cogniz client
# Note: You need a project_id. Use "default" or create a custom project
client = Client(
    api_key=os.getenv("COGNIZ_API_KEY"),
    project_id="default"  # Use your project ID here
)


def step_1_store_user_info():
    """
    Step 1: Store information about your user
    """
    print("=" * 60)
    print("STEP 1: Storing User Information")
    print("=" * 60)

    # Store user preferences and information
    result = client.store(
        content="Sarah prefers dark mode, speaks Spanish, and works in healthcare",
        user_id="sarah_123",
        metadata={"tags": ["preferences", "profile"]}
    )

    print(f"[SUCCESS] Memory stored successfully!")
    print(f"Memory ID: {result.get('id', 'N/A')}")
    print()


def step_2_retrieve_memories():
    """
    Step 2: Retrieve relevant memories when needed
    """
    print("=" * 60)
    print("STEP 2: Retrieving User Memories")
    print("=" * 60)

    # Search for relevant information
    search_result = client.search(
        query="What language does the user speak?",
        user_id="sarah_123",
        limit=5
    )

    # Extract results from the response
    memories = search_result.get('results', [])

    print(f"[SUCCESS] Found {len(memories)} relevant memories:")
    for i, memory in enumerate(memories, 1):
        content = memory.get('content', str(memory))
        print(f"\n   {i}. {content}")

    print()
    return memories


def step_3_build_ai_response():
    """
    Step 3: Use memories to create personalized AI responses
    """
    print("=" * 60)
    print("STEP 3: Building Personalized AI Response")
    print("=" * 60)

    user_question = "Can you help me with HIPAA compliance?"

    # Get relevant context from memory
    search_result = client.search(
        query=user_question,
        user_id="sarah_123",
        limit=3
    )

    # Extract results from search response
    memories = search_result.get('results', [])

    # Build context for your LLM
    context = "User context:\n"
    for memory in memories:
        content = memory.get('content', str(memory))
        context += f"- {content}\n"

    print(f"User question: {user_question}")
    print(f"Retrieved {len(memories)} relevant memories")
    print()
    print(f"AI can now respond with personalized context:")
    print(f"   'Since you work in healthcare, here's HIPAA-specific guidance...'")
    print(f"   'I can explain this in Spanish if you prefer...'")
    print()

    # Store this new interaction
    client.store(
        content="User asked about HIPAA compliance in healthcare context",
        user_id="sarah_123",
        metadata={"tags": ["questions", "compliance"]}
    )

    print("[SUCCESS] Interaction stored for future reference")
    print()


def complete_example():
    """
    Complete example: Simple chatbot with memory
    """
    print("\n" + "=" * 60)
    print("COMPLETE EXAMPLE: Memory-Powered Chatbot")
    print("=" * 60 + "\n")

    user_id = "demo_user_001"

    # Simulate a conversation
    conversations = [
        "My name is Alex and I love Python programming",
        "I'm working on a machine learning project",
        "What was my name again?",
    ]

    for i, message in enumerate(conversations, 1):
        print(f"Turn {i}:")
        print(f"  User: {message}")

        # Retrieve relevant context
        search_result = client.search(
            query=message,
            user_id=user_id,
            limit=3
        )

        # Extract results
        memories = search_result.get('results', [])

        # Simple response logic
        if "name" in message.lower() and "again" in message.lower():
            if memories:
                content = memories[0].get('content', '')
                name = content.split()[3] if len(content.split()) > 3 else 'unknown'
                response = f"Your name is {name}"
            else:
                response = "I don't have that information yet"
        else:
            response = "I'll remember that!"

            # Store new information
            client.store(
                content=message,
                user_id=user_id,
                metadata={"tags": ["conversation"]}
            )

        print(f"  Bot: {response}")
        print()


def cleanup(user_id="sarah_123"):
    """
    Optional: Clean up demo data
    """
    print("=" * 60)
    print("CLEANUP (Optional)")
    print("=" * 60)

    # Uncomment to delete all memories for this demo:
    # client.memory.delete_all(user_id=user_id)
    # print(f"All memories deleted for user: {user_id}")

    print("Tip: Keep memories between runs to see persistence")
    print()


def main():
    """
    Run the quickstart tutorial
    """
    print("\n")
    print("COGNIZ QUICKSTART")
    print("Build your first memory-powered AI app")
    print("\n")

    # Basic steps
    step_1_store_user_info()
    step_2_retrieve_memories()
    step_3_build_ai_response()

    # Complete example
    complete_example()

    # Optional cleanup
    # cleanup()

    print("=" * 60)
    print("QUICKSTART COMPLETE")
    print("=" * 60)
    print()
    print("What you learned:")
    print("  - How to store memories with client.store()")
    print("  - How to retrieve memories with client.search()")
    print("  - How to build personalized AI responses")
    print()
    print("Next steps:")
    print("  1. Try 02_personal_assistant.py for a full chatbot")
    print("  2. Explore 04_customer_support.py for business use case")
    print("  3. Check out 14_openai_integration.py for LLM integration")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# INTEGRATION TIPS
# =============================================================================

"""
## How to use Cogniz with your LLM

### With OpenAI:
```python
from openai import OpenAI

openai = OpenAI()

# Get memories
search_result = client.search(query, user_id=user_id)
memories = search_result.get('results', [])
context = "\\n".join([m.get('content', str(m)) for m in memories])

# Add to your prompt
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"User context: {context}"},
        {"role": "user", "content": query}
    ]
)
```

### With Anthropic Claude:
```python
from anthropic import Anthropic

anthropic = Anthropic()

search_result = client.search(query, user_id=user_id)
memories = search_result.get('results', [])
context = "\\n".join([m.get('content', str(m)) for m in memories])

response = anthropic.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[
        {"role": "user", "content": f"Context: {context}\\n\\nUser: {query}"}
    ]
)
```

### Memory Best Practices:
1. **Store facts, not fluff** - Skip greetings, store meaningful info
2. **Use clear user_id** - Keep users' memories isolated
3. **Add relevant tags** - Makes filtering faster
4. **Limit search results** - Top 3-5 memories usually sufficient
5. **Update, don't duplicate** - Use memory.update() for changes

### Error Handling:
```python
try:
    client.store(content=content, user_id=user_id)
except Exception as e:
    print(f"Memory storage failed: {e}")
    # Continue without memory - don't break user experience
```
"""
