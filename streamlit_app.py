import os
import streamlit as st
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

# Load API keys
load_dotenv(".env")

# Create clients
hindsight = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

bank_id = "meetmind"


# -----------------------------
# Store meeting history
# -----------------------------

if "meeting_history" not in st.session_state:
    st.session_state.meeting_history = []


# -----------------------------
# Page settings
# -----------------------------

# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:
    st.markdown("## 🧠 MeetMind")

    st.markdown("### AI Meeting Preparation")

    st.divider()

    st.markdown("**Memory Engine**")
    st.success("Hindsight Connected")

    st.markdown("**AI Model**")
    st.info("Groq — GPT-OSS 120B")

    st.divider()

    st.caption(
        "MeetMind remembers important client "
        "information across meetings."
    )

st.title("🧠 MeetMind")

st.markdown(
    "### Your AI-powered client memory assistant"
)

st.markdown(
    "Prepare for your next meeting using everything "
    "MeetMind remembers from previous conversations."
)

st.divider()

st.markdown("### 🧠 How MeetMind Works")

st.info(
    "MeetMind stores important information from your meetings in "
    "Hindsight memory. When you have another meeting, it recalls "
    "relevant past information and prepares a personalized briefing."
)
# -----------------------------
# Ask MeetMind
# -----------------------------

st.markdown("### 💬 Ask MeetMind About This Client")

# -----------------------------
# Ask MeetMind
# -----------------------------

st.markdown("## 💬 Ask MeetMind")

with st.container(border=True):

    st.markdown(
        "Ask questions about what MeetMind remembers "
        "from previous client meetings."
    )

    memory_question = st.text_input(
        "Your question",
        placeholder="Example: What concerns has Acme Corp raised?"
    )

    if st.button("🔍 Ask MeetMind"):

        if memory_question.strip() == "":
            st.warning("Please enter a question.")

        else:

            try:
                result = hindsight.recall(
                    bank_id=bank_id,
                    query=memory_question
                )

                question_memories = "\n".join(
                    memory.text for memory in result.results
                )

            except Exception:
                st.error(
                    "MeetMind could not retrieve memories right now. "
                    "Please try again."
                )
                st.stop()

            if question_memories:

                response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are MeetMind, an AI client-memory assistant.

Answer the user's question using ONLY the
information provided in the Hindsight memories.

Do not guess, infer, or add information.

If the answer is not present in memory,
say: "Not mentioned in memory."

Keep the answer short and factual.
"""
                        },
                        {
                            "role": "user",
                            "content": f"""
Question:
{memory_question}

Hindsight memories:
{question_memories}
"""
                        }
                    ]
                )

                answer = response.choices[0].message.content

                st.markdown("### 🧠 MeetMind's Answer")

                with st.container(border=True):
                    st.markdown(answer)

            else:
                st.info("No relevant memories found.")


# -----------------------------
# Client information
# -----------------------------

st.markdown("## 👤 Client & Meeting")

with st.container(border=True):
    st.markdown("### 👤 Client Information")

    client_name = st.text_input(
        "Client Name",
        value="Acme Corp"
    )

    st.markdown("### 📝 Today's Meeting")

    meeting = st.text_area(
        "What happened in today's meeting?",
        placeholder=(
            "Example: The client said security is still their "
            "biggest concern and asked about a lower-cost plan..."
        ),
        height=160
    )

    st.caption(
        "💡 MeetMind will remember important information from this meeting."
    )


# -----------------------------
# Prepare meeting button
# -----------------------------

if st.button("🚀 Prepare My Meeting"):

    if meeting.strip() == "":
        st.warning("Please enter what happened in today's meeting.")

    else:

        # -----------------------------
        # Store meeting in Hindsight
        # -----------------------------

        try:
            hindsight.retain(
                bank_id=bank_id,
                content=f"""
                New meeting with client {client_name}.
                {meeting}
                """
            )

            st.success("🧠 MeetMind learned from this meeting and stored it in Hindsight memory.")

        except Exception:
            st.error(
                "Hindsight is taking too long to respond. "
                "Please try again in a few seconds."
            )
            st.stop()

        # Store meeting for UI history
        st.session_state.meeting_history.append({
            "client": client_name,
            "notes": meeting
        })

        # -----------------------------
        # Recall relevant memories
        # -----------------------------

        try:
            result = hindsight.recall(
                bank_id=bank_id,
                query=f"""
                What are the important concerns,
                requirements, commitments, and unresolved
                issues of {client_name}?
                """
            )

        except Exception:
            st.error(
                "MeetMind could not retrieve memories right now. "
                "Please try again."
            )
            st.stop()

        memories = "\n".join(
            memory.text for memory in result.results
        )

                # -----------------------------
        # Hindsight Memory
        # -----------------------------

        st.markdown("## 🧠 MeetMind Memory")

        st.caption(
            "Powered by Hindsight • Long-term client memory"
        )

        if memories:

            with st.container(border=True):

                st.markdown(
                    "### 🔎 Relevant memories retrieved from Hindsight"
                )

                st.caption(
                    "These details were recalled from previous client conversations."
                )

                memory_text = memories.lower()

                if "security" in memory_text:
                    st.markdown(
                        "🔐 **Security**  \n"
                        "The client's security and data protection concerns "
                        "are important."
                    )

                if "pricing" in memory_text or "lower-cost" in memory_text:
                    st.markdown(
                        "💰 **Pricing**  \n"
                        "The client has requested a lower-cost pricing plan."
                    )

                if "salesforce" in memory_text:
                    st.markdown(
                        "🔗 **Salesforce Integration**  \n"
                        "Salesforce integration is an important feature for the client."
                    )

                if "partnership" in memory_text:
                    st.markdown(
                        "🤝 **Partnership**  \n"
                        "The client is interested in continuing the partnership."
                    )

        else:
            st.info("No relevant memories found.")
                    # -----------------------------
        # Groq AI Briefing
        # -----------------------------

        st.info(
            "✅ Hindsight memory retrieved. Generating AI meeting brief..."
        )

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": """
You are MeetMind, an AI meeting preparation assistant.

Your job is to summarize the Hindsight memories into a
short, factual meeting briefing.

IMPORTANT RULES:

1. Use ONLY facts explicitly stated in the Hindsight memories.
2. Do NOT infer, assume, predict, or add information.
3. Do NOT invent missing details.
4. Only describe something as unresolved if the Hindsight
   memories explicitly indicate that it is unresolved.
5. If no unresolved issue is explicitly mentioned,
   write: "Not mentioned in memory."
6. If there is not enough information for any section,
   write: "Not mentioned in memory."

Use exactly this format:

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
Prepare me for my next meeting with {client_name}.

Here are the memories retrieved from Hindsight:

{memories}
"""
                }
            ]
        )

        briefing = response.choices[0].message.content

        # -----------------------------
        # AI Meeting Brief
        # -----------------------------

        st.markdown("## 📋 MeetMind AI Meeting Brief")

        with st.container(border=True):

            st.markdown(
                "Here is your personalized preparation based on "
                "**Hindsight memory**:"
            )

            st.markdown(briefing)
            # -----------------------------
# -----------------------------
# Meeting History
# -----------------------------

st.markdown("## 📅 Meeting History")

if st.session_state.meeting_history:

    for i, item in enumerate(
        reversed(st.session_state.meeting_history), 1
    ):

        with st.expander(
            f"Meeting {len(st.session_state.meeting_history) - i + 1} — {item['client']}"
        ):
            st.write(item["notes"])

else:
    st.info("No meetings recorded yet.")