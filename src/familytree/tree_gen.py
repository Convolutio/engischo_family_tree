"""Generate the family tree according to the TOML file.

See the readme for the structure of the toml file.
"""

from collections.abc import Iterator
from typing import NamedTuple, cast
from pydantic import BaseModel
import pathlib
from treelib.exceptions import NodeIDAbsentError

from .infer_color import (
    ColorDispatcher,
    ColorationDataWithColor,
)
from .infer_promo import (
    ColorationDataWithGradYear,
    GraduationYearAlignator,
)
from .tree_utils import (
    SENTINEL_ID,
    ColorizedNodeData,
    TypedTree,
    depth_first_search,
    init_tree,
    is_sentinel,
)

from .config_exceptions import BadTreeConfigException

from .tree_viz_config import (
    FamilyMemberConfig,
    FamilyTreeConfig,
)


def coalesce[T](value: T | None, default_value: T) -> T:
    return value if value is not None else default_value


# --- Final data given for graphviz ---


class FamilyMemberFinalData:
    name: str
    picture: str
    color: str
    initial_grad_year: int

    def __init__(
        self,
        name: str,
        image: str,
        color: str,
        initial_promo: int,
    ) -> None:
        if not pathlib.Path("./_rescaled/").joinpath(image).exists():
            raise BadTreeConfigException(
                f"The picture {image} does not exist in its rescaled version."
            )
        self.name = name
        self.picture = f"./_rescaled/{image}"
        self.color = color
        self.initial_promo = initial_promo


class FamilyMember(NamedTuple):
    id_: str
    invisible: bool
    ancestor_id: str | None
    real_ancestor_id: str | None
    data: FamilyMemberFinalData


# --- Final data given for graphviz ---


# --- Inferred attributes ---


class BaseColorizedData(BaseModel):
    pass


# First computed coloration data : in ColorationDataWithGradYear


class FullColorationData(ColorationDataWithGradYear, ColorationDataWithColor):
    pass


# --- Inferred attributes ---


class FamilyTree:
    _tree: TypedTree[ColorizedNodeData[FamilyMemberConfig, FullColorationData]]
    _default_picture: str
    _default_color: str

    def __init__(self, tree_config: FamilyTreeConfig) -> None:
        nodes = tree_config.members_config
        self._default_picture = tree_config.default_picture
        self._default_color = tree_config.default_node_color

        # build a first tree
        new_tree = init_tree(ColorizedNodeData[FamilyMemberConfig, BaseColorizedData])
        for node in nodes:
            new_tree.create_node(
                node.id,
                node.id,
                SENTINEL_ID,
                data=ColorizedNodeData(colorizedData=BaseColorizedData(), config=node),
            )
        for node in nodes:
            if node.ancestor is not None:
                try:
                    new_tree.move_node(node.id, node.ancestor)
                except NodeIDAbsentError:
                    raise BadTreeConfigException(
                        f"The specified ancestor {node.ancestor} is not defined"
                    )

        alignment_inferrer = GraduationYearAlignator[
            FamilyMemberConfig, BaseColorizedData, ColorationDataWithGradYear
        ](tree_config.default_grad_year)
        color_inferrer = ColorDispatcher[
            FamilyMemberConfig, ColorationDataWithGradYear, FullColorationData
        ]()

        aligned_tree = alignment_inferrer.transform(
            new_tree,
            lambda old_node, init_grad_year: ColorizedNodeData(
                config=(
                    old_node.config
                    if isinstance(old_node.config, FamilyMemberConfig)
                    else FamilyMemberConfig(
                        id=old_node.config.id, name=old_node.config.name
                    )
                ),
                colorizedData=ColorationDataWithGradYear(
                    initial_grad_year=init_grad_year,
                ),
            ),
        )
        final_tree = color_inferrer.transform(
            aligned_tree,
            lambda old_node, inferred_color: ColorizedNodeData(
                config=cast(
                    ColorizedNodeData[FamilyMemberConfig, ColorationDataWithGradYear],
                    old_node,
                ).config,
                colorizedData=FullColorationData(
                    initial_grad_year=cast(
                        ColorizedNodeData[
                            FamilyMemberConfig, ColorationDataWithGradYear
                        ],
                        old_node,
                    ).colorizedData.initial_grad_year,
                    color=inferred_color,
                ),
            ),
        )

        self._tree = final_tree

    def iterate_over_nodes(self) -> Iterator[FamilyMember]:
        """Iterate in with a depth first search algorithm.

        So the edges can be added.
        """
        return (
            FamilyMember(
                member.identifier,
                member.data.config.name.startswith("deadbeef"),
                ancestor.identifier if not is_sentinel(ancestor) else None,
                member.data.config.ancestor,
                FamilyMemberFinalData(
                    member.data.config.name,
                    coalesce(member.data.config.picture, self._default_picture),
                    coalesce(member.data.colorizedData.color, self._default_color),
                    member.data.colorizedData.initial_grad_year,
                ),
            )
            for ancestor, member in depth_first_search(self._tree)
        )
