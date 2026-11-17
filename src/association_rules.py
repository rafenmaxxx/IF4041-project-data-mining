from itertools import combinations
from fpgrowth import fp_growth, transactions

def generate_association_rules(frequent_patterns, min_confidence=0.5):
    rules = []
    for itemset, itemset_data in frequent_patterns.items():
        if len(itemset) < 2:
            continue

        support_union = itemset_data["support"]
        for i in range(1, len(itemset)):
            for antecedent in combinations(itemset, i):
                consequent = tuple(
                    item for item in itemset
                    if item not in antecedent
                )
                antecedent_data = frequent_patterns.get(tuple(sorted(antecedent)))

                consequent_data = frequent_patterns.get(tuple(sorted(consequent)))

                if antecedent_data is None or consequent_data is None:
                    raise ValueError(
                        "Frequent itemset tidak lengkap."
                        "Periksa hasil FP-Growth."
                    )

                support_antecedent = antecedent_data["support"]
                support_consequent = consequent_data["support"]

                confidence = (support_union / support_antecedent)
                lift = (confidence / support_consequent)

                if confidence >= min_confidence:
                    rules.append({
                        "antecedent" : tuple(sorted(antecedent)),
                        "consequent" : tuple(sorted(consequent)),
                        "support" : support_union,
                        "confidence" : confidence,
                        "lift" : lift
                    })

        rules.sort(
            key=lambda rule: (
                -rule["lift"],
                -rule["confidence"],
                -rule["support"]
            )
        )
        
    return rules


def tampilkan_rules(rules, top_n=10):

    print(f"{'No':<5}"
          f"{'Association Rule':<35}"
          f"{'Support':<12}"
          f"{'Confidence':<15}"
          f"{'Lift':<10}")

    print("-" * 77)

    for i, rule in enumerate(rules[:top_n], start=1):

        antecedent = ", ".join(rule["antecedent"])
        consequent = ", ".join(rule["consequent"])

        rule_name = f"{antecedent} -> {consequent}"

        print(
            f"{i:<5}"
            f"{rule_name:<35}"
            f"{rule['support']:<12.2%}"
            f"{rule['confidence']:<15.2%}"
            f"{rule['lift']:<10.3f}"
        )

# contoh

# # Jalankan FP-Growth
# frequent_patterns = fp_growth(
#     transactions,
#     min_support=0.5
# )

# # Generate association rules
# rules = generate_association_rules(
#     frequent_patterns,
#     min_confidence=0.5
# )

# tampilkan_rules(rules)
