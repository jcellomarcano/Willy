# Makefile for Willy* Compiler and Simulator

.PHONY: all install test benchmark clean

all: test

install:
	@mkdir -p ~/.local/bin
	@echo '#!/usr/bin/env bash' > ~/.local/bin/willy
	@echo 'export PYTHONPATH="$(shell pwd):$${PYTHONPATH}"' >> ~/.local/bin/willy
	@echo 'exec python3 -m willy.cli "$$@"' >> ~/.local/bin/willy
	@chmod +x ~/.local/bin/willy
	@echo "Willy* wrapper installed to ~/.local/bin/willy"

test:
	python3 test_runner.py

benchmark:
	python3 benchmark.py

clean:
	rm -rf __pycache__ willy/__pycache__ tests/__pycache__
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
