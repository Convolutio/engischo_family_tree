from typing import Literal, override
from pydantic import BaseModel

from familytree.base_tree_transformer import BaseTreeTransformer, ColorationFunction
from familytree.tree_utils import (
    BaseSettingData,
    ColorizedNodeData,
    TypedTree,
    depth_first_search,
    init_tree,
    is_real_node,
    IndependantSubTree,
)


class ColorPair(BaseModel):
    start: str
    end: str


type InferredColor = str | None


class SettingDataWithColor(BaseSettingData):
    color_scale: ColorPair | None = None


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#").lower()

    def rgb_component(i: Literal[0, 2, 4]):
        return int(hex_color[i : i + 2], 16)

    return (rgb_component(0), rgb_component(2), rgb_component(4))


def depth_color(
    color_scale: ColorPair | None, depth: int, max_depth: int
) -> InferredColor:
    """
    Returns a hex color (#RRGGBB) that gets darker with depth.
    """
    if color_scale is None:
        return None
    start, end = hex_to_rgb(color_scale.start), hex_to_rgb(color_scale.end)
    # Clamp between 0–1
    t = 0 if max_depth <= 1 else min(max((depth - 1) / (max_depth - 1), 0), 1)

    # Interpolate between two RGB colors
    r = int(start[0] + t * (end[0] - start[0]))
    g = int(start[1] + t * (end[1] - start[1]))
    b = int(start[2] + t * (end[2] - start[2]))

    return f"#{r:02x}{g:02x}{b:02x}"


class ColorationDataWithColor(BaseModel):
    color: InferredColor


class ColorDispatcher[
    SettingData: SettingDataWithColor,
    InitialColorationData: BaseModel,
    MergedColorationData: ColorationDataWithColor,
](
    BaseTreeTransformer[
        SettingData,
        InitialColorationData,
        ColorPair | None,
        InferredColor,
        MergedColorationData,
    ]
):
    @override
    @classmethod
    def _data_of_interest(
        cls, node_data: ColorizedNodeData[SettingData, InitialColorationData]
    ):
        return node_data.config.color_scale

    @override
    @classmethod
    def _default_subtree_data_value(cls) -> ColorPair | None:
        return None

    @override
    def _merge_subtrees(
        self,
        dfs_ordered_subtrees: list[
            IndependantSubTree[SettingData, InitialColorationData, ColorPair | None]
        ],
        colorize_data: ColorationFunction[
            SettingData, InitialColorationData, InferredColor, MergedColorationData
        ],
    ) -> TypedTree[ColorizedNodeData[SettingData, MergedColorationData]]:
        colorized_tree = init_tree(ColorizedNodeData[SettingData, MergedColorationData])
        for inde_tree_ancestor, color_scale, inde_tree in dfs_ordered_subtrees:
            color_scale = color_scale if not isinstance(color_scale, bool) else None
            inde_tree_depth = inde_tree.depth()
            # the nodes are added with their parents after them, as the
            # independant_trees has been added in a depth-first search
            # mode
            for ancestor, node in depth_first_search(inde_tree):
                node_data = node.data
                colorized_tree.create_node(
                    node.identifier,
                    node.identifier,
                    ancestor.identifier
                    if is_real_node(ancestor)
                    else inde_tree_ancestor.identifier,
                    colorize_data(
                        node_data,
                        depth_color(
                            color_scale, inde_tree.depth(node), inde_tree_depth
                        ),
                    ),
                )
        return colorized_tree
