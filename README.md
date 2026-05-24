# Spec Mutation Survival Analyzer

A research tool that measures how strong a formal specification is
by automatically mutating it and checking whether the mutations go undetected.

Built for the [Apart Research Secure Program Synthesis Hackathon](https://apartresearch.com/sprints/secure-program-synthesis-hackathon-2026-05-22-to-2026-05-24) (May 2026).

---

## The Core Idea

When AI generates code, someone has to write a *specification* — formal rules
describing what the code must do. But specs themselves can be wrong:
too weak, redundant, or missing edge cases.

This tool answers: **which parts of your spec are actually doing anything?**

It works by:
1. Taking a plain-English function description
2. Generating a Hypothesis property-based spec (via Gemini API)
3. Mutating the spec hundreds of ways (flipping operators, removing clauses)
4. Checking which mutations go undetected
5. Reporting a **spec coverage score** — like code coverage, but for specs

A clause that survives mutation is redundant. A clause that kills mutations
is load-bearing. The ratio is your spec's coverage score.

---

## Analogy

> Code coverage tells you which lines of code your tests hit.
> Spec coverage tells you which clauses of your spec are actually enforced.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/spec-mutation-analyzer
cd spec-mutation-analyzer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 5. Run
python main.py "a function that sorts a list of integers"
```

---

## Example Output

```
============================================================
   SPEC MUTATION SURVIVAL ANALYZER
============================================================
  Analyzing: "a function that sorts a list of integers"

MUTATION RESULTS:
  ✓  KILLED    →  <= → < (occurrence 0)
     Load-bearing — the spec depends on this.
  ⚠  SURVIVED  →  removed assert #0  (len(result) == len(lst))
     Redundant — removing this changed nothing.
  ...

FINAL SUMMARY:
  Spec coverage : 66.7%
  ▲ Moderate spec — some clauses need strengthening.
```

---

## File Structure

```
├── main.py          # Entry point — run this
├── llm_client.py    # Calls Gemini API to generate specs
├── mutator.py       # Generates mutated versions of specs
├── runner.py        # Runs specs against implementations
├── scorer.py        # Computes survival rates and coverage score
├── requirements.txt
└── README.md
```

---

## Research Context

This project addresses a core problem in secure program synthesis:
specs are usually assumed to be correct, but they can be just as buggy
as the code they're meant to verify. Mutation survival analysis brings
the well-established technique of mutation testing to the spec layer itself.

**Spec coverage** is an underexplored metric. This tool is a prototype
demonstrating it's feasible to compute automatically.