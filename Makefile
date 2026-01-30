PALETTE_MAP=rainbow.map
TEMPLATE_FONT=

FONT_FILE=$(notdir $(basename $(TEMPLATE_FONT)))
PALETTE_NAME=$(notdir $(basename $(PALETTE_MAP)))

BUILD_DIR=build
TINT_FLAGS=--palette-map $(PALETTE_MAP)

ifneq ($(FONT_NAME),)
TINT_FLAGS+=--font-name "$(FONT_NAME)"
endif

all: $(BUILD_DIR)/$(FONT_FILE).$(PALETTE_NAME).ttf

$(BUILD_DIR)/$(FONT_FILE).ttf: $(TEMPLATE_FONT) | $(BUILD_DIR)/
	cp $^ $@

%.$(PALETTE_NAME).ttf: %.ttf
	./tint.py $^ $@ $(TINT_FLAGS) 
	cp $@ $(BUILD_DIR)/Font.ttf

%.ascii.ttf: %.ttf
	pyftsubset $^ --unicodes="U+0000-007F" --output-file=$@

%/:
	mkdir -p $@

clean:
	rm -r build/*

.SECONDARY:
.DELETE_ON_ERROR:
