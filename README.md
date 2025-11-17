# Cogniz Cookbooks

Production-ready examples for building AI applications with persistent memory using Cogniz.

## Overview

This repository contains practical, executable examples demonstrating how to integrate Cogniz memory platform into real-world applications. Each cookbook is a complete, production-ready implementation that you can run and adapt to your needs.

## Installation

```bash
pip install cogniz openai
```

Set up your API keys:

```bash
export COGNIZ_API_KEY="your_cogniz_api_key"
export OPENAI_API_KEY="your_openai_api_key"
```

## Cookbooks

### Getting Started

**01_quickstart.py** - Build your first memory-powered AI (5 minutes)
- Learn basic memory operations
- Create a simple chatbot with memory
- Integrate with OpenAI and Anthropic

**02_personal_assistant.py** - Personal AI that learns preferences (15 minutes)
- Track user preferences over time
- Provide personalized recommendations
- Build adaptive conversation systems

**03_travel_assistant.py** - Travel planning with memory (15 minutes)
- Remember travel preferences and history
- Generate personalized itineraries
- Track past trips and experiences

### Business Applications

**04_customer_support.py** - Support agent with customer history (20 minutes)
- Remember all customer interactions
- Detect sentiment for escalation
- Integrate with Zendesk and Intercom

### Framework Integrations

**14_openai_integration.py** - Complete OpenAI integration guide (20 minutes)
- Streaming responses with memory context
- Function calling patterns
- Production deployment examples

## Quick Start

```python
from cogniz import Client

# Initialize client
client = Client(api_key="your_api_key", project_id="default")

# Store memory
client.store(
    content="User prefers dark mode and speaks Spanish",
    user_id="user_123",
    metadata={"tags": ["preferences"]}
)

# Retrieve relevant memories
memories = client.search(
    query="What are the user's preferences?",
    user_id="user_123"
)

# Use in your application
for memory in memories:
    print(memory['content'])
```

## Running a Cookbook

Each cookbook can be run directly:

```bash
python 01_quickstart.py
```

Or import and use in your own code:

```python
from cookbook_01_quickstart import PersonalAssistant

assistant = PersonalAssistant(user_id="user_123")
response = assistant.chat("Hello!")
```

## Common Patterns

### Pattern 1: Retrieve - Enhance - Store

```python
# 1. Retrieve relevant context
memories = client.search(query, user_id=user_id)

# 2. Enhance LLM prompt with context
context = "\n".join([m['content'] for m in memories])
response = llm.generate(f"Context: {context}\n\nUser: {query}")

# 3. Store new interaction
client.store(
    content=f"User asked about {topic}",
    user_id=user_id
)
```

### Pattern 2: Multi-Agent Shared Memory

```python
# Agent 1 stores findings
client.store(
    content="Research findings on topic X",
    user_id="project_123",
    metadata={"tags": ["research"]}
)

# Agent 2 retrieves and uses
memories = client.search(
    query="topic X research",
    user_id="project_123"
)
```

### Pattern 3: Memory-Enhanced RAG

```python
# Combine traditional RAG with user memory
rag_results = vector_db.search(query)
memory_context = client.search(query, user_id=user_id)
combined_context = rag_results + memory_context
```

## Best Practices

### Memory Organization
- Use clear, descriptive user_id values for isolation
- Add relevant tags for efficient filtering
- Store structured information when possible

### Efficient Retrieval
- Limit search results to top 3-5 most relevant memories
- Use specific queries for better semantic matching
- Filter by tags when searching specific categories

### Memory Lifecycle
- Store important facts and preferences
- Update memories when information changes
- Remove outdated memories periodically

### Privacy & Compliance
- Never store sensitive PII unless necessary
- Implement data export for portability
- Support right-to-deletion workflows

## Use Cases by Industry

### Customer Support
- Track all customer interactions
- Provide context-aware responses
- Reduce ticket resolution time
- Detect escalation patterns

### Healthcare
- Patient interaction history
- Treatment preference tracking
- Medication records
- Compliance documentation

### Education
- Student progress tracking
- Learning style adaptation
- Curriculum personalization
- Performance analytics

### E-commerce
- Shopping preferences
- Purchase history
- Product recommendations
- Customer service context

### SaaS Applications
- User onboarding state
- Feature usage patterns
- Support ticket history
- Product feedback tracking

## Integration Examples

### With FastAPI

```python
from fastapi import FastAPI
from cogniz import Client

app = FastAPI()
client = Client(api_key="your_key", project_id="default")

@app.post("/chat")
async def chat(message: str, user_id: str):
    memories = client.search(message, user_id=user_id)
    # Process with your LLM
    return {"response": response}
```

### With LangChain

```python
from langchain.memory import CognizMemory
from langchain.chains import ConversationChain

memory = CognizMemory(user_id="user_123")
chain = ConversationChain(memory=memory)
chain.run("What did we discuss yesterday?")
```

### With Streamlit

```python
import streamlit as st
from cogniz import Client

client = Client(api_key=st.secrets["COGNIZ_API_KEY"], project_id="default")

user_input = st.text_input("Message:")
if user_input:
    memories = client.search(user_input, user_id=st.session_state.user_id)
    # Display context-aware response
```

## Performance

- Memory retrieval: < 100ms
- Supports millions of users
- Automatic memory compression
- Reduces LLM token usage by 80%+

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add your cookbook following the existing structure
4. Include documentation and use cases
5. Submit a pull request

### Cookbook Template

```python
"""
Title: Your Cookbook Title

Description: Brief description of what this cookbook demonstrates

Difficulty: Beginner/Intermediate/Advanced
Time: Estimated completion time

Use Case:
- Problem it solves
- Target audience
- Expected outcomes

Prerequisites:
- cogniz>=1.0.0
- other-package>=version
"""

from cogniz import Client

def main():
    # Your implementation
    pass

if __name__ == "__main__":
    main()
```

## Documentation

Full documentation available at: https://docs.cogniz.ai

API Reference: https://docs.cogniz.ai/api-reference

## Support

- GitHub Issues: https://github.com/cognizonline/cogniz-cookbooks/issues
- Email: support@cogniz.ai
- Documentation: https://docs.cogniz.ai

## License

MIT License - see LICENSE file for details

## Security

Never commit API keys or sensitive information to this repository. Use environment variables for all credentials.

If you discover a security vulnerability, please email security@cogniz.ai.
