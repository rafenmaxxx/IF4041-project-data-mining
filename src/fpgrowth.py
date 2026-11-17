from collections import Counter
import math

class FPNode:
    def __init__ (self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.node_link = None

    def increment(self, count):
        self.count += count

def hitung_fp(transactions):
    item_counts = Counter()

    for transaction in transactions:
        item_counts.update(transaction)

    return item_counts

def calculate_support(transactions, min_support=0.5):

    item_counts = hitung_fp(transactions)

    total_transaction = len(transactions)

    min_count = math.ceil(
        min_support * total_transaction
    )

    frequent_items = {}
    for item, count in item_counts.items():
        support = count / total_transaction
        if count >= min_count:
            frequent_items[item] = {
                "count" : count,
                "support" : support
            }

    return frequent_items

def build_fp_tree(transactions, min_support=0.5):

    frequent_items = calculate_support(transactions, min_support)

    frequent_counts = {
        item: data["count"]
        for item, data in frequent_items.items()
    }

    ordered_items = sorted(frequent_counts, key=lambda item: (-frequent_counts[item], item))

    rank = {
        item: index 
        for index, item in enumerate(ordered_items)
    }

    header_table = {
        item: {
            "count": count,
            "head" : None,
            "tail" : None
        }
        for item, count in frequent_counts.items()
    }

    root = FPNode(None, 0, None)

    # membuat tree
    for transaction in transactions:
        filtered_items = [
            item for item in set(transaction)
            if item in frequent_counts
        ]

        # urutkan berdasarkan rank
        sorted_transaction = sorted(
            filtered_items,
            key=lambda item: rank[item]
        )

        current_node = root

        for item in sorted_transaction:
            # kalau node sudah ada
            if item in current_node.children:
                current_node.children[item].increment(1)
            else:
                new_node = FPNode(item, 1, current_node)
                current_node.children[item] = new_node

                # hubungan dengan node link
                if header_table[item]["head"] is None:
                    header_table[item]["head"] = new_node
                else:
                    header_table[item]["tail"].node_link = new_node

                header_table[item]["tail"] = new_node

            current_node = current_node.children[item]
    return root, header_table

def print_tree(node, level=0):
    for child in node.children.values():
        print("  " * level + f"{child.item}: {child.count}")
        print_tree(child, level + 1)

def print_header_table(header_table):
    for item, data in header_table.items():
        print(f"\nItem: {item}")
        print(f"Total count: {data['count']}")

        current = data["head"]

        print("Node links:", end=" ")

        while current is not None:
            print(current.count, end=" -> ")
            current = current.node_link

        print("None")

def find_prefix_path(base_item, header_table):
    conditional_patterns = []
    current_node = header_table[base_item]["head"]

    # telusuri seluruh node dnegan item sama
    while current_node is not None:
        prefix_path = []

        parent = current_node.parent
        while parent is not None and parent.item is not None:
            prefix_path.append(parent.item)
            parent = parent.parent

        if prefix_path:
            conditional_patterns.append(
                (prefix_path, current_node.count)
            )

        current_node = current_node.node_link

    return conditional_patterns

def build_conditional_tree(pattern_base, min_count):
    item_counts = Counter()

    for path, weight in pattern_base:
        for item in set(path):
            item_counts[item] += weight

    frequent_counts = {
        item: count
        for item, count in item_counts.items()
        if count >= min_count
    }

    if not frequent_counts:
        return None, None

    ordered_items = sorted(
        frequent_counts,
        key=lambda item: (-frequent_counts[item], item)
    )

    rank = {
        item: index
        for index, item in enumerate(ordered_items)
    }

    header_table = {
        item: {
            "count": count,
            "head": None,
            "tail": None
        }
        for item, count in frequent_counts.items()
    }

    root = FPNode(None, 0, None)

    for path, weight in pattern_base:
        filtered_items = [
            item for item in set(path)
            if item in frequent_counts
        ]

        sorted_items = sorted(
            filtered_items,
            key=lambda item: rank[item]
        )

        current_node = root

        for item in sorted_items:
            if item in current_node.children:
                current_node.children[item].increment(weight)
            else:
                new_node = FPNode(
                    item,
                    weight,
                    current_node
                )

                current_node.children[item] = new_node

                if header_table[item]["head"] is None:
                    header_table[item]["head"] = new_node
                else:
                    header_table[item]["tail"].node_link = new_node
                header_table[item]["tail"] = new_node
            current_node = current_node.children[item]

    return root, header_table


def mine_patterns(header_table, min_count, suffix=(), patterns=None):
    if patterns is None:
        patterns = {}

    items = sorted(
        header_table.keys(),
        key=lambda item: (
            header_table[item]["count"],
            item
        )
    )

    for item in items:
        new_suffix = suffix + (item,)

        patterns[frozenset(new_suffix)] = (
            header_table[item]["count"]
        )

        conditional_base = find_prefix_path(
            item,
            header_table
        )

        conditional_root, conditional_header = (
            build_conditional_tree(
                conditional_base,
                min_count
            )
        )

        if conditional_header is not None:

            mine_patterns(
                conditional_header,
                min_count,
                new_suffix,
                patterns
            )

    return patterns

def run_fpgrowth(transactions: list[set[str]], min_support: float) -> dict[frozenset[str], int]:
    if not 0 < min_support <= 1:
        raise ValueError("min_support harus antara 0 dan 1")

    if not transactions:
        return {}

    # Hitung minimum count
    total_transactions = len(transactions)

    min_count = math.ceil(
        min_support * total_transactions
    )

    # Bangun FP-Tree utama
    root, header_table = build_fp_tree(
        transactions,
        min_support
    )

    # Cari seluruh frequent patterns
    patterns = mine_patterns(
        header_table,
        min_count
    )

    return patterns
