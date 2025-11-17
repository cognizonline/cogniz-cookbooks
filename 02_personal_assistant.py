"""
Personal AI Assistant with Memory

Build an AI assistant that learns your preferences over time

Difficulty: Beginner
Time: 15 minutes

Use Case:
- Remember user preferences and habits
- Provide personalized recommendations
- Learn from every interaction
- Adapt responses based on context

Prerequisites:
- cogniz>=1.0.0
- openai>=1.0.0
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
from typing import Optional


class PersonalAssistant:
    """
    Memory-powered personal AI assistant.

    Features:
    - Learns user preferences automatically
    - Remembers past conversations
    - Provides personalized responses
    - Adapts over time
    """

    def __init__(
        self,
        user_id: str,
        cogniz_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        self.user_id = user_id
        self.cogniz = Client(api_key=cogniz_api_key or os.getenv("COGNIZ_API_KEY", project_id="default")
        )
        self.openai = OpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )

    def chat(self, message: str) -> str:
        """
        Process user message with memory context.
        """
        print(f"\n{'='*60}")
        print(f" You: {message}")
        print(f"{'='*60}\n")

        # Retrieve relevant memories
        print(" Searching memory...")
        memories = self.cogniz.search(
            query=message,
            user_id=self.user_id,
            limit=5
        )

        print(f" Found {len(memories)} relevant memories")

        # Build context
        context = self._build_context(memories)

        # Generate response
        print(" Generating response...")
        response = self._generate_response(message, context)

        print(f"\n Assistant: {response}\n")

        # Store this interaction
        self._store_interaction(message, response)

        return response

    def _build_context(self, memories):
        """Build context string from memories."""
        if not memories:
            return "No previous context available."

        context = "Previous context about user:\n"
        for mem in memories[:3]:
            context += f"- {mem['content']}\n"

        return context

    def _generate_response(self, message: str, context: str) -> str:
        """Generate response using LLM with memory context."""
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful personal assistant. Use the context about the user to provide personalized responses.\n\n{context}"
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"I'm having trouble right now. Error: {str(e)}"

    def _store_interaction(self, message: str, response: str):
        """Store interaction in memory."""
        # Detect if this contains preference information
        is_preference = any(word in message.lower()
                          for word in ["prefer", "like", "favorite", "love", "hate", "always", "never"])

        # Store user message if it contains useful info
        if is_preference or len(message.split()) > 5:
            self.cogniz.store(
                content=message,
                user_id=self.user_id,
                metadata={"tags": ["conversation", "preference" if is_preference else "general"]}
            )


# =============================================================================
# DEMO SCENARIOS
# =============================================================================

def demo_learning_preferences():
    """
    Demo: Assistant learns preferences over time
    """
    print("\n" + "="*80)
    print("DEMO 1: Learning User Preferences")
    print("="*80)

    assistant = PersonalAssistant(user_id="demo_user_001")

    # Conversation where assistant learns about user
    messages = [
        "Hi! I'm Alex and I work from home as a software engineer",
        "I prefer morning meetings before 10 AM",
        "I'm vegetarian and love Italian food",
        "Can you suggest a good restaurant for lunch tomorrow?"
    ]

    for msg in messages:
        response = assistant.chat(msg)

    print(" Notice: The assistant's last response is personalized!")
    print("   - Knows user works from home")
    print("   - Suggests vegetarian Italian restaurant")
    print("   - Recommends lunch time (not dinner)")
    print()


def demo_remembering_context():
    """
    Demo: Assistant remembers previous conversations
    """
    print("\n" + "="*80)
    print("DEMO 2: Remembering Previous Context")
    print("="*80)

    assistant = PersonalAssistant(user_id="demo_user_002")

    # First conversation
    print("--- Day 1 ---")
    assistant.chat("I'm starting a new fitness routine, running 3 times a week")

    # Later conversation
    print("\n--- Day 3 ---")
    response = assistant.chat("How's my fitness plan going?")

    print(" Notice: Assistant remembers the fitness routine from Day 1!")
    print()


def demo_personalized_recommendations():
    """
    Demo: Personalized recommendations based on memory
    """
    print("\n" + "="*80)
    print("DEMO 3: Personalized Recommendations")
    print("="*80)

    assistant = PersonalAssistant(user_id="demo_user_003")

    # Build up preferences
    assistant.chat("I love sci-fi movies, especially space exploration themes")
    assistant.chat("My favorite book series is The Expanse")

    # Get recommendation
    response = assistant.chat("Can you recommend a movie for tonight?")

    print(" Notice: Recommendation is based on stored preferences!")
    print()


def demo_complete_example():
    """
    Complete example: Day in the life with personal assistant
    """
    print("\n" + "="*80)
    print("COMPLETE EXAMPLE: A Day with Your Personal Assistant")
    print("="*80)

    assistant = PersonalAssistant(user_id="alex_001")

    # Morning
    print("\n--- 8:00 AM: Morning Briefing ---")
    assistant.chat("Good morning! What's on my schedule today?")

    # Store meeting
    assistant.chat("I have a client meeting at 2 PM, need to prepare presentation")

    # Midday
    print("\n--- 12:00 PM: Lunch Break ---")
    assistant.chat("What should I have for lunch?")

    # Afternoon check-in
    print("\n--- 1:30 PM: Pre-meeting ---")
    assistant.chat("What do I need to remember for my 2 PM meeting?")

    # Evening
    print("\n--- 6:00 PM: End of day ---")
    assistant.chat("How was my day? What did I accomplish?")

    print("\n Throughout the day, the assistant:")
    print("   - Remembered your schedule")
    print("   - Tracked your tasks")
    print("   - Provided relevant reminders")
    print("   - Built a timeline of your day")
    print()


def main():
    """
    Run all demos
    """
    print("\n" + "="*80)
    print(" PERSONAL AI ASSISTANT DEMO")
    print("="*80)

    demo_learning_preferences()
    demo_remembering_context()
    demo_personalized_recommendations()
    demo_complete_example()

    print("="*80)
    print(" DEMO COMPLETE")
    print("="*80)
    print()
    print("What you learned:")
    print("   How to build a learning AI assistant")
    print("   Memory-based personalization")
    print("   Context-aware conversations")
    print("   Preference tracking over time")
    print()
    print("Next steps:")
    print("  1. Add task management features")
    print("  2. Integrate with calendar APIs")
    print("  3. Add proactive reminders")
    print("  4. Build mobile app interface")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# PRODUCTION ENHANCEMENTS
# =============================================================================

"""
## Advanced Features

