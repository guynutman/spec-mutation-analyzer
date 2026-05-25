# experiments/run_experiments.py
# Runs the full spec mutation survival analysis on all 9 test cases.
# Saves results to experiments/results/results.json
# Prints a summary table for copy-pasting into the report.

import sys
import os
import json
from datetime import datetime

# Allow imports from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_client import generate_spec
from mutator import generate_mutations
from runner import make_target
from test_cases import make_cases

def score_with_custom_impls(spec_code, implementations):
    """
    Same as scorer.score_spec but uses the test case's own implementations
    instead of the hardcoded ones in runner.py.
    """
    # Baseline
    baseline = {}
    for name, impl in implementations.items():
        runner = make_target(impl)
        result = runner(spec_code)
        baseline[name] = result['passed']

    # Mutations
    mutations = generate_mutations(spec_code)
    results = []
    for mutation in mutations:
        mutation_results = {}
        for name, impl in implementations.items():
            runner = make_target(impl)
            result = runner(mutation['code'])
            mutation_results[name] = result['passed']

        survived = (mutation_results == baseline)
        results.append({
            'label':    mutation['label'],
            'results':  mutation_results,
            'survived': survived,
        })

    total = len(results)
    survived_count = sum(1 for r in results if r['survived'])
    killed_count = total - survived_count
    survival_rate = survived_count / total if total > 0 else 0

    return {
        'baseline':      baseline,
        'mutations':     results,
        'total':         total,
        'survived':      survived_count,
        'killed':        killed_count,
        'survival_rate': survival_rate,
        'coverage':      round((1 - survival_rate) * 100, 1),
    }


def run_all():
    cases = make_cases()
    all_results = []

    print()
    print("=" * 70)
    print("   RUNNING ALL EXPERIMENTS")
    print("=" * 70)

    for i, case in enumerate(cases, 1):
        print(f"\n[{i}/9] {case['name']} ({case['complexity']})")
        print(f"       \"{case['description']}\"")

        # Generate spec (real API or fallback)
        spec = generate_spec(case['description'], fallback_key=case['fallback_key'])

        # Score
        report = score_with_custom_impls(spec, case['implementations'])

        result_entry = {
            'name':        case['name'],
            'description': case['description'],
            'complexity':  case['complexity'],
            'total':       report['total'],
            'killed':      report['killed'],
            'survived':    report['survived'],
            'coverage':    report['coverage'],
            'baseline':    report['baseline'],
            'mutations':   [
                {'label': m['label'], 'survived': m['survived']}
                for m in report['mutations']
            ]
        }
        all_results.append(result_entry)

        # Print per-case summary
        print(f"       Mutations: {report['total']}  |  "
              f"Killed: {report['killed']}  |  "
              f"Survived: {report['survived']}  |  "
              f"Coverage: {report['coverage']}%")

        # Show survived mutations
        survived = [m for m in report['mutations'] if m['survived']]
        if survived:
            print(f"       Redundant clauses:")
            for m in survived:
                print(f"         ⚠  {m['label']}")

    # Save to JSON
    os.makedirs(os.path.join(os.path.dirname(__file__), 'results'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), 'results', 'results.json')
    with open(out_path, 'w') as f:
        json.dump({
            'run_at': datetime.now().isoformat(),
            'cases': all_results
        }, f, indent=2)

    # Print summary table
    print()
    print("=" * 70)
    print("   RESULTS SUMMARY TABLE (copy into report)")
    print("=" * 70)
    print(f"{'Function':<25} {'Complexity':<10} {'Mutations':<11} "
          f"{'Killed':<8} {'Survived':<10} {'Coverage'}")
    print("-" * 70)
    for r in all_results:
        print(f"{r['name']:<25} {r['complexity']:<10} {r['total']:<11} "
              f"{r['killed']:<8} {r['survived']:<10} {r['coverage']}%")
    print("=" * 70)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    run_all()