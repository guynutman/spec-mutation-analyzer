# experiments/test_cases.py
# Each test case has:
#   - description: plain English for the LLM
#   - fallback_key: which hardcoded spec to use if API fails
#   - implementations: dict of {name: function} to test against
#   - complexity: Simple / Medium / Complex

def make_cases():
    # ── SIMPLE ────────────────────────────────────────────────────

    def sort_correct(lst): return sorted(lst)
    def sort_wrong_length(lst): return sorted(lst)[:-1] if lst else []
    def sort_unsorted(lst): return lst[:]
    def sort_empty(lst): return []

    def max_correct(lst): return max(lst)
    def max_wrong(lst): return min(lst)
    def max_off_by_one(lst): return sorted(lst)[-2] if len(lst) > 1 else lst[0]
    def max_first(lst): return lst[0]

    def palindrome_correct(s): return s == s[::-1]
    def palindrome_always_true(s): return True
    def palindrome_always_false(s): return False
    def palindrome_wrong(s): return s == s[1:]

    # ── MEDIUM ────────────────────────────────────────────────────

    def median_correct(lst):
        s = sorted(lst)
        n = len(s)
        return s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2

    def median_always_middle(lst):
        s = sorted(lst)
        return s[len(s) // 2]  # ignores even-length averaging

    def median_wrong(lst): return sorted(lst)[0]
    def median_mean(lst): return sum(lst) / len(lst)

    def dedup_correct(lst):
        seen = []
        for x in lst:
            if x not in seen:
                seen.append(x)
        return seen

    def dedup_set(lst): return list(set(lst))  # doesn't preserve order
    def dedup_nothing(lst): return lst[:]
    def dedup_empty(lst): return []

    def bsearch_correct(lst, val):
        lo, hi = 0, len(lst) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if lst[mid] == val: return mid
            elif lst[mid] < val: lo = mid + 1
            else: hi = mid - 1
        return -1

    def bsearch_linear(lst, val):
        try: return lst.index(val)
        except: return -1

    def bsearch_always_zero(lst, val): return 0
    def bsearch_always_missing(lst, val): return -1

    # ── COMPLEX ───────────────────────────────────────────────────

    def flatten_correct(lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(flatten_correct(item))
            else:
                result.append(item)
        return result

    def flatten_one_level(lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result

    def flatten_nothing(lst): return lst[:]
    def flatten_empty(lst): return []

    def group_correct(lst):
        return {'even': [x for x in lst if x % 2 == 0],
                'odd':  [x for x in lst if x % 2 != 0]}

    def group_swapped(lst):
        return {'even': [x for x in lst if x % 2 != 0],
                'odd':  [x for x in lst if x % 2 == 0]}

    def group_empty(lst): return {'even': [], 'odd': []}
    def group_all_even(lst): return {'even': lst[:], 'odd': []}

    def merge_correct(a, b):
        result, i, j = [], 0, 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]: result.append(a[i]); i += 1
            else: result.append(b[j]); j += 1
        return result + a[i:] + b[j:]

    def merge_concat(a, b): return a + b  # not sorted
    def merge_sorted_concat(a, b): return sorted(a + b)  # correct result, wrong method
    def merge_empty(a, b): return []

    return [
        {
            "name": "Sort integers",
            "description": "a function that sorts a list of integers in ascending order",
            "fallback_key": "sort",
            "complexity": "Simple",
            "implementations": {
                "correct":       sort_correct,
                "wrong_length":  sort_wrong_length,
                "unsorted":      sort_unsorted,
                "always_empty":  sort_empty,
            }
        },
        {
            "name": "Find maximum",
            "description": "a function that returns the maximum value in a non-empty list of integers",
            "fallback_key": "max",
            "complexity": "Simple",
            "implementations": {
                "correct":       max_correct,
                "returns_min":   max_wrong,
                "off_by_one":    max_off_by_one,
                "returns_first": max_first,
            }
        },
        {
            "name": "Palindrome check",
            "description": "a function that returns True if a string is a palindrome, False otherwise",
            "fallback_key": "palindrome",
            "complexity": "Simple",
            "implementations": {
                "correct":       palindrome_correct,
                "always_true":   palindrome_always_true,
                "always_false":  palindrome_always_false,
                "wrong_slice":   palindrome_wrong,
            }
        },
        {
            "name": "Median of list",
            "description": "a function that returns the median of a list of numbers (average of two middle elements for even-length lists)",
            "fallback_key": "median",
            "complexity": "Medium",
            "implementations": {
                "correct":        median_correct,
                "ignores_even":   median_always_middle,
                "returns_min":    median_wrong,
                "returns_mean":   median_mean,
            }
        },
        {
            "name": "Remove duplicates",
            "description": "a function that removes duplicates from a list while preserving the original order of first occurrences",
            "fallback_key": "dedup",
            "complexity": "Medium",
            "implementations": {
                "correct":           dedup_correct,
                "ignores_order":     dedup_set,
                "no_dedup":          dedup_nothing,
                "always_empty":      dedup_empty,
            }
        },
        {
            "name": "Binary search",
            "description": "a function binary_search(lst, val) that returns the index of val in a sorted list, or -1 if not found",
            "fallback_key": "binary_search",
            "complexity": "Medium",
            "implementations": {
                "correct":        bsearch_correct,
                "linear_search":  bsearch_linear,
                "always_zero":    bsearch_always_zero,
                "always_missing": bsearch_always_missing,
            }
        },
        {
            "name": "Flatten nested list",
            "description": "a function that recursively flattens a nested list of integers into a single flat list",
            "fallback_key": "flatten",
            "complexity": "Complex",
            "implementations": {
                "correct":      flatten_correct,
                "one_level":    flatten_one_level,
                "no_flatten":   flatten_nothing,
                "always_empty": flatten_empty,
            }
        },
        {
            "name": "Group even/odd",
            "description": "a function that takes a list of integers and returns a dict with keys 'even' and 'odd' containing the respective elements",
            "fallback_key": "group_even_odd",
            "complexity": "Complex",
            "implementations": {
                "correct":    group_correct,
                "swapped":    group_swapped,
                "all_empty":  group_empty,
                "all_even":   group_all_even,
            }
        },
        {
            "name": "Merge sorted lists",
            "description": "a function that merges two sorted lists into a single sorted list",
            "fallback_key": "merge_sorted",
            "complexity": "Complex",
            "implementations": {
                "correct":        merge_correct,
                "unsorted_concat": merge_concat,
                "sorted_concat":  merge_sorted_concat,
                "always_empty":   merge_empty,
            }
        },
    ]