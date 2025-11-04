# 🖥️ Engineering school Family tree generator 🌳⚙️

Here is library to compose its family tree from a TOML file and a directory
with pictures.

## Install

This project uses Python librairies, Make and external librairies:

- Python >= 3.13 and its deps in the `pyproject.toml`
- Graphviz >= 2.43.0
- Image Magick >= 7.1.2-5 (to rescale images)
- Make (for efficient building)
- inotify-tools (for the watch mode)

_To safely manage those dependencies_, we propose an installation with
[`conda`](https://github.com/conda-forge/miniforge?tab=readme-ov-file#install).

The Makefile target below creates a conda env called `family-tree` with the
system deps and the built python package

```sh
# Creates an isolated conda environment family-tree with all the project deps
make install
```

To develop on the Python project or run the tests, choose this installation rule:

```sh
# Add pytest and let the installed familytree package be edited
make install-dev
```

## Build, preview and pack the output graph

__Stay into your environment with the built python package:__

```sh
conda activate family-tree
```

Then use the `eirbtree` CLI to work on your family tree.

1. In another directory in your system, create all the required source files

   ```sh
   # wherever you want, e.g. in the my-awesome-family/ directory
   eirbtree init-workspace
   ```

2. Edit the `.env` file to customize the name of the output PNG, DOT and SVG
   files
3. Add pictures inside the `img` directory and edit the `family.toml` file.
   `eirbtree` can watch those files for an automatic rebuild of your family
   tree with the command below

   ```sh
   # in the same directory
   eirbtree watch
   ```

   If you just want a single build, just run the command below

   ```sh
   eirbtree build
   ```

4. To preview your produced tree, just run

   ```sh
   # in the same directory
   eirbtree preview
   ```

5. To pack the tree pictures in an archive, run

   ```sh
   # always stay in the directory of your family.toml when running eirbtree
   eirbtree clean
   ```

For details about the usage of `eirbtree`, the CLI has `--help` options.

## Remove the produced files

To remove only the produced archives and the built files:

```sh
# in the directory of your family.toml
eirbtree clean
```

## Uninstall the library

To purely remove the files produced by the virtual environment:

```sh
# be sure to leave the conda environment before
conda deactivate family-tree
# remove pip installation + conda virtual environment
make clean-deps
```

## Family settings

- The picture of a member must be in the `img` directory (no constraint on the
  shape, just PNG or JPG/JPEG format --- the image will be rescaled)
- The `family.toml` file contains
  - the general tree parameters in the beginning of the TOML file
  - the information about the members (___single___ ancestor, picture, name,
  ...)

  See the content of the generated `family.toml` when running `eirbtree
  init-workspace`

  ```toml
  [[member]]
  id = "member-id"
  name = "The first member"

  [[member]]
  id = "member-second"
  name = "The son of the first member"
  # picture is optional
  picture = "member-second.png"
  # ancestor is optional
  ancestor = "member-id"
  # color_scale is optional
  # define the color scale of the member cards in the subtree of the member
  color_scale = { start = "#ff0000", end = "#ffd700" }
  # initial_promo is optional
  # define when the member was supposed to be graduated when he arrived in the
  # school (fill in for at least one member of a line of descent so it is
  # aligned with the others)
  initial_grad_year = 2028
  ```
