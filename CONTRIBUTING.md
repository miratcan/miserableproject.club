Contributing
============

Thanks for considering a contribution! This project is a small Django app.

Local setup
-----------
- Python 3.11+
- Create a virtualenv and install: `pip install -e .`
- Copy `.env.example` to `.env` and adjust as needed
- Run checks: `python manage.py check`
- Run tests: `python manage.py test`

Guidelines
----------
- Keep changes minimal and focused; add tests when possible.
- Follow ASCII-only UI text in templates. Use `div.field` per form field and `div.actions` for buttons.
- Use conventional commit messages when practical.

Linting/formatting
------------------
- Optional: install pre-commit hooks: `pip install pre-commit && pre-commit install`
- Hooks run Black/Ruff on changed files.

Security
--------
- Don’t include real secrets or tokens in PRs.
- See SECURITY.md for reporting vulnerabilities.

