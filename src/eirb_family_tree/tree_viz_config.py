from pathlib import Path
import tomllib
from typing import cast
from pydantic import BaseModel, ValidationError
import logging

from .infer_color import SettingDataWithColor
from .infer_promo import SettingDataWithGraduationYear


class FamilyMemberConfig(SettingDataWithGraduationYear, SettingDataWithColor):
    ancestor: str | None = None
    picture: str | None = None


class FamilyTreeConfig(BaseModel):
    default_picture: str
    max_picture_side_length: int
    text_height: int
    font_color: str
    edge_length: int
    node_sep_distance: int
    default_node_color: str
    tb_randkir: bool
    default_grad_year: int
    members_config: list[FamilyMemberConfig]


_config: FamilyTreeConfig | None = None


def _open_config_file(tree_config_file: Path):
    with open(tree_config_file, "rb") as f:
        return tomllib.load(f)


def load_tree_from_config(tree_config_file: Path) -> FamilyTreeConfig:
    """Generate the tree from the config file."""
    global _config
    if _config is None:
        raw_config = _open_config_file(tree_config_file)
        try:
            members = [
                FamilyMemberConfig(**cast(dict, mc)) for mc in raw_config["member"]
            ]
            _config = FamilyTreeConfig(**raw_config, members_config=members)
        except ValidationError as val_error:
            logging.error(f"The {tree_config_file.name} file is wrongly defined:")
            raise val_error
    return _config
