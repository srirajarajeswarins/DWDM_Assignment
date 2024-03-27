import streamlit as st
import pandas as pd

class TreeNode:
    def __init__(self, item, frequency, parent):
        self.item = item
        self.frequency = frequency
        self.parent = parent
        self.children = {}
        self.next_node = None  # Link to the next node with the same item


def build_tree(transactions, min_support):
    item_counts = {}
    for transaction in transactions:
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1

    frequent_items = {item: count for item, count in item_counts.items() if count >= min_support}

    if len(frequent_items) == 0:
        return None, None

    ordered_items = sorted(frequent_items.items(), key=lambda x: (-x[1], x[0]))

    root = TreeNode(item=None, frequency=None, parent=None)
    header_table = {}

    for item, _ in ordered_items:
        header_table[item] = None

    for transaction in transactions:
        filtered_transaction = [item for item in transaction if item in frequent_items]
        if len(filtered_transaction) > 0:
            insert_tree(filtered_transaction, root, header_table)

    return root, header_table


def insert_tree(transaction, node, header_table):
    if transaction[0] in node.children:
        node.children[transaction[0]].frequency += 1
    else:
        node.children[transaction[0]] = TreeNode(item=transaction[0], frequency=1, parent=node)
        if header_table[transaction[0]] is None:
            header_table[transaction[0]] = node.children[transaction[0]]
        else:
            update_header(header_table[transaction[0]], node.children[transaction[0]])

    if len(transaction) > 1:
        insert_tree(transaction[1:], node.children[transaction[0]], header_table)


def update_header(node_to_test, target_node):
    while node_to_test.next_node is not None:
        node_to_test = node_to_test.next_node
    node_to_test.next_node = target_node


def ascend_tree(node, prefix_path):
    if node.parent is not None:
        prefix_path.append(node.item)
        ascend_tree(node.parent, prefix_path)


def find_prefix_path(base_item, header_table):
    node = header_table[base_item]
    conditional_patterns = {}
    while node is not None:
        prefix_path = []
        ascend_tree(node, prefix_path)
        if len(prefix_path) > 1:
            conditional_patterns[frozenset(prefix_path[1:])] = node.frequency
        node = node.next_node
    return conditional_patterns


def mine_tree(node, header_table, min_support, prefix, frequent_itemsets):
    for base_item in sorted(header_table.keys()):
        new_frequent_set = prefix.copy()
        new_frequent_set.add(base_item)
        frequent_itemsets.append(new_frequent_set)
        conditional_patterns = find_prefix_path(base_item, header_table)
        conditional_tree, conditional_header = build_tree(conditional_patterns.keys(), min_support)
        if conditional_header is not None:
            mine_tree(conditional_tree, conditional_header, min_support, new_frequent_set, frequent_itemsets)


def fpgrowth(transactions, min_support, header_table):
    root, header_table = build_tree(transactions, min_support)
    frequent_itemsets = []
    mine_tree(root, header_table, min_support, set(), frequent_itemsets)
    return frequent_itemsets, header_table


def main(header_table):
    st.title("FP-Growth Algorithm with Streamlit")

    st.write("Enter the transactions one by one below. Press Enter on an empty input to finish.")

    transactions = []
    input_counter = 0
    while True:
        transaction = st.text_input(f"Enter transaction {input_counter + 1} (comma-separated items):",
                                    key=f"transaction_input_{input_counter}")
        if transaction.strip() == "":
            break
        items = transaction.split(',')
        transactions.append([item.strip() for item in items])
        input_counter += 1

    min_support = st.number_input("Enter minimum support:", value=1.0)

    if st.button("Run FP-Growth"):
        frequent_itemsets, header_table = fpgrowth(transactions, min_support, header_table)

        st.write("Frequent itemsets:")

        frequent_pattern_growth = {item: [] for item in header_table.keys()}
        for itemset in frequent_itemsets:
            for item in itemset:
                frequent_pattern_growth[item].append(itemset)

        # Replace <NA> with empty list
        frequent_pattern_growth_cleaned = {k: v if v is not pd.NA else [] for k, v in frequent_pattern_growth.items()}

        # Convert dictionary to DataFrame for better display
        frequent_pattern_growth_df = pd.DataFrame.from_dict(frequent_pattern_growth_cleaned, orient='index')

        # Display frequent pattern growth table
        st.write("Frequent Pattern Growth:")
        st.table(frequent_pattern_growth_df)


if __name__ == "__main__":
    header_table = None  # Initialize header_table variable
    main(header_table)
