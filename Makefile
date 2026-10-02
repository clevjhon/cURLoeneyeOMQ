.PHONY: all clean font doc manifest verify

all: font doc manifest

font:
	python3 build_true_ttf.py

doc: font
	xelatex test_oeneye.tex
	xelatex chapter_architecture.tex

manifest: doc
	sha256sum OMQ.ttf test_oeneye.pdf chapter_architecture.pdf oeneye.iso > manifest.sha256
	@echo "[SUCCESS] Full build suite and manifest generation complete."

verify:
	sha256sum -c manifest.sha256

clean:
	rm -f OMQ.ttf test_oeneye.pdf chapter_architecture.pdf test_oeneye.aux test_oeneye.log chapter_architecture.aux chapter_architecture.log manifest.sha256
