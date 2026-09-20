"""Functions to infer initial graduation year of the members."""

from typing import cast, override
from functools import reduce

from pydantic import BaseModel
from .tree_utils import (
    BaseSettingData,
    ColorizedNodeData,
    IndependantSubTree,
    SentinelNode,
    TypedNode,
    TypedTree,
    depth_first_search,
    init_tree,
    is_real_node,
    is_subtree_ancestor,
)
from .config_exceptions import BadTreeConfigException
from .base_tree_transformer import BaseTreeTransformer, ColorationFunction


type OptEarlierGradYear = int | None
type EarlierGradYear = int

fake_node_id = 0


def create_new_fake_node_id() -> str:
    global fake_node_id
    to_be_returned = f"deadbeef{fake_node_id}"
    fake_node_id += 1
    return to_be_returned


class SettingDataWithGraduationYear(BaseSettingData):
    initial_grad_year: int | None = None


class ColorationDataWithGradYear(BaseModel):
    initial_grad_year: int


class GraduationYearAlignator[
    SettingData: SettingDataWithGraduationYear,
    InitialColorationData: BaseModel,
    FinalColorationData: ColorationDataWithGradYear,
](
    BaseTreeTransformer[
        SettingData,
        InitialColorationData,
        OptEarlierGradYear,
        EarlierGradYear,
        FinalColorationData,
    ]
):
    def __init__(self, default_grad_year: int) -> None:
        super().__init__()
        self._default_init_grad_year = default_grad_year

    @override
    @classmethod
    def _data_of_interest(
        cls, node_data: ColorizedNodeData[SettingData, InitialColorationData]
    ) -> OptEarlierGradYear | None:
        return node_data.config.initial_grad_year

    @override
    @classmethod
    def _default_subtree_data_value(cls) -> OptEarlierGradYear:
        return None

    def infer_earlier_grad_year_for_unspecified(
        self,
        dfs_ordered_subtrees: list[
            IndependantSubTree[SettingData, InitialColorationData, OptEarlierGradYear]
        ],
        unspecified_subtree_idx: int,
    ) -> EarlierGradYear:
        """The shallowest subtrees can omit their earlier graduation year setting.

        This function is here to infer it from the child subtrees of the
        unspecified subtree.
        """
        unspecified_subtree = dfs_ordered_subtrees[unspecified_subtree_idx]
        subtree_number = len(dfs_ordered_subtrees)
        i = unspecified_subtree_idx + 1
        earlier_grad_year = -1
        while i < subtree_number and is_subtree_ancestor(
            unspecified_subtree, child_subtree := dfs_ordered_subtrees[i]
        ):
            # a child subtree is always annotated (by definition of the sep)
            child_grad_year = cast(EarlierGradYear, child_subtree.data)
            related_ancestor_depth = unspecified_subtree.subtree.depth(
                child_subtree.ancestor
            )
            infered_grad_year = child_grad_year - related_ancestor_depth
            if earlier_grad_year < 0 or earlier_grad_year > infered_grad_year:
                earlier_grad_year = infered_grad_year
            i += 1
        return (
            earlier_grad_year
            if earlier_grad_year >= 0
            else self._default_init_grad_year
        )

    def infer_earlier_grad_year_everywhere(
        self,
        dfs_ordered_subtrees: list[
            IndependantSubTree[SettingData, InitialColorationData, OptEarlierGradYear]
        ],
    ):
        def rf(
            acc: tuple[
                EarlierGradYear,
                list[
                    IndependantSubTree[
                        SettingData, InitialColorationData, EarlierGradYear
                    ]
                ],
            ],
            elt: tuple[
                int,
                IndependantSubTree[
                    SettingData, InitialColorationData, OptEarlierGradYear
                ],
            ],
        ) -> tuple[
            EarlierGradYear,
            list[
                IndependantSubTree[SettingData, InitialColorationData, EarlierGradYear]
            ],
        ]:
            idx, (ancestor, opt_grad_year, subtree) = elt
            grad_year_for_elt = (
                opt_grad_year
                if opt_grad_year is not None
                else self.infer_earlier_grad_year_for_unspecified(
                    dfs_ordered_subtrees, idx
                )
            )
            current_earlier_grad_year, acc_annotated_subtree_list = acc
            earlier_grad_year = (
                grad_year_for_elt
                if current_earlier_grad_year < 0
                or grad_year_for_elt < current_earlier_grad_year
                else current_earlier_grad_year
            )
            return (
                earlier_grad_year,
                [
                    *acc_annotated_subtree_list,
                    IndependantSubTree(ancestor, grad_year_for_elt, subtree),
                ],
            )

        earlier_grad_year_for_family, labeled_subtrees = reduce(
            rf,
            enumerate(dfs_ordered_subtrees),
            cast(
                tuple[
                    EarlierGradYear,
                    list[
                        IndependantSubTree[
                            SettingData, InitialColorationData, EarlierGradYear
                        ]
                    ],
                ],
                (-1, []),
            ),
        )
        return earlier_grad_year_for_family, labeled_subtrees

    @classmethod
    def create_fake_node(
        cls,
        tree: TypedTree[ColorizedNodeData[SettingData, FinalColorationData]],
        colorize_data: ColorationFunction[
            SettingData, InitialColorationData, EarlierGradYear, FinalColorationData
        ],
        parent: TypedNode[ColorizedNodeData[SettingData, FinalColorationData]]
        | SentinelNode,
        grad_year: int,
    ) -> TypedNode[ColorizedNodeData[SettingData, FinalColorationData]]:
        new_fake_node_id = create_new_fake_node_id()
        return cast(
            TypedNode[ColorizedNodeData[SettingData, FinalColorationData]],
            tree.create_node(
                new_fake_node_id,
                new_fake_node_id,
                parent,
                colorize_data(
                    ColorizedNodeData(
                        colorizedData=None,
                        config=BaseSettingData(
                            id=new_fake_node_id, name=new_fake_node_id
                        ),
                    ),
                    grad_year,
                ),
            ),
        )

    @classmethod
    def add_fake_nodes(
        cls,
        tree: TypedTree[ColorizedNodeData[SettingData, FinalColorationData]],
        colorize_data: ColorationFunction[
            SettingData, InitialColorationData, EarlierGradYear, FinalColorationData
        ],
        from_node: TypedNode[ColorizedNodeData[SettingData, FinalColorationData]]
        | SentinelNode,
        from_grad_year: EarlierGradYear,
        to_grad_year: EarlierGradYear,
    ) -> TypedNode[ColorizedNodeData[SettingData, FinalColorationData]] | SentinelNode:
        return reduce(
            lambda last_node, grad_year: cls.create_fake_node(
                tree, colorize_data, last_node, grad_year
            ),
            range(from_grad_year + 1, to_grad_year),
            from_node,
        )

    @override
    def _merge_subtrees(
        self,
        dfs_ordered_subtrees: list[
            IndependantSubTree[SettingData, InitialColorationData, OptEarlierGradYear]
        ],
        colorize_data: ColorationFunction[
            SettingData, InitialColorationData, EarlierGradYear, FinalColorationData
        ],
    ) -> TypedTree[ColorizedNodeData[SettingData, FinalColorationData]]:
        earlier_grad_year_for_family, labeled_subtress = (
            self.infer_earlier_grad_year_everywhere(dfs_ordered_subtrees)
        )
        aligned_tree = init_tree(ColorizedNodeData[SettingData, FinalColorationData])
        aligned_tree_sentinel_grad_year = earlier_grad_year_for_family - 1
        for subtree_ancestor, subtree_root_grad_year, subtree in labeled_subtress:
            for ancestor, node in depth_first_search(subtree):
                member_grad_year = subtree_root_grad_year + subtree.depth(node) - 1

                if is_real_node(ancestor):
                    aligned_tree.create_node(
                        node.identifier,
                        node.identifier,
                        ancestor.identifier,
                        colorize_data(node.data, member_grad_year),
                    )
                    continue

                unaligned_ancestor_in_aligned_tree = aligned_tree.get_node(
                    subtree_ancestor.identifier
                )
                if unaligned_ancestor_in_aligned_tree is None:
                    raise Exception(
                        "As the subtrees are dfs ordered, this case is impossible"
                    )
                unaligned_ancestor_grad_year = (
                    unaligned_ancestor_in_aligned_tree.data.colorizedData.initial_grad_year
                    if is_real_node(unaligned_ancestor_in_aligned_tree)
                    else aligned_tree_sentinel_grad_year
                )
                if member_grad_year <= unaligned_ancestor_grad_year:
                    raise BadTreeConfigException(
                        f'"{node.data.config.name}" could not get to school before his/her ancestor, even if it would be fun. ({member_grad_year=} <= ancestor_grad_year={unaligned_ancestor_grad_year})'
                    )
                actual_ancestor_in_aligned_tree = self.add_fake_nodes(
                    aligned_tree,
                    colorize_data,
                    unaligned_ancestor_in_aligned_tree,
                    unaligned_ancestor_grad_year,
                    member_grad_year,
                )
                aligned_tree.create_node(
                    node.identifier,
                    node.identifier,
                    actual_ancestor_in_aligned_tree,
                    colorize_data(node.data, member_grad_year),
                )

        return aligned_tree
