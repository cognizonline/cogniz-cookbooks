"""
Travel Planning Assistant with Memory

Build a travel assistant that remembers preferences and past trips

Difficulty: Beginner
Time: 15 minutes

Use Case:
- Remember travel preferences (budget, accommodation style, activities)
- Track past destinations and experiences
- Provide personalized recommendations
- Build trip itineraries based on user history

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
from typing import Optional, List, Dict


class TravelAssistant:
    """
    Memory-powered travel planning assistant.

    Features:
    - Remembers travel preferences
    - Tracks visited destinations
    - Provides personalized recommendations
    - Learns from past trips
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

    def plan_trip(self, destination: str, duration: str) -> str:
        """
        Plan a trip with personalized recommendations.
        """
        print(f"\n{'='*60}")
        print(f"️  Planning trip to {destination} for {duration}")
        print(f"{'='*60}\n")

        # Retrieve travel preferences
        print(" Retrieving your travel profile...")
        preferences = self.cogniz.search(
            query="travel preferences accommodation budget activities",
            user_id=self.user_id,
            limit=10
        )

        print(f" Found {len(preferences)} preferences")

        # Get past trips for context
        past_trips = self.cogniz.search(
            query=f"visited {destination} past trips",
            user_id=self.user_id,
            metadata={"tags": ["trip"]},
            limit=5
        )

        print(f" Found {len(past_trips)} past trips for context")

        # Generate itinerary
        print("️  Generating personalized itinerary...")
        itinerary = self._generate_itinerary(
            destination, duration, preferences, past_trips
        )

        print(f"\n Itinerary:\n{itinerary}\n")

        # Store this trip plan
        self._store_trip(destination, duration, itinerary)

        return itinerary

    def store_preference(self, preference: str):
        """Store travel preference."""
        print(f" Storing preference: {preference}")

        self.cogniz.store(
            content=preference,
            user_id=self.user_id,
            metadata={"tags": ["preference", "travel"]}
        )

        print(" Preference saved\n")

    def record_trip(self, destination: str, experience: str):
        """Record completed trip experience."""
        print(f" Recording trip to {destination}")

        self.cogniz.store(
            content=f"Visited {destination}. Experience: {experience}",
            user_id=self.user_id,
            metadata={"tags": ["trip", "visited", destination.lower()]}
        )

        print(" Trip recorded\n")

    def get_recommendations(self, query: str) -> List[str]:
        """Get personalized travel recommendations."""
        print(f" Searching recommendations for: {query}")

        # Get user preferences
        preferences = self.cogniz.search(
            query=query,
            user_id=self.user_id,
            limit=5
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(query, preferences)

        print(f"\n Recommendations:\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        print()

        return recommendations

    def _generate_itinerary(
        self,
        destination: str,
        duration: str,
        preferences: List[Dict],
        past_trips: List[Dict]
    ) -> str:
        """Generate personalized itinerary using LLM."""
        # Build context from preferences
        context = "User's travel preferences:\n"
        for pref in preferences[:5]:
            context += f"- {pref['content']}\n"

        if past_trips:
            context += "\nPast trips:\n"
            for trip in past_trips[:3]:
                context += f"- {trip['content']}\n"

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a travel planning assistant. Create a personalized itinerary based on user preferences.\n\n{context}"
                    },
                    {
                        "role": "user",
                        "content": f"Create a {duration} itinerary for {destination}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Unable to generate itinerary: {str(e)}"

    def _generate_recommendations(self, query: str, preferences: List[Dict]) -> List[str]:
        """Generate recommendations based on preferences."""
        context = "User preferences:\n" + "\n".join([p['content'] for p in preferences[:5]])

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a travel advisor. Provide 3 specific recommendations based on user preferences.\n\n{context}"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )

            # Parse recommendations (simple split by newlines)
            recommendations = [line.strip("- ").strip()
                             for line in response.choices[0].message.content.split("\n")
                             if line.strip() and not line.strip().endswith(":")]

            return recommendations[:3] if recommendations else ["Unable to generate recommendations"]

        except Exception as e:
            return [f"Error: {str(e)}"]

    def _store_trip(self, destination: str, duration: str, itinerary: str):
        """Store planned trip in memory."""
        self.cogniz.store(
            content=f"Planned {duration} trip to {destination}",
            user_id=self.user_id,
            metadata={"tags": ["trip", "planned", destination.lower()]},
            metadata={"destination": destination, "duration": duration}
        )


# =============================================================================
# DEMO SCENARIOS
# =============================================================================

def demo_first_time_traveler():
    """Demo: First-time user sets preferences"""
    print("\n" + "="*80)
    print("DEMO 1: First-Time Traveler - Setting Preferences")
    print("="*80)

    assistant = TravelAssistant(user_id="traveler_001")

    # Store preferences
    assistant.store_preference("Budget traveler, prefer hostels or Airbnb")
    assistant.store_preference("Love hiking and outdoor activities")
    assistant.store_preference("Vegetarian, looking for local cuisine")
    assistant.store_preference("Prefer off-the-beaten-path destinations")

    # Plan trip
    itinerary = assistant.plan_trip("Iceland", "7 days")

    print(" Notice: Itinerary is personalized based on stored preferences!")
    print()


def demo_returning_traveler():
    """Demo: Returning user with travel history"""
    print("\n" + "="*80)
    print("DEMO 2: Returning Traveler with History")
    print("="*80)

    assistant = TravelAssistant(user_id="traveler_002")

    # Record past trips
    assistant.record_trip("Japan", "Amazing food, loved temples in Kyoto")
    assistant.record_trip("Thailand", "Great beaches, too touristy in Bangkok")

    # Store preferences learned from trips
    assistant.store_preference("Prefer cultural experiences over beach resorts")
    assistant.store_preference("Budget: $100-150 per day")

    # Plan new trip
    itinerary = assistant.plan_trip("Vietnam", "10 days")

    print(" Notice: Assistant avoids touristy areas based on Thailand experience!")
    print(" Notice: Recommends cultural sites similar to Japan!")
    print()


def demo_recommendations():
    """Demo: Get personalized recommendations"""
    print("\n" + "="*80)
    print("DEMO 3: Personalized Recommendations")
    print("="*80)

    assistant = TravelAssistant(user_id="traveler_003")

    # Set preferences
    assistant.store_preference("Love adventure sports - skiing, surfing, hiking")
    assistant.store_preference("Prefer cold climates")
    assistant.store_preference("Budget: luxury travel, $300+/day")

    # Get recommendations
    recommendations = assistant.get_recommendations("Where should I go in winter?")

    print(" Notice: Recommendations match preferences (cold, adventure, luxury)!")
    print()


def demo_complete_workflow():
    """Complete workflow: Profile → Research → Plan → Record"""
    print("\n" + "="*80)
    print("COMPLETE EXAMPLE: End-to-End Travel Planning")
    print("="*80)

    assistant = TravelAssistant(user_id="sarah_travel")

    # Step 1: Build profile
    print("\n--- Step 1: Building Travel Profile ---")
    assistant.store_preference("Solo female traveler, safety is priority")
    assistant.store_preference("Love photography and nature")
    assistant.store_preference("Budget: mid-range, $80-120/day")
    assistant.store_preference("Prefer small cities and towns over big cities")

    # Step 2: Get recommendations
    print("\n--- Step 2: Exploring Destinations ---")
    destinations = assistant.get_recommendations("Safe destinations for solo female travelers in Europe")

    # Step 3: Plan trip
    print("\n--- Step 3: Planning Trip ---")
    itinerary = assistant.plan_trip("Portugal", "14 days")

    # Step 4: After trip - record experience
    print("\n--- Step 4: After Trip - Recording Experience ---")
    assistant.record_trip("Portugal", "Beautiful country! Loved Porto and Lisbon. Great for solo travelers. Would recommend longer stay in smaller coastal towns.")

    print("\n Complete workflow demonstrated!")
    print("   Next trip: Assistant will remember Portugal experience")
    print()


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("️  TRAVEL ASSISTANT DEMO")
    print("="*80)

    demo_first_time_traveler()
    demo_returning_traveler()
    demo_recommendations()
    demo_complete_workflow()

    print("="*80)
    print(" DEMO COMPLETE")
    print("="*80)
    print()
    print("What you learned:")
    print("   Store travel preferences and history")
    print("   Generate personalized itineraries")
    print("   Get recommendations based on past trips")
    print("   Build travel profile over time")
    print()
    print("Next steps:")
    print("  1. Integrate with booking APIs (Expedia, Booking.com)")
    print("  2. Add real-time pricing data")
    print("  3. Build mobile app for travel logs")
    print("  4. Add photo memory features")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# PRODUCTION ENHANCEMENTS
# =============================================================================

"""
## Advanced Features

### 1. Flight & Hotel Search Integration
```python
def search_flights(self, origin: str, destination: str, dates: str):
    # Get user preferences
    prefs = self.cogniz.search(
        query="flight preferences airline class",
        user_id=self.user_id
    )

    # Search flights with preferences
    results = flight_api.search(
        origin=origin,
        destination=destination,
        dates=dates,
        class="economy" if "budget" in str(prefs) else "business"
    )

    return results
```

### 2. Budget Tracking
```python
def track_budget(self, trip_id: str, expense: dict):
    self.cogniz.store(
        content=f"Spent ${expense['amount']} on {expense['category']}",
        user_id=self.user_id,
        metadata={"tags": ["expense", trip_id]},
        metadata=expense
    )

def get_trip_expenses(self, trip_id: str):
    expenses = self.cogniz.search(
        query="expenses",
        user_id=self.user_id,
        metadata={"tags": [trip_id]}
    )

    total = sum(float(e['metadata']['amount']) for e in expenses)
    return {"expenses": expenses, "total": total}
```

### 3. Travel Companions
```python
def plan_group_trip(self, destination: str, traveler_ids: List[str]):
    # Get preferences for all travelers
    all_preferences = []
    for traveler_id in traveler_ids:
        prefs = self.cogniz.search(
            query="travel preferences",
            user_id=traveler_id
        )
        all_preferences.extend(prefs)

    # Find common interests
    common = find_common_preferences(all_preferences)

    # Generate group itinerary
    return generate_group_itinerary(destination, common)
```

### 4. Real-Time Updates
```python
def get_travel_alerts(self, destination: str):
    # Check memory for past issues
    past_issues = self.cogniz.search(
        query=f"{destination} problems issues weather",
        user_id=self.user_id
    )

    # Get real-time alerts
    alerts = travel_alert_api.get(destination)

    # Combine with user's past experiences
    return {
        "current_alerts": alerts,
        "past_experiences": past_issues
    }
```

### 5. Photo Memory
```python
def store_trip_photos(self, trip_id: str, photos: List[str]):
    for photo_url in photos:
        # Extract location and objects from photo
        analysis = vision_api.analyze(photo_url)

        # Store photo memory
        self.cogniz.store(
            content=f"Photo from {analysis['location']}: {analysis['description']}",
            user_id=self.user_id,
            metadata={"tags": ["photo", trip_id, analysis['location']}],
            metadata={"url": photo_url, "analysis": analysis}
        )
```

### 6. Local Recommendations
```python
def get_local_tips(self, destination: str):
    # Check if user has been there
    past_visit = self.cogniz.search(
        query=f"visited {destination}",
        user_id=self.user_id
    )

    if past_visit:
        return f"You've been to {destination} before! Your notes: {past_visit[0]['content']}"
    else:
        # Get recommendations from other users who match profile
        similar_travelers = find_similar_travelers(self.user_id)
        their_trips = get_their_experiences(similar_travelers, destination)
        return aggregate_recommendations(their_trips)
```

## Integration Examples

### Booking.com API
```python
def search_accommodations(self, destination: str, dates: str):
    # Get accommodation preferences
    prefs = self.cogniz.search(
        query="accommodation hotel hostel airbnb preferences",
        user_id=self.user_id
    )

    budget_range = extract_budget(prefs)

    # Search with preferences
    results = booking_api.search(
        destination=destination,
        checkin=dates['checkin'],
        checkout=dates['checkout'],
        price_min=budget_range['min'],
        price_max=budget_range['max']
    )

    return results
```

### Google Maps Integration
```python
def create_map_itinerary(self, destination: str, itinerary: str):
    # Parse locations from itinerary
    locations = extract_locations(itinerary)

    # Create custom Google Map
    map_url = google_maps.create_custom_map(
        title=f"Trip to {destination}",
        locations=locations
    )

    # Store map in memory
    self.cogniz.store(
        content=f"Map for {destination}: {map_url}",
        user_id=self.user_id,
        metadata={"tags": ["map", destination]}
    )

    return map_url
```

## Performance Tips
- Store trip summaries, not day-by-day details
- Use tags for efficient filtering by destination
- Limit memory search to relevant trip history
- Update preferences after each trip
- Archive old trips after 2 years
"""
