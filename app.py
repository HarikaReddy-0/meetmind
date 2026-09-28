import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq
load_dotenv(".env")

groq_key = os.getenv("GROQ_API_KEY")

print("Groq key loaded:", bool(groq_key))

groq_client = Groq(
    api_key=groq_key
)

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

bank_id = "meetmind"

# Ask the user for today's meeting
meeting = input("What happened in today's meeting?\n> ")

# Store the new meeting in Hindsight
client.retain(
    bank_id=bank_id,
    content=f"""
    New meeting with client Acme Corp.
    {meeting}
    """
)

print("\nMeeting stored successfully!")

# Recall everything important about the client
result = client.recall(
    bank_id=bank_id,
    query="What are the important concerns, requirements, and unresolved issues of Acme Corp?"
)

print("\n--- MEETMIND MEMORY ---")

# Combine Hindsight memories into one text
memories = "\n".join(
    memory.text for memory in result.results
)

# Ask Groq to create a meeting briefing
response = groq_client.chat.completions.create(
    model="openai/gpt-oss-120b",
            messages=[
    {
        "role": "system",
        "content": """
You are MeetMind, an AI meeting preparation assistant.

Create a short meeting briefing using ONLY the information
provided in the Hindsight memories.

Do not add assumptions, examples, recommendations, technical
details, or facts that are not explicitly present in the memories.

If something is not mentioned in the memories, say:
"Not mentioned in memory."

Use this format:

MEETING BRIEF

Key Concerns:
- ...

Important Requirements:
- ...

Unresolved Issues:
- ...

What to Remember:
- ...

Keep the briefing concise and factual.
"""
    },
        {
            "role": "user",
            "content": f"""
            Prepare me for my next meeting with Acme Corp.

            Here are the memories retrieved from Hindsight:

            {memories}
            """
        }
    ]
)

# Display the AI-generated briefing
print("\n--- MEETMIND AI MEETING BRIEF ---")
print(response.choices[0].message.content)

client.close()