from itertools import combinations

import pandas as pd


RULE_COLUMNS = ["antecedents", "consequents", "support", "confidence", "lift"]


def generate_rules(frequent_itemsets: dict[frozenset[str], int], total_transactions: int, min_confidence: float = 0.5) -> pd.DataFrame:
    if total_transactions <= 0:
        raise ValueError("total_transactions harus lebih besar dari 0")
    if not 0 <= min_confidence <= 1:
        raise ValueError("min_confidence harus antara 0 dan 1")

    rules = []
    for itemset, itemset_count in frequent_itemsets.items():
        if len(itemset) < 2:
            continue

        items = sorted(itemset)
        support = itemset_count / total_transactions

        for size in range(1, len(items)):
            for antecedent_items in combinations(items, size):
                antecedent = frozenset(antecedent_items)
                consequent = frozenset(itemset - antecedent)

                antecedent_count = frequent_itemsets.get(antecedent)
                consequent_count = frequent_itemsets.get(consequent)
                if antecedent_count is None or consequent_count is None:
                    raise ValueError(
                        "Frequent itemset tidak lengkap: subset antecedent "
                        "atau consequent tidak ditemukan."
                    )
                if antecedent_count <= 0 or consequent_count <= 0:
                    raise ValueError("Support count harus lebih besar dari 0")

                confidence = itemset_count / antecedent_count
                if confidence >= min_confidence:
                    lift = confidence / (consequent_count / total_transactions)
                    rules.append({
                        "antecedents": antecedent,
                        "consequents": consequent,
                        "support": support,
                        "confidence": confidence,
                        "lift": lift
                    })

    rules.sort(
        key=lambda rule: (
            -rule["lift"],
            -rule["confidence"],
            -rule["support"],
            tuple(sorted(rule["antecedents"])),
            tuple(sorted(rule["consequents"]))
        )
    )
    return pd.DataFrame(rules, columns=RULE_COLUMNS)
