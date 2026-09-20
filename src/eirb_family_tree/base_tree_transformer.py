from abc import ABC, abstractmethod
from typing import Callable

from pydantic import BaseModel

from eirb_family_tree.tree_utils import (
    BaseSettingData,
    ColorizedNodeData,
    IndependantSubTree,
    TypedTree,
    create_data_independant_subtrees,
)

type ColorationFunction[
    SettingData: BaseSettingData,
    InitialColorationData: BaseModel,
    NewColorationData,
    FinalColorationData: BaseModel,
] = Callable[
    [
        ColorizedNodeData[SettingData, InitialColorationData]
        | ColorizedNodeData[BaseSettingData, None],
        NewColorationData,
    ],
    ColorizedNodeData[SettingData, FinalColorationData],
]


class BaseTreeTransformer[
    SettingData: BaseSettingData,
    InitialColorationData: BaseModel,
    PerSubtreeColorationData,
    NewColorationData,
    MergedColorationData: BaseModel,
](ABC):
    @classmethod
    @abstractmethod
    def _data_of_interest(
        cls, node_data: ColorizedNodeData[SettingData, InitialColorationData]
    ) -> PerSubtreeColorationData | None:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _default_subtree_data_value(cls) -> PerSubtreeColorationData:
        raise NotImplementedError

    @classmethod
    def _divide_into_subtrees(
        cls, tree: TypedTree[ColorizedNodeData[SettingData, InitialColorationData]]
    ) -> list[
        IndependantSubTree[SettingData, InitialColorationData, PerSubtreeColorationData]
    ]:
        return create_data_independant_subtrees(
            tree, cls._data_of_interest, cls._default_subtree_data_value()
        )

    @abstractmethod
    def _merge_subtrees(
        self,
        dfs_ordered_subtrees: list[
            IndependantSubTree[
                SettingData, InitialColorationData, PerSubtreeColorationData
            ]
        ],
        colorize_data: ColorationFunction[
            SettingData, InitialColorationData, NewColorationData, MergedColorationData
        ],
    ) -> TypedTree[ColorizedNodeData[SettingData, MergedColorationData]]:
        raise NotImplementedError

    def transform(
        self,
        tree: TypedTree[ColorizedNodeData[SettingData, InitialColorationData]],
        colorize_data: ColorationFunction[
            SettingData, InitialColorationData, NewColorationData, MergedColorationData
        ],
    ) -> TypedTree[ColorizedNodeData[SettingData, MergedColorationData]]:
        return self._merge_subtrees(self._divide_into_subtrees(tree), colorize_data)
