from graphviz import Digraph, Source as GraphvizSource
import pathlib

from .tree_viz_config import FamilyTreeConfig
from .config_exceptions import BadTreeConfigException


BUILD_DIR = pathlib.Path("./out").resolve()


def pixels_to_inches(pixel_value: int) -> str:
    return str(pixel_value / 96)


ASSETS_DIR = BUILD_DIR.joinpath("assets")


def create_assets_symlink(scaled_images_dir: pathlib.Path):
    if not ASSETS_DIR.exists():
        ASSETS_DIR.symlink_to(scaled_images_dir.resolve(), True)


def get_asset_path(image_filename: pathlib.Path):
    """Create a symlink to the assets/ dir in the build dir, if required.

    Return the path."""
    asset_copy = ASSETS_DIR.joinpath(image_filename.name)
    if not asset_copy.exists():
        raise BadTreeConfigException(f"The following picture does not exist: {str(image_filename)}")
    return asset_copy.relative_to(BUILD_DIR)


def add_node(
    dot: Digraph,
    id_: str,
    name: str,
    img: str,
    color: str,
    invisible: bool,
    tree_config: FamilyTreeConfig,
):
    if invisible:
        dot.node(id_, style="invis")
        return

    image_rel_path = get_asset_path(pathlib.Path(img))

    # we use a complex xml table to insert both a picture and a label for the
    # node. The nested tables is here to support a correct box size fitting
    label = rf'''<
<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" WIDTH="100%">
    <TR><TD ALIGN="CENTER" VALIGN="MIDDLE">
    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
        <TR><TD FIXEDSIZE="true" ALIGN="CENTER" VALIGN="MIDDLE"
        WIDTH="{tree_config.max_picture_side_length}"
        HEIGHT="{tree_config.max_picture_side_length}"><IMG SRC="{image_rel_path}"/></TD></TR>
        <TR>
            <TD ALIGN="CENTER" VALIGN="MIDDLE" HEIGHT="{tree_config.text_height}"><FONT
            COLOR="{tree_config.font_color}" POINT-SIZE="15">{name}</FONT></TD>
        </TR>
    </TABLE>
    </TD></TR>
</TABLE>
  >'''
    dot.node(
        id_,
        label=label,
        fillcolor=color,
    )


def add_edge(dot: Digraph, u_id: str, v_id: str, invisible: bool):
    dot.edge(u_id, v_id, style="invis" if invisible else None)


def init_tree(filename: str, scaled_images_dir: pathlib.Path, tree_config: FamilyTreeConfig):
    create_assets_symlink(scaled_images_dir)
    return Digraph(
        name=filename,
        comment="Tree of the Holy Family",
        node_attr={"shape": "ellipse", "style": "filled", "color": "none"},
        graph_attr={
            "bgcolor": "#fafafa",
            # we harmonize the scale across the formats (png, svg)
            "dpi": "96",
            "imagescale": "true",
            # vertical tree
            "rankdir": "TB" if tree_config.tb_randkir else "LR",
            "splines": "curved",
            "nodesep": pixels_to_inches(tree_config.node_sep_distance),
            # space between the nodes
            "ranksep": pixels_to_inches(tree_config.edge_length),
        },
    )


def render_tree(tree: Digraph, filename: str):
    tree.render(
        filename=filename,
        directory=BUILD_DIR,
        # rendering to support the font aligning
        engine="dot",
        renderer="cairo",
        format="svg",
        outfile=BUILD_DIR / (filename + ".svg"),
    )
    print("⚙️ Generated the Family Tree's graph file")
    print("✨ Produced the Family Tree in svg")
    # the graph .gv file is already generated; opening it
    tree_dot = GraphvizSource.from_file(BUILD_DIR / filename)
    tree_dot.render(
        filename,
        directory=BUILD_DIR,
        format="png",
        # same rendering as in svg
        engine="dot",
        renderer="cairo",
        outfile=BUILD_DIR / (filename + ".png"),
    )
    print("✨ Produced the Family Tree in png")
