help:
    @just --list

# Install all the required deps
[group("install")]
install:
    pixi install

# Install all the deps, including the development one
[group("install")]
install-dev:
    pixi install -e dev

# Echo the command to enter in a venv with all the development deps
source-env-dev:
    @echo "pixi shell -e dev"

[group("test")]
type_check:
	@pixi run typecheck

[group("test")]
test:
	@pixi run test
