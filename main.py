# main.py
import sys
import ast
from llm_client import generate_spec
from scorer import score_spec

def main(description: str):
    print()
    print("=" * 60)
    print("   SPEC MUTATION SURVIVAL ANALYZER")
    print("=" * 60)
    print(f"  Analyzing: \"{description}\"")
    print("=" * 60)

    print()
    print("Step 1: Generating spec from description...")
    # Pass description as fallback_key hint — scorer picks closest match
    spec = generate_spec(description)
    print("  Done.")

    print()
    print("Step 2: Assertions in this spec:")
    print("-" * 60)
    tree = ast.parse(spec)
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            print(f"  Assert #{count}: {ast.unparse(node.test)}")
            count += 1
    if count == 0:
        print("  No assertions found — check spec output.")
        return

    print()
    print("Step 3: Scoring spec...")
    print("-" * 60)
    report = score_spec(spec)  # ← fixed: no description arg

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
    print(f"  Function analyzed  : {description}")
    print(f"  Total mutations    : {report['total']}")
    print(f"  Load-bearing       : {report['killed']}")
    print(f"  Redundant          : {report['survived']}")
    print(f"  Spec coverage      : {report['coverage']:.1f}%")
    print()
    if report['survived'] == 0:
        print("  ★ Perfect spec — every clause is load-bearing.")
    elif report['coverage'] >= 75:
        print("  ◆ Strong spec — minor redundancy.")
    elif report['coverage'] >= 50:
        print("  ▲ Moderate spec — some clauses need strengthening.")
    else:
        print("  ✗ Weak spec — majority of clauses are redundant.")
    print("=" * 60)

if __name__ == "__main__":
    description = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
                  "a function that sorts a list of integers"
    main(description)