# tests/test_pipeline.py
# Run with: python -m pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mutator import generate_mutations
from runner import make_target
from scorer import score_spec

SORT_SPEC = """
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
"""

# ── Mutator tests ─────────────────────────────────────────────────────────────

def test_mutations_generated():
    """Mutator produces at least one mutation."""
    mutations = generate_mutations(SORT_SPEC)
    assert len(mutations) > 0

def test_mutations_have_label_and_code():
    """Every mutation has a label and code string."""
    mutations = generate_mutations(SORT_SPEC)
    for m in mutations:
        assert 'label' in m
        assert 'code' in m
        assert isinstance(m['code'], str)
        assert len(m['code']) > 0

def test_assert_removal_mutations():
    """There should be one assert-removal mutation per assert."""
    import ast
    tree = ast.parse(SORT_SPEC)
    assert_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))
    mutations = generate_mutations(SORT_SPEC)
    removal_mutations = [m for m in mutations if 'removed assert' in m['label']]
    assert len(removal_mutations) == assert_count

def test_operator_mutations():
    """Operator mutations should exist for <= in the spec."""
    mutations = generate_mutations(SORT_SPEC)
    op_mutations = [m for m in mutations if '<=' in m['label']]
    assert len(op_mutations) > 0

# ── Runner tests ──────────────────────────────────────────────────────────────

def test_correct_impl_passes():
    """Correct sort implementation should pass the spec."""
    runner = make_target(sorted)
    result = runner(SORT_SPEC)
    assert result['passed'] is True

def test_broken_impl_fails():
    """Implementation that always returns [] should fail."""
    runner = make_target(lambda lst: [])
    result = runner(SORT_SPEC)
    assert result['passed'] is False

def test_wrong_length_fails():
    """Implementation that drops elements should fail."""
    def wrong_length(lst): return sorted(lst)[:-1] if lst else []
    runner = make_target(wrong_length)
    result = runner(SORT_SPEC)
    assert result['passed'] is False

def test_runner_returns_error_message():
    """Failed run should include an error message."""
    runner = make_target(lambda lst: [])
    result = runner(SORT_SPEC)
    assert result['error'] is not None

# ── Scorer tests ──────────────────────────────────────────────────────────────

def test_score_has_required_fields():
    """Score report must have all required fields."""
    report = score_spec(SORT_SPEC)
    for field in ['total', 'killed', 'survived', 'survival_rate', 'baseline', 'mutations']:
        assert field in report

def test_score_totals_add_up():
    """killed + survived must equal total."""
    report = score_spec(SORT_SPEC)
    assert report['killed'] + report['survived'] == report['total']

def test_coverage_between_0_and_1():
    """Survival rate must be between 0 and 1."""
    report = score_spec(SORT_SPEC)
    assert 0.0 <= report['survival_rate'] <= 1.0

def test_correct_impl_passes_baseline():
    """Baseline must show correct implementation passing."""
    report = score_spec(SORT_SPEC)
    assert report['baseline'].get('correct') is True

def test_broken_impls_fail_baseline():
    """Baseline must show broken implementations failing."""
    report = score_spec(SORT_SPEC)
    assert report['baseline'].get('wrong_length') is False
    assert report['baseline'].get('not_sorted') is False
    assert report['baseline'].get('always_empty') is False