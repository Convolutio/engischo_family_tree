from collections.abc import Callable
from typing import Any, Iterator, Type, TypeGuard, override, NamedTuple, cast
from pydantic import BaseModel
from treelib.node import Node
from treelib.tree import Tree


class SentinelNode(Node):
    """Cast with this class so the data attribute has a fixed type."""

    data: None


class TypedNode[T](Node):
    """Cast with this class so the data attribute has a fixed type."""

    data: T


class TypedTree[T](Tree):
    def __init__(
        self,
        tree=None,
        deep: bool = False,
        node_class=None,
        identifier: str | None = None,
    ) -> None:
        super().__init__(tree, deep, node_class, identifier)

    @override
    def create_node(
        self,
        tag: str | None = None,
        identifier: str | None = None,
        parent: Node | str | None = None,
        data: T | None = None,
    ) -> TypedNode[T] | SentinelNode:
        # Assuming the data as T excepted for the sentinel
        return cast(
            TypedNode[T] | SentinelNode,
            super().create_node(tag, identifier, parent, data),
        )

    @override
    def get_node(self, nid: str | None) -> TypedNode[T] | SentinelNode | None:
        # Assuming the data as T excepted for the sentinel
        return cast(TypedNode[T] | None | SentinelNode, super().get_node(nid))


class NodeAndAncestor[T](NamedTuple):
    ancestor: TypedNode[T] | SentinelNode  # a node or the sentinel for the root
    node: TypedNode[T]


SENTINEL_ID = "<SENTINEL>"


def is_sentinel(node: TypedNode[Any] | SentinelNode) -> TypeGuard[SentinelNode]:
    return node.identifier == SENTINEL_ID


def is_real_node[T](node: TypedNode[T] | SentinelNode) -> TypeGuard[TypedNode[T]]:
    return not is_sentinel(node)


def init_tree[T](node_type: Type[T]) -> TypedTree[T]:
    node_type = node_type  # unused (for type inference)
    new_tree = TypedTree[T]()
    new_tree.create_node(SENTINEL_ID, SENTINEL_ID, None)
    return new_tree


def depth_first_search[T](tree: TypedTree[T]) -> Iterator[NodeAndAncestor[T]]:
    node_it = (
        node
        for node in (tree.get_node(nid) for nid in tree.expand_tree(mode=Tree.DEPTH))
        if node is not None
    )
    next(node_it)  # remove the sentinel
    return (
        NodeAndAncestor(
            cast(
                TypedNode[T] | SentinelNode,
                tree.get_node(cast(str, tree.ancestor(node.identifier))),
            ),
            cast(TypedNode[T], node),
        )
        for node in node_it
    )


class BaseSettingData(BaseModel):
    id: str
    name: str


class ColorizedNodeData[SettingData: BaseSettingData, ColorizedData](BaseModel):
    colorizedData: ColorizedData
    config: SettingData


class IndependantSubTree[
    SettingData: BaseSettingData,
    InitialColorationData,
    NewColorizationData,
](NamedTuple):
    ancestor: (
        TypedNode[ColorizedNodeData[SettingData, InitialColorationData]] | SentinelNode
    )
    data: NewColorizationData
    subtree: TypedTree[ColorizedNodeData[SettingData, InitialColorationData]]


def create_data_independant_subtrees[
    SettingData: BaseSettingData,
    InitialColorationData,
    NewColorationData,
](
    tree: TypedTree[ColorizedNodeData[SettingData, InitialColorationData]],
    data_of_interest: Callable[
        [ColorizedNodeData[SettingData, InitialColorationData]],
        NewColorationData | None,
    ],
    default_data_value: NewColorationData,
) -> list[IndependantSubTree[SettingData, InitialColorationData, NewColorationData]]:
    """Return the list of independant subtrees labeled with a given data.

    The T data type must not include None.

    Arguments:
    * data_of_interest: take the node data and return the data if available
    """
    independant_trees: list[
        IndependantSubTree[SettingData, InitialColorationData, NewColorationData]
    ] = []
    inde_tree_of_node: dict[str, int] = {}
    for ancestor, node in depth_first_search(tree):
        node_data = node.data
        subtree_data = data_of_interest(node_data)
        if subtree_data is not None or is_sentinel(ancestor):
            # create new independant tree if a color has been defined
            inde_tree = init_tree(ColorizedNodeData[SettingData, InitialColorationData])
            inde_tree.create_node(
                node_data.config.id,
                node_data.config.id,
                SENTINEL_ID,
                data=node_data,
            )
            independant_trees.append(
                IndependantSubTree(
                    ancestor,
                    subtree_data if subtree_data is not None else default_data_value,
                    inde_tree,
                )
            )
            inde_tree_of_node[node.identifier] = len(independant_trees) - 1
        else:
            # add the child in the independant tree of its parent
            inde_tree_idx = inde_tree_of_node[ancestor.identifier]
            inde_tree = independant_trees[inde_tree_idx][2]
            inde_tree.create_node(
                node_data.config.id, node_data.config.id, ancestor, data=node_data
            )
            inde_tree_of_node[node.identifier] = inde_tree_idx
    return independant_trees


def is_subtree_ancestor[
    SettingData: BaseSettingData,
    InitialColorationData,
    NewColorationData,
](
    subtree: IndependantSubTree[SettingData, InitialColorationData, NewColorationData],
    other_subtree: IndependantSubTree[
        SettingData, InitialColorationData, NewColorationData
    ],
) -> bool:
    if is_sentinel(other_subtree.ancestor):
        return False
    return subtree.subtree.get_node(other_subtree.ancestor.identifier) is not None
