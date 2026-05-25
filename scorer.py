# scorer.py
import ast
from runner import make_target, IMPLEMENTATIONS
from mutator import generate_mutations

def score_spec(spec_code: str) -> dict:
    # Baseline
    baseline = {}
    for name, impl in IMPLEMENTATIONS.items():
        runner = make_target(impl)
        baseline[name] = runner(spec_code)['passed']

    # Mutations
    mutations = generate_mutations(spec_code)
    results = []
    for mutation in mutations:
        mutation_results = {}
        for name, impl in IMPLEMENTATIONS.items():
            runner = make_target(impl)
            mutation_results[name] = runner(mutation['code'])['passed']
        survived = (mutation_results == baseline)
        results.append({
            'label':    mutation['label'],
            'results':  mutation_results,
            'survived': survived,
        })

    total = len(results)
    survived_count = sum(1 for r in results if r['survived'])
    killed_count = total - survived_count

    return {
        'baseline':      baseline,
        'mutations':     results,
        'total':         total,
        'survived':      survived_count,
        'killed':        killed_count,
        'survival_rate': survived_count / total if total > 0 else 0,
        'coverage':      round((killed_count / total) * 100, 1) if total > 0 else 0,
    }