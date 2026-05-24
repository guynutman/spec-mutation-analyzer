# llm_client.py
# Calls the Gemini API with a plain-English function description
# and returns a Python Hypothesis spec (property-based tests).

from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# This prompt tells Gemini exactly what format to return
SPEC_PROMPT = """
You are a formal specification expert. Given a function description, write
property-based tests using Python's Hypothesis library that fully specify
the correct behavior.

Rules:
- Use @given and strategies from hypothesis
- Each property should be a separate function named prop_1, prop_2, etc.
- Test the function called `target`
- Output ONLY raw Python code, no explanation, no markdown fences

Function description: {description}
"""

def generate_spec(description: str) -> str:
    """
    Takes a plain-English function description like:
      "a function that sorts a list of integers"
    Returns Python code containing Hypothesis property tests.
    """

    # --- TEMPORARY: hardcoded spec so we can build without burning API quota ---
    # When ready to use real API, delete this block and uncomment the API call below
    return """
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def prop_1(lst):
    # Property: output must be same length as input
    result = target(lst)
    assert len(result) == len(lst)

@given(st.lists(st.integers()))
def prop_2(lst):
    # Property: output must contain exactly the same elements
    result = target(lst)
    assert sorted(result) == sorted(lst)

@given(st.lists(st.integers()))
def prop_3(lst):
    # Property: every element must be <= the next (i.e. sorted)
    result = target(lst)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]
"""

    # --- REAL API CALL (uncomment when quota is available) ---
    # response = client.models.generate_content(
    #     model="gemini-2.0-flash",
    #     contents=SPEC_PROMPT.format(description=description)
    # )
    # if response.text is None:
    #     raise ValueError("Gemini returned an empty response")
    # return response.text


if __name__ == "__main__":
    print("Generating spec for: 'a function that sorts a list of integers'")
    print()
    spec = generate_spec("a function that sorts a list of integers")
    print(spec)