# mutator.py
# Takes a spec (Python code string) and generates mutated versions of it.
# Each mutation makes exactly ONE small change — flipping an operator or
# removing one assert. If a mutation doesn't change the spec's behavior,
# that clause is redundant (dead weight).

import ast
import copy

# Each entry: (original operator, replacement operator, human-readable label)
# These are AST node types — Python's internal representation of code
MUTATIONS = [
    (ast.Lt,    ast.LtE,   "< → <="),    # strictly less than → less or equal
    (ast.LtE,   ast.Lt,    "<= → <"),    # less or equal → strictly less than
    (ast.Gt,    ast.GtE,   "> → >="),    # strictly greater → greater or equal
    (ast.GtE,   ast.Gt,    ">= → >"),    # greater or equal → strictly greater
    (ast.Eq,    ast.NotEq, "== → !="),   # equal → not equal
    (ast.NotEq, ast.Eq,    "!= → =="),   # not equal → equal
]

class OperatorMutator(ast.NodeTransformer):
    """
    Walks the AST and replaces one specific occurrence of an operator.
    Example: if there are 3 `==` signs and occurrence=1,
    it replaces only the second one.
    """
    def __init__(self, target_type, replacement_type, occurrence):
        self.target_type = target_type
        self.replacement_type = replacement_type
        self.occurrence = occurrence  # which instance to mutate (0-indexed)
        self.count = 0

    def visit(self, node):
        if isinstance(node, self.target_type):
            if self.count == self.occurrence:
                self.count += 1
                return self.replacement_type()
            self.count += 1
        return self.generic_visit(node)

class AssertRemover(ast.NodeTransformer):
    """
    Removes one specific assert statement from the spec.
    Example: if there are 3 asserts and target_index=1,
    it removes only the second one.
    """
    def __init__(self, target_index):
        self.target_index = target_index
        self.count = 0

    def visit_Assert(self, node):
        if self.count == self.target_index:
            self.count += 1
            return None  # returning None removes this node from the AST
        self.count += 1
        return node

def count_nodes(tree, node_type):
    """Count how many times a given node type appears in the AST."""
    return sum(1 for n in ast.walk(tree) if isinstance(n, node_type))

def generate_mutations(spec_code: str) -> list[dict]:
    """
    Returns a list of mutations, each as a dict:
      {
        'label': human-readable description of what changed,
        'code':  the mutated spec as a Python code string
      }
    """
    mutations = []
    tree = ast.parse(spec_code)

    # --- Operator mutations ---
    # For each operator type, find every occurrence and mutate each one separately
    for (old_type, new_type, label) in MUTATIONS:
        count = count_nodes(tree, old_type)
        for i in range(count):
            mutated_tree = copy.deepcopy(tree)
            mutator = OperatorMutator(old_type, new_type, occurrence=i)
            mutated_tree = mutator.visit(mutated_tree)
            ast.fix_missing_locations(mutated_tree)
            try:
                code = ast.unparse(mutated_tree)
                mutations.append({
                    'label': f"{label} (occurrence {i})",
                    'code': code
                })
            except Exception:
                pass

    # --- Assert removal mutations ---
    # Remove each assert one at a time
    assert_count = count_nodes(tree, ast.Assert)
    for i in range(assert_count):
        mutated_tree = copy.deepcopy(tree)
        remover = AssertRemover(target_index=i)
        mutated_tree = remover.visit(mutated_tree)
        ast.fix_missing_locations(mutated_tree)
        try:
            code = ast.unparse(mutated_tree)
            mutations.append({
                'label': f"removed assert #{i}  ({get_assert_text(tree, i)})",
                'code': code
            })
        except Exception:
            pass

    return mutations

def get_assert_text(tree, index):
    """Helper: returns the human-readable text of the Nth assert."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            if count == index:
                return ast.unparse(node.test)
            count += 1
    return "unknown"


if __name__ == "__main__":
    from llm_client import generate_spec

    spec = generate_spec("a function that sorts a list of integers")
    mutations = generate_mutations(spec)

    print(f"Generated {len(mutations)} mutations from the base spec.\n")
    print("Sample (first 3 mutations):")
    print("-" * 50)
    for m in mutations[:3]:
        print(f"Mutation: {m['label']}")
        print(m['code'])
        print()