from pathlib import Path

from .tree_viz_config import FamilyTreeConfig

from .tree_gen import FamilyTree

from . import styled_tree

def gen_with_graphviz(family_tree: FamilyTree, tree_config: FamilyTreeConfig, image_dir: Path, filename: str):

    rendered_graph = styled_tree.init_tree(filename, image_dir, tree_config)
    for (
        member_id,
        invisible,
        ancestor_id,
        real_ancestor_id,
        member_data,
    ) in family_tree.iterate_over_nodes():
        styled_tree.add_node(
            rendered_graph,
            member_id,
            member_data.name,
            member_data.picture,
            member_data.color,
            invisible,
            tree_config
        )
        if ancestor_id is not None:
            has_indirect_ancestor = (real_ancestor_id != ancestor_id)
            styled_tree.add_edge(
                rendered_graph,
                ancestor_id,
                member_id,
                has_indirect_ancestor or invisible,
            )
            if has_indirect_ancestor and real_ancestor_id is not None:
                styled_tree.add_edge(
                    rendered_graph, real_ancestor_id, member_id, False
                )

    styled_tree.render_tree(rendered_graph, filename)
