# llm_client.py
# Calls Gemini API to generate a Hypothesis spec from plain English.
# Falls back to hardcoded spec if API quota is exhausted.

from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SPEC_PROMPT = """You are a formal specification expert. Given a function description, write
property-based tests using Python's Hypothesis library that fully specify
the correct behavior.

Rules:
- Use @given and strategies from hypothesis
- Each property should be a separate function named prop_1, prop_2, etc.
- Test the function called `target`
- Output ONLY raw Python code, no explanation, no markdown fences
- Do not import anything — assume hypothesis is already imported
- Do NOT write redundant clauses. Every assertion must be logically
  independent — removing it must change which implementations pass or fail.
  If an assertion is implied by the others, leave it out.
"""

# Hardcoded fallback specs for each test case (used if API quota fails)
FALLBACK_SPECS = {
    "sort": """
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def prop_1(lst):
    result = target(lst)
    assert len(result) == len(lst)

@given(st.lists(st.integers()))
def prop_2(lst):
    result = target(lst)
    assert sorted(result) == sorted(lst)

@given(st.lists(st.integers()))
def prop_3(lst):
    result = target(lst)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]
""",
    "max": """
from hypothesis import given, strategies as st

@given(st.lists(st.integers(), min_size=1))
def prop_1(lst):
    result = target(lst)
    assert result in lst

@given(st.lists(st.integers(), min_size=1))
def prop_2(lst):
    result = target(lst)
    assert all(result >= x for x in lst)

@given(st.lists(st.integers(), min_size=1))
def prop_3(lst):
    result = target(lst)
    assert result == sorted(lst)[-1]
""",
    "palindrome": """
from hypothesis import given, strategies as st

@given(st.text())
def prop_1(s):
    result = target(s)
    assert isinstance(result, bool)

@given(st.text())
def prop_2(s):
    result = target(s)
    assert result == (s == s[::-1])

@given(st.text())
def prop_3(s):
    if target(s):
        assert s == s[::-1]
""",
    "median": """
from hypothesis import given, strategies as st

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def prop_1(lst):
    result = target(lst)
    assert min(lst) <= result <= max(lst)

@given(st.lists(st.integers(), min_size=1))
def prop_2(lst):
    s = sorted(lst)
    n = len(s)
    result = target(lst)
    if n % 2 == 1:
        assert result == s[n // 2]
    else:
        assert result == (s[n // 2 - 1] + s[n // 2]) / 2
""",
    "dedup": """
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def prop_1(lst):
    result = target(lst)
    assert len(result) == len(set(result))

@given(st.lists(st.integers()))
def prop_2(lst):
    result = target(lst)
    assert set(result) == set(lst)

@given(st.lists(st.integers()))
def prop_3(lst):
    result = target(lst)
    seen = []
    for x in lst:
        if x not in seen:
            seen.append(x)
    assert result == seen
""",
    "binary_search": """
from hypothesis import given, strategies as st

@given(st.lists(st.integers(), min_size=1).map(sorted), st.integers())
def prop_1(lst, target_val):
    result = target(lst, target_val)
    if target_val in lst:
        assert result >= 0
        assert lst[result] == target_val
    else:
        assert result == -1

@given(st.lists(st.integers(), min_size=1).map(sorted))
def prop_2(lst):
    for val in lst:
        result = target(lst, val)
        assert result >= 0
""",
    "flatten": """
from hypothesis import given, strategies as st

def nested_lists(draw):
    return draw(st.lists(st.one_of(st.integers(), st.lists(st.integers(), max_size=3)), max_size=5))

@given(st.lists(st.one_of(st.integers(), st.lists(st.integers(), max_size=3)), max_size=5))
def prop_1(lst):
    result = target(lst)
    assert isinstance(result, list)
    assert all(isinstance(x, int) for x in result)

@given(st.lists(st.integers()))
def prop_2(lst):
    result = target(lst)
    assert result == lst
""",
    "group_even_odd": """
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def prop_1(lst):
    result = target(lst)
    assert 'even' in result and 'odd' in result

@given(st.lists(st.integers()))
def prop_2(lst):
    result = target(lst)
    assert all(x % 2 == 0 for x in result['even'])
    assert all(x % 2 != 0 for x in result['odd'])

@given(st.lists(st.integers()))
def prop_3(lst):
    result = target(lst)
    assert sorted(result['even'] + result['odd']) == sorted(lst)
""",
    "merge_sorted": """
from hypothesis import given, strategies as st

@given(st.lists(st.integers()).map(sorted), st.lists(st.integers()).map(sorted))
def prop_1(a, b):
    result = target(a, b)
    assert len(result) == len(a) + len(b)

@given(st.lists(st.integers()).map(sorted), st.lists(st.integers()).map(sorted))
def prop_2(a, b):
    result = target(a, b)
    assert sorted(result) == sorted(a + b)

@given(st.lists(st.integers()).map(sorted), st.lists(st.integers()).map(sorted))
def prop_3(a, b):
    result = target(a, b)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]
"""
}

def generate_spec(description: str, fallback_key: str = "") -> str:
    """
    Tries Gemini API first. If quota is exhausted, uses fallback spec.
    fallback_key: key into FALLBACK_SPECS dict (e.g. 'sort', 'median')
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=SPEC_PROMPT.format(description=description)
        )
        if response.text is None:
            raise ValueError("Empty response from Gemini")
        print(f"  [API] Gemini generated spec successfully.")
        return response.text
    except Exception as e:
        print(f"  [FALLBACK] API unavailable ({str(e)[:60]}...). Using hardcoded spec.")
        if fallback_key and fallback_key in FALLBACK_SPECS:
            return FALLBACK_SPECS[fallback_key]
        # Default fallback
        return FALLBACK_SPECS["sort"]


if __name__ == "__main__":
    spec = generate_spec("a function that sorts a list of integers", fallback_key="sort")
    print(spec)