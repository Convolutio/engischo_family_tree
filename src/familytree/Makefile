# The user can declare the Parametres in a .env
-include .env

.PHONY: build watch preview preview-png pack-output \
	init-workspace clean-rescaled-pictures clean

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

clean-rescaled-pictures:
	$(CONFIRM)
	rm -f $(IMAGES_RESCALED_DIR)/*

clean:
	@rm -f $(OUTPUT).tar.gz
	@rm -f $(BUILD_DIR)/$(OUTPUT)*
	@rm -f $(BUILD_DIR)/assets
