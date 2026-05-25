# Spec Mutation Survival Analyzer

> **Which parts of your formal specification are actually doing anything?**

Built for the [Apart Research Secure Program Synthesis Hackathon](https://apartresearch.com/sprints/secure-program-synthesis-hackathon-2026-05-22-to-2026-05-24), May 2026.

---

## The Core Argument

Formal verification promises mathematical certainty that code is correct. But that promise is only as strong as the specification being verified against. A specification with redundant or missing clauses can pass all verification checks while still permitting dangerous behavior — **the code is verified, but verified against the wrong thing.**

This failure mode is invisible to standard testing and to casual expert review, because the spec *looks* complete. This tool makes it visible.

---

## What Is Spec Coverage?

Code coverage tells you which lines of code your tests execute.
**Spec coverage tells you which clauses of your spec are actually enforced.**

We borrow *mutation testing* — a well-established technique from software testing — and apply it to the specification layer itself:

1. Take a formal specification (property-based tests describing what a function must do)
2. Generate hundreds of mutated versions — flip `<=` to `<`, remove an assert, flip `==` to `!=`
3. Run each mutation against a suite of implementations
4. If a mutation goes **undetected** → that clause is **redundant** (dead weight)
5. If a mutation is **caught** → that clause is **load-bearing** (doing real work)

The ratio gives you a **spec coverage score**: a single number expressing how much of your spec is actually enforced.

---

## Why This Matters for AI Safety

As AI generates code at scale, the bottleneck shifts from *writing* code to *specifying* what the code should do. A weak spec means a formally verified program may still behave incorrectly — verified against the wrong thing. Spec coverage makes specification weakness measurable and actionable, without requiring any formal methods expertise from the user.

---

## Example Output

```
============================================================
   SPEC MUTATION SURVIVAL ANALYZER
============================================================
  Analyzing: "a function that sorts a list of integers"

WHAT THE SPEC IS TESTING:
  Assert #0: len(result) == len(lst)
  Assert #1: sorted(result) == sorted(lst)
  Assert #2: result[i] <= result[i + 1]

BASELINE (original spec vs implementations):
  ✓ correct
  ✗ wrong_length
  ✗ not_sorted
  ✗ always_empty

MUTATION RESULTS:
  ✓  KILLED    →  <= → < (occurrence 0)
     Load-bearing — the spec depends on this.
  ✓  KILLED    →  == → != (occurrence 0)
     Load-bearing — the spec depends on this.
  ✓  KILLED    →  == → != (occurrence 1)
     Load-bearing — the spec depends on this.
  ⚠  SURVIVED  →  removed assert #0  (len(result) == len(lst))
     Redundant — removing this changed nothing.
  ⚠  SURVIVED  →  removed assert #1  (sorted(result) == sorted(lst))
     Redundant — removing this changed nothing.
  ✓  KILLED    →  removed assert #2  (result[i] <= result[i + 1])
     Load-bearing — the spec depends on this.

FINAL SUMMARY:
  Total mutations tested : 6
  Load-bearing clauses   : 4
  Redundant clauses      : 2
  Spec coverage score    : 66.7%
  ▲ Moderate spec — some clauses need strengthening.
============================================================
```

**What this finding means:** The spec author wrote three assertions believing they were independent. The tool reveals that Assert #0 and Assert #1 are each implied by the other two — removing either one changes nothing. The spec is weaker than it looks, and this would be invisible to manual review.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/guynutman/spec-mutation-analyzer
cd spec-mutation-analyzer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 5. Run on any function description
python main.py "a function that sorts a list of integers"
python main.py "a function that finds the median of a list"
python main.py "a function that removes duplicates from a list"
```

---

## How It Works

```
Plain-English Description
         ↓
  Gemini API generates
  Hypothesis property tests
  (the spec)
         ↓
  AST Mutation Engine
  ├─ Operator flips: <= → <, == → !=, > → >=, etc.
  └─ Assert removal: remove one clause at a time
         ↓
  Run each mutation against
  4 implementations:
  ├─ correct
  ├─ wrong_length (drops last element)
  ├─ not_sorted (returns unsorted)
  └─ always_empty (always returns [])
         ↓
  Spec Coverage Score + Per-Clause Report
```

---

## File Structure

```
├── main.py          ← Entry point — run this
├── llm_client.py    ← Calls Gemini API to generate specs from English
├── mutator.py       ← Generates mutated spec variants (AST-based)
├── runner.py        ← Runs specs against implementations via Hypothesis
├── scorer.py        ← Computes survival rates and coverage score
├── requirements.txt
└── README.md
```

---

## Limitations

- Specs are Python/Hypothesis property tests, not Lean/Coq formal proofs
- Hypothesis is non-deterministic — survival results can vary between runs (mitigated with `max_examples=500`)
- Implementations are currently hardcoded; real-world use would require user-supplied implementations
- Mutation operators cover comparisons and assertion removal; logical connectives (`and`/`or`, `∀`/`∃`) are future work

---

## Future Work

The most important extension is **Lean 4 integration**. A Lean theorem admits direct mutation analysis — flipping `∧` to `∨`, removing a hypothesis, weakening `=` to `≤` — using identical survival testing logic. This would bring spec coverage to the layer where formal verification provides its strongest guarantees.

Additional directions: auto-generating implementations via LLM (closing the CEGIS loop), logical connective mutations, and a non-expert UI.

---

## Authors

Guy Nutman — UCLA, Henry Samueli School of Engineering
Nir Nutman — UCSB, Robert Mehrabian College of Engineering

Built during the Apart Research Secure Program Synthesis Hackathon, May 2026.

---

## License

MIT