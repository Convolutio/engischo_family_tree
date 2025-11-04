# The user can declare the Parametres in a .env
-include .env

.PHONY: build watch type_check test \
	preview preview-png pack-output \
	install install-dev init-workspace \
	clean-deps clean-rescaled-pictures clean

#  >>> Parametres >>>
FAMILY_DATA ?= family.toml
IMAGES_SRC_DIR ?= img
BUILD_DIR ?= out
IMAGES_RESCALED_DIR ?= _rescaled
OUTPUT ?= UnnamedFamily
#  <<< Parametres <<<

IMAGES_SRC := $(wildcard $(IMAGES_SRC_DIR)/*)
IMAGES_RESCALED := $(patsubst $(IMAGES_SRC_DIR)/%,$(IMAGES_RESCALED_DIR)/%,${IMAGES_SRC})
ROOT_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

CONDA := conda
CONDA_ENV_NAME := family-tree
CONDA_RUN := $(CONDA) run -n $(CONDA_ENV_NAME) --no-capture-output

CONFIRM = @read -p "🚨 Confirm running '$@'? [y/N] " answer; \
	if [ "$$answer" != "y" ] && [ "$$answer" != "Y" ]; then \
		echo "❌ Cancelled."; exit 1; \
	fi

#  >>> BUILD rules >>>

build: $(BUILD_DIR)/$(OUTPUT).svg $(BUILD_DIR)/$(OUTPUT).png \
	$(BUILD_DIR)/$(OUTPUT)

$(BUILD_DIR)/$(OUTPUT).svg $(BUILD_DIR)/$(OUTPUT).png \
	$(BUILD_DIR)/$(OUTPUT): $(FAMILY_DATA) $(IMAGES_RESCALED)
	eirbtree-generate $(OUTPUT) $(FAMILY_DATA) $(IMAGES_RESCALED_DIR)

$(IMAGES_RESCALED_DIR)/%: $(IMAGES_SRC_DIR)/%
	magick $^ -resize 160x160 $@

watch:
	@echo "👀 Wathing the $(FAMILY_DATA) and the $(IMAGES_SRC_DIR)/ directory... Ready to build!"
	while true; do \
		echo "⚙️ Building..."; \
		make -f $(ROOT_DIR)/Makefile  build; \
		inotifywait -qre close_write $(FAMILY_DATA); \
	done

#  <<< BUILD rules <<<

#  >>> OUTPUT rules >>>

preview: $(BUILD_DIR)/$(OUTPUT).svg
	eog $^

preview-png: $(BUILD_DIR)/$(OUTPUT).png
	eog $^

$(OUTPUT).tar.gz: $(BUILD_DIR)/$(OUTPUT).svg $(BUILD_DIR)/$(OUTPUT).png
	tar -cvzf $@ $<

pack-output: $(OUTPUT).tar.gz

#  <<< OUTPUT rules <<<

#  >>> TEST rules >>>

type_check:
	mypy $(ROOT_DIR)/src/

test:
	pytest

#  <<< TEST rules <<<

#  >>> INIT WORKSPACE >>>

$(BUILD_DIR):
	@mkdir $@

$(IMAGES_SRC_DIR):
	cp -r $(ROOT_DIR)/img.example $@

$(IMAGES_RESCALED_DIR):
	@mkdir $@

$(FAMILY_DATA):
	cp $(ROOT_DIR)/family.example.toml $@

.env:
	cp $(ROOT_DIR)/.env.example $@

init-workspace: $(FAMILY_DATA) .env $(BUILD_DIR) $(IMAGES_SRC_DIR) \
	$(IMAGES_RESCALED_DIR)

#  <<< INIT WORKSPACE <<<

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
	rm -rf ./src/eirb_family_tree.egg-info build ./src/familytree/__pycache__ && \
		conda remove -n $(CONDA_ENV_NAME) --all

clean-rescaled-pictures:
	$(CONFIRM)
	rm -f $(IMAGES_RESCALED_DIR)/*

clean:
	@rm -f $(OUTPUT).tar.gz
	@rm -f $(BUILD_DIR)/$(OUTPUT)*
	@rm -f $(BUILD_DIR)/assets
