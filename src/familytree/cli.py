import click
import subprocess
from pathlib import Path

from .graphviz_gen import gen_with_graphviz
from .tree_gen import FamilyTree
from .tree_viz_config import load_tree_from_config

_makefile_path = str(Path(__file__).parent / "Makefile")


def _run_makefile(target: str | list[str] | None = None):
    """Call the Makefile"""
    cmd: list[str] = ["make", "-f", _makefile_path]
    if isinstance(target, str):
        cmd.append(target)
    elif isinstance(target, list):
        for t in target:
            cmd.append(t)
    subprocess.run(cmd)


@click.group()
def main():
    pass


@main.command()
def init_workspace():
    """Init the workspace to custom a family tree with the eirbtree lib."""
    _run_makefile("init-workspace")


@main.command()
def build():
    """Build the family tree output files from the data files."""
    _run_makefile("build")


@main.command()
def watch():
    """Watch the family data files and rebuild the trees if required."""
    _run_makefile("watch")


@main.command()
@click.option("--png", is_flag=True, help="Display the png file instead of the svg")
def preview(png: bool):
    """Display one of the produced image with eog."""
    _run_makefile("preview" if not png else "preview-png")


@main.command()
def pack_output():
    """Archive the output pictures in an archive."""
    _run_makefile("pack-output")


@main.command()
@click.option(
    "--rescaled-images", is_flag=True, help="Also delete the rescaled images."
)
def clean(rescaled_images: bool):
    """Remove the produced files."""
    targets = ["clean"]
    if rescaled_images:
        targets.append("clean-rescaled-pictures")
    _run_makefile(targets)


@click.command()
@click.argument("output_filename")
@click.argument("tree_config_file")
@click.argument("image_dir")
def generate_tree(output_filename: str, tree_config_file: str, image_dir: str):
    """Generate the eirb family tree from the given workspace.

    Process the TREE_CONFIG_FILE and use the IMAGE_DIR to copy the rescaled
    pictures. Generate the output files with the given OUTPUT_FILENAME
    """
    tree_config = load_tree_from_config(Path(tree_config_file))
    generated_family_tree = FamilyTree(tree_config)
    gen_with_graphviz(
        generated_family_tree, tree_config, Path(image_dir), output_filename
    )


if __name__ == "__main__":
    main()
