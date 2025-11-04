from pathlib import Path
from familytree.graphviz_gen import gen_with_graphviz
from familytree.tree_gen import FamilyTree
from familytree.tree_viz_config import load_tree_from_config
from typing import cast

import argparse

def get_cli_options():
    parser = argparse.ArgumentParser(description="Eirb Family tree Generator")
    parser.add_argument("filename", help="The name of the output file.")
    parser.add_argument("tree_config_file", help="The toml file with the tree config.")
    parser.add_argument("image_dir", help="Directory with the rescaled images.")
    args = parser.parse_args()
    return cast(str, args.filename), Path(args.tree_config_file), Path(args.image_dir)


if __name__ == "__main__":
    filename, tree_config_file, image_dir = get_cli_options()
    tree_config = load_tree_from_config(tree_config_file)
    generated_family_tree = FamilyTree(tree_config)
    gen_with_graphviz(generated_family_tree, tree_config, image_dir, filename)

