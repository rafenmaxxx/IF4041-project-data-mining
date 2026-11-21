import math
from collections import Counter, defaultdict
from itertools import combinations


def _generate_candidates(prev_level, k):
    prev_set = set(prev_level)
    groups = defaultdict(list)
    for itemset in prev_level:
        groups[itemset[:-1]].append(itemset[-1])

    candidates = set()
    for prefix, lasts in groups.items():
        lasts.sort()
        for i in range(len(lasts)):
            for j in range(i + 1, len(lasts)):
                cand = prefix + (lasts[i], lasts[j])
                if all(cand[:d] + cand[d + 1:] in prev_set for d in range(k - 2)):
                    candidates.add(cand)
    return candidates


def run_apriori(transactions: list[set[str]], min_support: float) -> dict[frozenset[str], int]:
    n = len(transactions)
    min_count = math.ceil(min_support * n)

    item_counts = Counter(item for t in transactions for item in t)
    freq_items = sorted(item for item, c in item_counts.items() if c >= min_count)
    result = {frozenset([item]): item_counts[item] for item in freq_items}

    item_to_id = {item: j for j, item in enumerate(freq_items)}
    weighted_tx = Counter()
    for t in transactions:
        encoded = tuple(sorted(item_to_id[item] for item in t if item in item_to_id))
        if len(encoded) >= 2:
            weighted_tx[encoded] += 1

    current_level = [(j,) for j in range(len(freq_items))]
    k = 2

    while current_level and weighted_tx:
        candidates = _generate_candidates(current_level, k)
        if not candidates:
            break

        counts = Counter()
        n_cand = len(candidates)
        for t, weight in weighted_tx.items():
            if math.comb(len(t), k) <= n_cand:
                for combo in combinations(t, k):
                    if combo in candidates:
                        counts[combo] += weight
            else:
                t_set = set(t)
                for cand in candidates:
                    if all(item in t_set for item in cand):
                        counts[cand] += weight

        current_level = sorted(c for c, cnt in counts.items() if cnt >= min_count)
        for c in current_level:
            result[frozenset(freq_items[j] for j in c)] = counts[c]

        alive_items = {item for c in current_level for item in c}
        next_tx = Counter()
        for t, weight in weighted_tx.items():
            reduced = tuple(item for item in t if item in alive_items)
            if len(reduced) > k:
                next_tx[reduced] += weight
        weighted_tx = next_tx
        k += 1

    return result
