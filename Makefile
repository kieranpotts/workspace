#
# Task runners for this project's development lifecycle.
#

.PHONY: install help

help:
	@echo "Available targets:"
	@echo "  install  - Check out every repository listed in repos.yaml as an adjacent worktree"
	@echo "  help     - Show this help message"

install:
	./run/install.py
