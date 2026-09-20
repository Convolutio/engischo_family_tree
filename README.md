# 🖥️ Engineering school Family tree generator 🌳⚙️

Here is a library to compose its family tree from a TOML file and a directory
with pictures.

This project uses Python libraries, Make and external executables:

- Python >= 3.13 and its deps in the `pyproject.toml`
- Graphviz >= 2.43.0
- Image Magick >= 7.1.2-5 (to rescale images)
- Make (for efficient building)
- inotify-tools (for the watch mode)

> While only inotify-tools is used for the watch mode, this project only
> supports linux-64 architectures.

_To safely manage those dependencies_, we propose an installation with
[`pixi@v0.81.0`](https://pixi.prefix.dev/v0.81.0/installation/).

```sh
PIXI_VERSION=0.81.0 curl -fsSL https://pixi.sh/install.sh | sh
```

## Use the library

### Initiating the workspace

You can set a workspace to manage your family tree with the commands below,
inside your directory to store the data of your family tree.

> Those commands are reproducible and do not require any sudo permission. Feel
> free to directly copy/paste them in your shell, when in your directory.

```sh
# Init the pixi environment with the eirb_family_tree library ready to be used
# as a CLI
pixi init \
  --channel conda-forge \
  --platform linux-64
pixi workspace preview add pixi-build
#  The package is built from source in your machine
pixi add \
  --git https://github.com/Convolutio/engischo_family_tree.git \
  eirb_family_tree

# Use the eirbtree CLI to store an initial placeholder family tree in your directory
pixi run eirbtree init-workspace
```

Then you can edit your file. The `eirbtree` CLI allows you to build the tree,
preview it and watch your source files to dynamically rebuild it. To use the
CLI, do this.

```sh
# Go inside your virtual environment
pixi shell

# Finally, use eirbtree as you wish
eirbtree --help
```

### Build, preview and pack the output graph

__Stay into your environment to use the CLI:__

```sh
pixi shell
```

Then use the `eirbtree` CLI to work on your family tree.

1. Edit the `.env` file to customize the name of the output PNG, DOT and SVG
   files
2. Add pictures inside the `img` directory and edit the `family.toml` file.
   `eirbtree` can watch those files for an automatic rebuild of your family
   tree with the command below

   ```sh
   # in the same directory
   eirbtree watch
   ```

   If you just want a single build, just run the command below

   ```sh
   # in the same directory
   eirbtree build
   ```

3. To preview your produced tree, just run

   ```sh
   # in the same directory
   eirbtree preview
   ```

4. To pack the tree pictures in an archive, run

   ```sh
   # always stay in the directory of your family.toml when running eirbtree
   eirbtree pack-output
   ```

For details about the usage of `eirbtree`, the CLI has `--help` options.

### Remove the produced files

To remove only the produced archives and the built files:

```sh
# in the directory of your family.toml
eirbtree clean
```

### Uninstall the library

To purely remove the files produced by the virtual environment:

```sh
# be sure to leave the pixi environment before
# remove every local deps
pixi clean
```

### Family settings

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

## Develop the library

The library is a python package inside a pixi project.

If you want to edit the library, then inside this repository you can work in the
local pixi environment.

```sh
# Install and go into an isolated pixi environment with all the project deps
# The python package is sourced in editable mode so the CLI can be used with the
# edited source code
pixi shell
```

To work with the development dependencies (mypy, pytest...), then source this
environment instead:

```sh
# Install and go into an isolated pixi environment with all the project deps and
# the test deps
pixi shell -e dev
```

To build the package as in the library usage stage, run

```sh
pixi publish
```

There is also a `justfile` for lazy developers.

### References

- [Getting started with a Pixi workspace](https://pixi.prefix.dev/v0.81.0/first_workspace/)
- [Develop and build a Pixi package](https://pixi.prefix.dev/v0.81.0/build/getting_started/)
- [Develop and build a Pixi package with a python package inside its source code](https://pixi.prefix.dev/v0.81.0/build/python/)
- [Pixi python build backend references](https://pixi.prefix.dev/v0.81.0/build/backends/pixi-build-python/)

> NB: to build a python package with external deps in other languages (such as
> graphviz, make etc.), I do not know other alternatives than pixi/conda.
> Docker and nix are harder in the usage stage.
> The actual caveat with Pixi is that its building features are not stable. That
> is why it is recommended for now to use the version 0.81.0.
