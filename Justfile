set dotenv-load := false

# Helper to run Django management commands via uv
dj *args:
    uv run python manage.py {{args}}

# Common tasks
setup:
    uv venv
    source .venv/bin/activate && uv sync

run:
    just dj runserver

migrate:
    just dj migrate --noinput

makemigrations:
    just dj makemigrations

check:
    just dj check
    just dj makemigrations --check --dry-run

test:
    just dj test -v 2

collectstatic:
    just dj collectstatic --noinput

superuser:
    just dj createsuperuser

loaddata file="apps/submissions/fixtures/internetguzeldir_submission.json":
    just dj loaddata {{file}}

shell:
    just dj shell
