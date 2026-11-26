
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer using Groq and retrieved context.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not context.strip():
        raise ValueError("No context provided.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Amir's AI Lead Generation Assistant. "
                    "Answer questions using only the supplied context. "
                    "Do not invent information or unsupported facts. "
                    "If the answer is missing, clearly say that "
                    "the provided documents do not contain the answer. "
                    "Use simple, professional language."
                )
            },
            {
                "role": "user",
                "content": (
                    f"CONTEXT:\n{context}\n\n"
                    f"QUESTION:\n{question}"
                )
            }
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content

    return answer or "I could not generate an answer."
