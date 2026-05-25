# runner.py
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

def make_target(impl_func):
    def run_spec(spec_code: str) -> dict:
        namespace = {
            'target':      impl_func,
            'given':       given,
            'settings':    settings,
            'HealthCheck': HealthCheck,
            'st':          st,
        }
        try:
            exec(spec_code, namespace)
            prop_funcs = [
                v for k, v in namespace.items()
                if k.startswith('prop_') and callable(v)
            ]
            if not prop_funcs:
                return {'passed': False, 'error': 'No prop_ functions found'}
            for prop in prop_funcs:
                prop()
            return {'passed': True, 'error': None}
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    return run_spec

def impl_correct(lst): return sorted(lst)
def impl_wrong_length(lst): return sorted(lst)[:-1] if lst else []
def impl_not_sorted(lst): return lst[:]
def impl_always_empty(lst): return []

IMPLEMENTATIONS = {
    'correct':      impl_correct,
    'wrong_length': impl_wrong_length,
    'not_sorted':   impl_not_sorted,
    'always_empty': impl_always_empty,
}