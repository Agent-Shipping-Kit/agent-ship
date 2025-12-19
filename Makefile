.PHONY: docs-serve docs-build docs-deploy help

help:
	@echo "Available commands:"
	@echo "  make docs-serve    - Serve documentation locally (http://localhost:8000)"
	@echo "  make docs-build    - Build documentation site"
	@echo "  make docs-deploy   - Deploy documentation to GitHub Pages"

docs-serve:
	pipenv run mkdocs serve

docs-build:
	pipenv run mkdocs build

docs-deploy:
	pipenv run mkdocs gh-deploy
