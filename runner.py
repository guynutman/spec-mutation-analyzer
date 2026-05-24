# runner.py
# Takes a spec (Python code string) and an implementation function,
# runs the spec's property tests against that implementation,
# and reports whether the implementation passed or failed.

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

def make_target(impl_func):
    """
    Returns a run_spec() function pre-loaded with a specific implementation.

    Usage:
        runner = make_target(my_sort_function)
        result = runner(spec_code)
        # result = {'passed': True/False, 'error': None or error message}
    """
    def run_spec(spec_code: str) -> dict:
        # Set examples to 500 to prevent non-deteriministic mutation survival with property-based testing (since Hypothesis is random)
        settings.register_profile("thorough", max_examples=500)
        settings.load_profile("thorough")
        
        # Inject the implementation as `target` so the spec can call it
        namespace = {
            'target':     impl_func,
            'given':      given,
            'settings':   settings,
            'HealthCheck':HealthCheck,
            'st':         st,
        }
        try:
            # Execute the spec code to register all prop_ functions
            exec(spec_code, namespace)

            # Find all functions named prop_1, prop_2, etc.
            prop_funcs = [
                v for k, v in namespace.items()
                if k.startswith('prop_') and callable(v)
            ]
            if not prop_funcs:
                return {'passed': False, 'error': 'No prop_ functions found in spec'}

            # Run each property test — Hypothesis generates random inputs automatically
            for prop in prop_funcs:
                prop()

            return {'passed': True, 'error': None}

        except Exception as e:
            return {'passed': False, 'error': str(e)}

    return run_spec


# ── Four implementations to test against ──────────────────────────────────────
# These range from correct to intentionally broken,
# so we can verify the spec catches real bugs.

def impl_correct(lst):
    """Correct: returns a properly sorted list."""
    return sorted(lst)

def impl_wrong_length(lst):
    """Buggy: sorts correctly but drops the last element."""
    return sorted(lst)[:-1] if lst else []

def impl_not_sorted(lst):
    """Buggy: returns the list in its original unsorted order."""
    return lst[:]

def impl_always_empty(lst):
    """Buggy: always returns an empty list regardless of input."""
    return []

IMPLEMENTATIONS = {
    'correct':      impl_correct,
    'wrong_length': impl_wrong_length,
    'not_sorted':   impl_not_sorted,
    'always_empty': impl_always_empty,
}


if __name__ == "__main__":
    from llm_client import generate_spec

    spec = generate_spec("a function that sorts a list of integers")

    print("Running base spec against all implementations:\n")
    for name, impl in IMPLEMENTATIONS.items():
        runner = make_target(impl)
        result = runner(spec)
        status = "PASS" if result['passed'] else "FAIL"
        print(f"  {name:20s} → {status}")
        if result['error']:
            print(f"    reason: {result['error'][:80]}")