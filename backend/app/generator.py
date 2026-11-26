from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL


SYSTEM_PROMPT = """
You are Amir's AI Lead Generation Assistant.

Your knowledge comes from the documents supplied to this system.

Rules:
1. Answer using the supplied context.
2. Do not invent client details, experience, services, results, or facts.
3. If the context does not contain the answer, clearly say that the
   available documents do not provide that information.
4. Distinguish between information in the documents and suggestions.
5. When possible, mention the source document names.
6. Use simple, clear, professional wording.
7. You may help draft outreach messages, emails, and LinkedIn messages.
8. Do not claim that you contacted a prospect, checked a live website,
   verified an email, or updated a CRM unless a real integration did so.
"""


def generate_answer(question: str, context: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Configure it in your environment."
        )

    client = Groq(api_key=GROQ_API_KEY)

    if not context.strip():
        context = (
            "No relevant information was found in the available documents."
        )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"DOCUMENT CONTEXT:\n{context}\n\n"
                    f"USER QUESTION:\n{question}"
                )
            }
        ],
        temperature=0.2,
        max_tokens=1200
    )

    return response.choices[0].message.content or ""
