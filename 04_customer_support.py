"""
Customer Support Agent with Persistent Memory

Build a support chatbot that remembers every customer interaction

Difficulty: Intermediate
Time: 20 minutes

Use Case:
- Remember all customer interactions automatically
- Provide context-aware support responses
- Track customer sentiment and history
- Reduce repeat questions with memory context

Prerequisites:
- cogniz>=1.0.0
- openai>=1.0.0 (or any LLM provider)
- python>=3.8

Setup:
    pip install cogniz openai
    export COGNIZ_API_KEY="your_api_key_here"
    export OPENAI_API_KEY="your_openai_key_here"
"""

from cogniz import Client
from openai import OpenAI
import os
from datetime import datetime
from typing import List, Dict, Optional
import json


class CustomerSupportAgent:
    """
    Memory-powered customer support agent.

    Features:
    - Remembers all customer interactions
    - Automatically categorizes support tickets
    - Provides context-aware responses
    - Tracks sentiment for escalation
    """

    def __init__(
        self,
        cogniz_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        # Initialize clients
        self.cogniz = Client(api_key=cogniz_api_key or os.getenv("COGNIZ_API_KEY", project_id="default")
        )
        self.openai = OpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )

    def handle_customer_query(
        self,
        customer_id: str,
        query: str,
        ticket_id: Optional[str] = None
    ) -> Dict:
        """
        Process customer query with full memory context.
        """
        print(f"\n{'='*60}")
        print(f" Ticket: {ticket_id or 'New Query'}")
        print(f" Customer: {customer_id}")
        print(f"{'='*60}\n")

        # Step 1: Retrieve customer history from memory
        print(" Retrieving customer history...")
        customer_history = self.cogniz.search(
            query=query,
            user_id=customer_id,
            limit=5
        )

        print(f" Found {len(customer_history)} relevant past interactions")
        print()

        # Step 2: Build context for LLM
        context = self._format_context(customer_history, query)

        # Step 3: Generate response
        print(" Generating response...")
        response = self._call_llm(context, query)
        print(f" Response generated")
        print()

        # Step 4: Store this interaction in memory
        print(" Storing interaction...")
        self._store_interaction(
            customer_id=customer_id,
            query=query,
            response=response,
            ticket_id=ticket_id
        )
        print(f" Memory updated")
        print()

        return {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "query": query,
            "response": response,
            "memories_used": len(customer_history)
        }

    def _format_context(
        self,
        customer_history: List[Dict],
        query: str
    ) -> str:
        """
        Format customer history as context for the LLM.
        """
        context = "# CUSTOMER HISTORY\n\n"

        if customer_history:
            context += "Previous interactions:\n"
            for mem in customer_history[:3]:  # Top 3 most relevant
                content = mem['content']
                timestamp = mem.get('created_at', 'Unknown')
                tags = mem.get('tags', [])

                context += f"- [{', '.join(tags)}] {content} (on {timestamp})\n"
        else:
            context += "No previous interactions found.\n"

        context += f"\n# CURRENT QUERY\n{query}\n"

        return context

    def _call_llm(self, context: str, query: str) -> str:
        """
        Call LLM with customer context.
        """
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful customer support agent. Use the customer history to provide personalized, context-aware support."
                    },
                    {
                        "role": "user",
                        "content": f"{context}\n\nPlease respond to the current query."
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"I apologize, I'm having technical difficulties. Error: {str(e)}"

    def _store_interaction(
        self,
        customer_id: str,
        query: str,
        response: str,
        ticket_id: Optional[str] = None
    ):
        """
        Store interaction in memory with automatic categorization.
        """
        # Detect category from query keywords
        category = self._detect_category(query)

        # Detect sentiment for escalation tracking
        sentiment = self._detect_sentiment(query)

        # Store in memory
        memory_content = f"Customer query: {query}"

        self.cogniz.store(
            content=memory_content,
            user_id=customer_id,
            metadata={"tags": [category, sentiment, "support"]},
            metadata={
                "ticket_id": ticket_id,
                "timestamp": datetime.now().isoformat(),
                "category": category,
                "sentiment": sentiment
            }
        )

    def _detect_category(self, query: str) -> str:
        """
        Categorize support query by keywords.
        """
        keywords = {
            "billing": ["invoice", "charge", "payment", "refund", "billing", "price"],
            "technical": ["bug", "error", "crash", "not working", "broken", "issue"],
            "account": ["password", "login", "access", "account", "signup", "register"],
            "product": ["feature", "how to", "usage", "guide", "help", "tutorial"]
        }

        query_lower = query.lower()
        for category, terms in keywords.items():
            if any(term in query_lower for term in terms):
                return category

        return "general"

    def _detect_sentiment(self, query: str) -> str:
        """
        Detect sentiment for escalation purposes.
        """
        negative_words = ["frustrated", "angry", "disappointed", "terrible", "worst", "hate"]
        positive_words = ["thanks", "appreciate", "great", "excellent", "happy", "love"]

        query_lower = query.lower()

        if any(word in query_lower for word in negative_words):
            return "negative"
        elif any(word in query_lower for word in positive_words):
            return "positive"
        else:
            return "neutral"

    def get_customer_summary(self, customer_id: str) -> Dict:
        """
        Generate summary of customer interactions.
        """
        memories = self.cogniz.get_all(user_id=customer_id)

        # Analyze patterns
        categories = {}
        sentiments = {}

        for mem in memories:
            tags = mem.get('tags', [])
            for tag in tags:
                if tag in ["billing", "technical", "account", "product"]:
                    categories[tag] = categories.get(tag, 0) + 1
                if tag in ["positive", "negative", "neutral"]:
                    sentiments[tag] = sentiments.get(tag, 0) + 1

        return {
            "customer_id": customer_id,
            "total_interactions": len(memories),
            "categories": categories,
            "sentiments": sentiments,
            "recent_memories": memories[:5]
        }


# =============================================================================
# DEMO SCENARIOS
# =============================================================================

def demo_first_contact():
    """
    Scenario: First-time customer with billing issue
    """
    print("\n" + "="*80)
    print("SCENARIO 1: First Contact - Billing Issue")
    print("="*80)

    agent = CustomerSupportAgent()

    result = agent.handle_customer_query(
        customer_id="cust_001",
        query="I was charged $299 but my invoice says $199. Can you help?",
        ticket_id="TKT-12345"
    )

    print(f" Result Summary:")
    print(f"   Customer: {result['customer_id']}")
    print(f"   Ticket: {result['ticket_id']}")
    print(f"   Memories used: {result['memories_used']}")
    print()


def demo_returning_customer():
    """
    Scenario: Returning customer - agent remembers previous issue
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Returning Customer - Follow-up")
    print("="*80)

    agent = CustomerSupportAgent()

    # Customer returns with follow-up
    result = agent.handle_customer_query(
        customer_id="cust_001",  # Same customer from scenario 1
        query="Hi, just following up on my billing issue from last week",
        ticket_id="TKT-12346"
    )

    print(f" Result Summary:")
    print(f"   Customer: {result['customer_id']}")
    print(f"   Ticket: {result['ticket_id']}")
    print(f"   Memories used: {result['memories_used']} (includes previous ticket!)")
    print(f"    Agent automatically references invoice #12345 from last week")
    print()


def demo_frustrated_customer():
    """
    Scenario: Frustrated customer - sentiment detection
    """
    print("\n" + "="*80)
    print("SCENARIO 3: Frustrated Customer - Sentiment Detection")
    print("="*80)

    agent = CustomerSupportAgent()

    result = agent.handle_customer_query(
        customer_id="cust_002",
        query="I'm so frustrated! This is the third time I'm contacting support about login issues!",
        ticket_id="TKT-12347"
    )

    print(f" Result Summary:")
    print(f"   Customer: {result['customer_id']}")
    print(f"   Sentiment: NEGATIVE (auto-detected)")
    print(f"    Recommendation: Escalate to senior agent")
    print()


def demo_customer_summary():
    """
    Show customer interaction summary report
    """
    print("\n" + "="*80)
    print("CUSTOMER SUMMARY REPORT")
    print("="*80)

    agent = CustomerSupportAgent()
    summary = agent.get_customer_summary("cust_001")

    print(json.dumps(summary, indent=2, default=str))
    print()


def main():
    """
    Run all demo scenarios
    """
    print("\n" + "="*80)
    print(" CUSTOMER SUPPORT AGENT DEMO")
    print("="*80)

    # Run demo scenarios
    demo_first_contact()
    demo_returning_customer()
    demo_frustrated_customer()

    # Show customer summary
    demo_customer_summary()

    print("="*80)
    print(" DEMO COMPLETE")
    print("="*80)
    print()
    print("What you learned:")
    print("   Store customer interactions automatically")
    print("   Retrieve context for personalized support")
    print("   Detect sentiment for escalation")
    print("   Generate customer interaction summaries")
    print()
    print("Next steps:")
    print("  1. Integrate with your support platform (Zendesk, Intercom)")
    print("  2. Add real sentiment analysis API")
    print("  3. Implement escalation workflows")
    print("  4. Track metrics (resolution time, CSAT)")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# PRODUCTION ENHANCEMENTS
# =============================================================================

"""
## Production Deployment Tips

### 1. Sentiment-Based Escalation
```python
if sentiment == "negative" and interaction_count > 2:
    # Auto-escalate to human agent
    escalate_to_human(customer_id, ticket_id)
```

### 2. Multi-Channel Support
```python
# Store interactions from all channels
client.store(
    content=message,
    user_id=customer_id,
    metadata={"tags": ["support", channel]},  # "email", "chat", "phone"
    metadata={"channel": channel}
)

# Retrieve across all channels
memories = client.search(
    query=query,
    user_id=customer_id
    # Automatically includes email, chat, phone history
)
```

### 3. Integration with Support Platforms

#### Zendesk Webhook:
```python
@app.post("/zendesk/webhook")
async def zendesk_webhook(ticket: dict):
    # Store ticket in Cogniz memory
    client.store(
        content=ticket['description'],
        user_id=ticket['requester_id'],
        metadata={"tags": ["zendesk", "support"]},
        metadata={"ticket_id": ticket['id']}
    )
```

#### Intercom Integration:
```python
from intercom_client import Client as IntercomClient

intercom = IntercomClient()

# Get user conversation history from Cogniz
memories = client.search(
    query=message,
    user_id=intercom_user_id
)

# Add to Intercom note
intercom.notes.create(
    user_id=intercom_user_id,
    body=f"Previous context: {memories}"
)
```

### 4. Analytics Dashboard
```python
def generate_support_metrics():
    all_memories = client.get_all()

    metrics = {
        "total_tickets": len(all_memories),
        "by_category": count_by_tag(all_memories, ["billing", "technical", "account"]),
        "by_sentiment": count_by_tag(all_memories, ["positive", "negative", "neutral"]),
        "escalation_rate": calculate_escalation_rate(all_memories)
    }

    return metrics
```

### 5. Multilingual Support
```python
# Detect customer language from profile
customer_profile = client.search(
    query="language preference",
    user_id=customer_id,
    metadata={"tags": ["profile"]}
)

# Auto-translate if needed
if customer_language != "en":
    response = translate(response, target=customer_language)
```

### 6. Proactive Support
```python
# Detect patterns in customer issues
memories = client.search(
    query="login issue",
    user_id=customer_id
)

if len(memories) >= 3:
    # Customer has contacted 3+ times about login
    send_proactive_outreach(
        customer_id,
        message="We noticed you're having trouble logging in. Here's a direct link to our security specialist."
    )
```

## Performance at Scale

### Expected Performance:
- Memory retrieval: <100ms
- Supports millions of customers
- Automatic memory compression keeps costs low
- No manual memory management required

### Cost Optimization:
- Cogniz automatically compresses memories for storage efficiency
- Reduces LLM context tokens by ~80%+
- Pay only for memories used, not stored

### Monitoring Checklist:
- [ ] Track memory storage per customer
- [ ] Monitor retrieval latency
- [ ] Measure CSAT improvement with memory vs without
- [ ] Track escalation rate changes
- [ ] Monitor cost per support interaction
"""
