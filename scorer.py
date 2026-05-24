# scorer.py
from runner import make_target, IMPLEMENTATIONS
from mutator import generate_mutations

def score_spec(spec_code: str) -> dict:
    """
    For each mutation:
      - Run it against all implementations
      - A mutation 'survives' if it passes the same implementations
        as the original spec (meaning it didn't change anything)
    Returns a full report.
    """

    # First get baseline: which impls does the ORIGINAL spec pass?
    baseline = {}
    for name, impl in IMPLEMENTATIONS.items():
        runner = make_target(impl)
        result = runner(spec_code)
        baseline[name] = result['passed']

    print("Baseline results:")
    for name, passed in baseline.items():
        print(f"  {name:20s} → {'PASS' if passed else 'FAIL'}")
    print()

    # Generate all mutations
    mutations = generate_mutations(spec_code)
    print(f"Testing {len(mutations)} mutations...\n")

    results = []
    for mutation in mutations:
        mutation_results = {}
        for name, impl in IMPLEMENTATIONS.items():
            runner = make_target(impl)
            result = runner(mutation['code'])
            mutation_results[name] = result['passed']

        # A mutation SURVIVES if its results match the baseline exactly
        # i.e. the mutation didn't change what the spec accepts/rejects
        survived = (mutation_results == baseline)

        results.append({
            'label':    mutation['label'],
            'results':  mutation_results,
            'survived': survived,
        })

    return {
        'baseline':       baseline,
        'mutations':      results,
        'total':          len(results),
        'survived':       sum(1 for r in results if r['survived']),
        'killed':         sum(1 for r in results if not r['survived']),
        'survival_rate':  sum(1 for r in results if r['survived']) / len(results) if results else 0,
    }

if __name__ == "__main__":
    from llm_client import generate_spec

    spec = generate_spec("a function that sorts a list of integers")
    report = score_spec(spec)

    print()
    print("=" * 60)
    print("         SPEC MUTATION SURVIVAL ANALYSIS")
    print("=" * 60)

    print()
    print("WHAT THE SPEC IS TESTING:")
    print("-" * 60)
    # Extract and number the asserts from the spec for reference
    import ast
    tree = ast.parse(spec)
    assert_num = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            print(f"  Assert #{assert_num}: {ast.unparse(node.test)}")
            assert_num += 1

    print()
    print("BASELINE (original spec vs implementations):")
    print("-" * 60)
    for name, passed in report['baseline'].items():
        icon = "✓" if passed else "✗"
        print(f"  {icon} {name}")

    print()
    print("MUTATION RESULTS:")
    print("-" * 60)
    for m in report['mutations']:
        if m['survived']:
            print(f"  ⚠  SURVIVED  →  {m['label']}")
            print(f"     This clause is redundant — removing it changed nothing.")
        else:
            print(f"  ✓  KILLED    →  {m['label']}")
            print(f"     This clause is load-bearing — the spec depends on it.")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    coverage = (1 - report['survival_rate']) * 100
    print(f"  Total mutations tested : {report['total']}")
    print(f"  Load-bearing clauses   : {report['killed']}  (killed mutations)")
    print(f"  Redundant clauses      : {report['survived']}  (survived mutations)")
    print(f"  Spec coverage score    : {coverage:.1f}%")
    print()
    if report['survived'] == 0:
        print("  ★ Perfect spec — every clause is doing real work.")
    elif coverage >= 75:
        print("  ◆ Strong spec — mostly load-bearing with minor redundancy.")
    elif coverage >= 50:
        print("  ▲ Moderate spec — some clauses need strengthening.")
    else:
        print("  ✗ Weak spec — majority of clauses are redundant.")
    print("=" * 60)