# Documentation

This directory contains the framework documentation built with MkDocs and Material theme.

## Serving Locally

```bash
# Using pipenv
pipenv run mkdocs serve

# Using make
make docs-serve
```

Access documentation at http://localhost:8000

## Building Documentation

```bash
# Using pipenv
pipenv run mkdocs build

# Using make
make docs-build
```

This creates a `site/` directory with static HTML files.

## Deploying to GitHub Pages

```bash
# Using pipenv
pipenv run mkdocs gh-deploy

# Using make
make docs-deploy
```

This deploys the documentation to the `gh-pages` branch.

## Documentation Structure

- `index.md` - Homepage
- `getting-started/` - Installation and quick start guides
- `building-agents/` - Agent patterns and configuration
- `api/` - API reference documentation
- `deployment/` - Deployment guides
- `testing/` - Testing documentation

## Adding New Documentation

1. Create markdown files in the appropriate directory
2. Update `mkdocs.yml` navigation to include new pages
3. Run `mkdocs serve` to preview changes
4. Commit and push changes
