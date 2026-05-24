# main.py
# Entry point for the Spec Mutation Survival Analyzer.
# Run this file to analyze any function description.
#
# Usage:
#   python main.py
#   python main.py "a function that finds the median of a list"

import sys
from llm_client import generate_spec
from mutator import generate_mutations
from scorer import score_spec

def main(description: str):
    print()
    print("=" * 60)
    print("   SPEC MUTATION SURVIVAL ANALYZER")
    print("=" * 60)
    print(f"  Analyzing: \"{description}\"")
    print("=" * 60)

    # Step 1: Generate the spec
    print()
    print("Step 1: Generating spec from description...")
    spec = generate_spec(description)
    print("  Done. Spec generated successfully.")

    # Step 2: Show what the spec is checking
    print()
    print("Step 2: Spec contains these assertions:")
    print("-" * 60)
    import ast
    tree = ast.parse(spec)
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            print(f"  Assert #{count}: {ast.unparse(node.test)}")
            count += 1
    if count == 0:
        print("  No assertions found — check the spec output.")
        return

    # Step 3: Run baseline
    print()
    print("Step 3: Running baseline (original spec vs implementations)...")
    print("-" * 60)

    # Step 4: Score the spec
    report = score_spec(spec)

    # Step 5: Print full report
    print()
    print("=" * 60)
    print("   MUTATION RESULTS")
    print("=" * 60)
    for m in report['mutations']:
        if m['survived']:
            print(f"  ⚠  SURVIVED  →  {m['label']}")
            print(f"     Redundant — removing this changed nothing.")
        else:
            print(f"  ✓  KILLED    →  {m['label']}")
            print(f"     Load-bearing — the spec depends on this.")

    print()
    print("=" * 60)
    print("   FINAL SUMMARY")
    print("=" * 60)
    coverage = (1 - report['survival_rate']) * 100
    print(f"  Function analyzed  : {description}")
    print(f"  Total mutations    : {report['total']}")
    print(f"  Load-bearing       : {report['killed']}  (good — spec catches changes)")
    print(f"  Redundant          : {report['survived']}  (weak — spec doesn't notice)")
    print(f"  Spec coverage      : {coverage:.1f}%")
    print()
    if report['survived'] == 0:
        print("  ★ Perfect spec — every clause is load-bearing.")
    elif coverage >= 75:
        print("  ◆ Strong spec — minor redundancy.")
    elif coverage >= 50:
        print("  ▲ Moderate spec — some clauses need strengthening.")
    else:
        print("  ✗ Weak spec — majority of clauses are redundant.")
    print("=" * 60)
    print()

if __name__ == "__main__":
    # Use command line argument if provided, otherwise use default
    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
    else:
        description = "a function that sorts a list of integers"
    
    main(description)