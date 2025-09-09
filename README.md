# miserableprojects.directory (MVP)

Minimal publishing platform for indie/solo founders' failure post-mortems in a single, consistent format.

## Features (MVP)
- Built-in email/password auth (no third-party providers)
- Submit form (Markdown supported except H1/H2 headers; links nofollow)
- Home: Latest posts
- Post detail: tagline + 4 main sections + meta/OG
- (Reports removed for MVP)
- Sitemap.xml and RSS (latest 50)
- Static files via WhiteNoise; SQLite

## Setup
1) Python 3.11+ is recommended. Dependency management uses `uv`.

Install `uv` (macOS/Homebrew):
```bash
brew install uv
```

Or with `pipx`:
```bash
pipx install uv
```

Install project dependencies:
```bash
uv venv               # create .venv
source .venv/bin/activate
uv sync               # install from pyproject.toml (creates uv.lock)
python manage.py migrate
python manage.py createsuperuser
```

2) Development
```bash
python manage.py runserver
```

Environment variables
---------------------
Copy `.env.example` to `.env` and adjust values. Key vars:

- `DJANGO_DEBUG` — 1 for dev, 0 for prod
- `DJANGO_SECRET_KEY` — required in production
- `DJANGO_ALLOWED_HOSTS` — comma-separated list
- `DEFAULT_FROM_EMAIL` — default sender
- `USE_ANYMAIL` and `ANYMAIL_BACKEND` — optional email backend
- `MAILGUN_*` — if using Mailgun
- `ADMIN_URL` — Django admin URL path (default `admin/`); set to a non-obvious value in production.

## Developer Commands (just)
For convenience, a Justfile provides shortcuts for common tasks.

Install just:
- macOS (Homebrew): `brew install just`
- Ubuntu/Debian: `sudo apt-get install just` (or `snap install just --classic`)
- Arch: `pacman -S just`
- Windows: `winget install Casey.Just` or `choco install just`
- Anywhere: prebuilt binaries at https://github.com/casey/just/releases

Don’t want to use just? You can always run the underlying commands directly, e.g. `uv run python manage.py runserver` or `uv run python manage.py migrate`.

```bash
# one-off manage.py commands
just dj <args>                 # e.g., just dj showmigrations

# env + deps
just setup                     # creates venv and runs uv sync

# run server
just run

# database
just migrate                   # apply migrations
just makemigrations            # create migrations

# checks and tests
just check                     # system checks + migration check
just test                      # run Django tests (verbosity 2)

# users and data
just superuser                 # create admin user
just loaddata                  # load internetguzeldir.com fixture

# static files (prod)
just collectstatic             # collect static to STATIC_ROOT
```

Auth routes
-----------
- Login: `/accounts/login/`
- Logout: `/accounts/logout/`
- Signup: `/accounts/signup/`
- Password reset: `/accounts/password_reset/`

## Data Model
- `Submission` — content and meta fields
- (Removed) `Report`

## Acceptance Criteria (mapping)
- H1/H2 stripped on save (Markdown supported except H1/H2 headers): `apps/submissions/models.py:strip_h1_h2` and form `clean()`
- Submit requires login: `SubmitView(LoginRequiredMixin)`
- (Removed) Report admin
- Canonical + OG: `templates/submissions/detail.html`
- RSS: `/rss.xml`; Sitemap: `/sitemap.xml`
- Form errors: Django form errors are rendered

## Notes
- Markdown sanitize: `apps/submissions/markdown.py` (bleach + markdown)
- Clean URL: `/p/{slug}` (slug = `slugify(project_name)` + 6‑char id)
- Search and tag filters are tracked for v1.1

## Shared Templates (Partials)
These templates are reused across pages to keep markup consistent:

- `templates/partials/header.html`: Header/nav
- `templates/partials/footer.html`: Footer and RSS
- `templates/partials/messages.html`: Django messages
- `templates/partials/tag_nav.html`: Tag navigation; expects `tag_items`, `active_tag`
- `templates/partials/items_list.html`: Generic list; items need `get_absolute_url`, `project_name`, `created_at`
- `templates/partials/pagination.html`: Pagination; expects `page_obj`, `prev_url`, `next_url`
- `templates/partials/robots_noindex_if_paginated.html`: Adds `noindex,follow` for page > 1

Example usage:
```
{% include 'partials/tag_nav.html' %}
{% include 'partials/items_list.html' with items=submissions empty_text='No items yet.' date_format='m/Y' %}
{# build prev_url/next_url variables: #}
{% include 'partials/pagination.html' %}
```
