from typing import cast
from familytree.infer_promo import EarlierGradYear, GraduationYearAlignator
from familytree.tree_utils import (
    SENTINEL_ID,
    BaseSettingData,
    ColorizedNodeData,
    IndependantSubTree,
    SentinelNode,
    init_tree,
)

type TestIndSubtree = IndependantSubTree[BaseSettingData, None, EarlierGradYear]


def init_test_tree():
    return init_tree(ColorizedNodeData[BaseSettingData, None])



def test_promo_inference():
    # initial_subtree
    empty_root_subtree = init_test_tree()
    sentinel_node = cast(SentinelNode, empty_root_subtree.get_node(SENTINEL_ID))

    # Subtrees
    treeA = init_test_tree()
    treeE = init_test_tree()
    treeF = init_test_tree()

    # Subtree without specified graduation year
    a = treeA.create_node("A", "A", SENTINEL_ID)
    b = treeA.create_node("B", "B", a)
    c = treeA.create_node("C", "C", a)
    d = treeA.create_node("D", "D", b)

    # Subtrees with one member for the test (we only need one node)
    treeE.create_node("E", "E", SENTINEL_ID)
    treeF.create_node("F", "F", SENTINEL_ID)

    # Create the dfs_ordered_subtrees list
    dfs_ordered_subtrees = [
        IndependantSubTree(sentinel_node, None, treeA),  # unspecified
        IndependantSubTree(c, 2026, treeE),
        IndependantSubTree(d, 2028, treeF),
    ]
    unspecified_subtree_idx = 0
    a = GraduationYearAlignator(2023)
    assert a.infer_earlier_grad_year_for_unspecified(
        dfs_ordered_subtrees, unspecified_subtree_idx
    ) == 2024
