.PHONY: type_check test install install-dev clean-deps 

CONDA := conda
CONDA_ENV_NAME := family-tree
CONDA_RUN := $(CONDA) run -n $(CONDA_ENV_NAME) --no-capture-output

CONFIRM = @read -p "🚨 Confirm running '$@'? [y/N] " answer; \
	if [ "$$answer" != "y" ] && [ "$$answer" != "Y" ]; then \
		echo "❌ Cancelled."; exit 1; \
	fi

#  >>> TEST rules >>>

type_check:
	mypy ./src/

test:
	pytest

#  <<< TEST rules <<<

#  >>> INSTALL rules >>>

install:
	$(CONFIRM)
	$(CONDA) env create -n $(CONDA_ENV_NAME) -f environment.yml && \
		$(CONDA_RUN) pip install .

install-dev:
	$(CONFIRM)
	$(CONDA) env create -n $(CONDA_ENV_NAME) -f environment.yml && \
		$(CONDA_RUN) pip install -e .[dev]

#  <<< INSTALL rules <<<

clean-deps:
	$(CONFIRM)
	rm -rf ./src/*.egg-info build ./src/familytree/__pycache__ \
		./tests/__pycache__/ && \
		conda remove -n $(CONDA_ENV_NAME) --all