### 1. Task Management
```python
def add_task(self, task: str, due_date: str):
    self.cogniz.store(
        content=f"Task: {task} (due: {due_date})",
        user_id=self.user_id,
        metadata={"tags": ["task", "todo"]},
        metadata={"due_date": due_date, "status": "pending"}
    )

def get_tasks(self):
    return self.cogniz.search(
        query="tasks",
        user_id=self.user_id,
        metadata={"tags": ["task"]}
    )
```

### 2. Calendar Integration
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

def sync_calendar(self):
    # Get calendar events
    events = calendar_service.events().list().execute()

    # Store in memory
    for event in events['items']:
        self.cogniz.store(
            content=f"Calendar: {event['summary']} at {event['start']}",
            user_id=self.user_id,
            metadata={"tags": ["calendar", "schedule"]}
        )
```

### 3. Proactive Reminders
```python
from datetime import datetime, timedelta

def check_reminders(self):
    # Get upcoming tasks
    memories = self.cogniz.search(
        query="upcoming tasks",
        user_id=self.user_id,
        metadata={"tags": ["task"]}
    )

    # Check due dates
    for mem in memories:
        due_date = mem['metadata'].get('due_date')
        if due_date and is_due_soon(due_date):
            send_reminder(self.user_id, mem['content'])
```

### 4. Learning User Patterns
```python
def analyze_patterns(self):
    memories = self.cogniz.get_all(user_id=self.user_id)

    # Analyze time patterns
    morning_tasks = [m for m in memories if "morning" in m['content']]
    evening_tasks = [m for m in memories if "evening" in m['content']]

    # Generate insights
    return {
        "preferred_work_time": "morning" if len(morning_tasks) > len(evening_tasks) else "evening",
        "common_activities": extract_common_themes(memories),
        "productivity_patterns": analyze_productivity(memories)
    }
```

### 5. Multi-Device Sync
```python
# Store device-specific preferences
def store_device_context(self, device_type: str):
    self.cogniz.store(
        content=f"User active on {device_type}",
        user_id=self.user_id,
        metadata={"tags": ["device", device_type]},
        metadata={"timestamp": datetime.now().isoformat()}
    )

# Retrieve works across all devices
memories = self.cogniz.search(
    query=query,
    user_id=self.user_id
    # Automatically includes context from phone, laptop, tablet
)
```

### 6. Voice Interface
```python
import speech_recognition as sr
from gtts import gTTS

def voice_chat(self):
    # Listen
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    # Convert to text
    message = recognizer.recognize_google(audio)

    # Process with memory
    response = self.chat(message)

    # Speak response
    tts = gTTS(response)
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")
```

## Privacy & Security

### User Data Export
```python
def export_my_data(self):
    memories = self.cogniz.get_all(user_id=self.user_id)

    # Export to JSON
    with open(f"my_data_{self.user_id}.json", "w") as f:
        json.dump(memories, f, indent=2)

    return f"Exported {len(memories)} memories"
```

### Data Deletion
```python
def delete_my_data(self):
    self.cogniz.delete_all(user_id=self.user_id)
    print("All personal data deleted")
```

### Memory Categories
```python
def organize_memories(self):
    memories = self.cogniz.get_all(user_id=self.user_id)

    categories = {
        "preferences": [],
        "tasks": [],
        "conversations": [],
        "schedule": []
    }

    for mem in memories:
        tags = mem.get('tags', [])
        for category in categories:
            if category in tags:
                categories[category].append(mem)

    return categories
```

## Performance Tips

- Limit memory search to top 3-5 results for faster responses
- Use tags for efficient filtering
- Store only meaningful information, skip small talk
- Update memories instead of creating duplicates
- Set memory expiration for temporary information
"""
