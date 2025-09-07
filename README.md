# miserableproject.club (MVP)

Minimal publishing platform for indie/solo founders’ failure post‑mortems in a single, consistent format.

## Features (MVP)
- OAuth via Reddit/Google (django‑allauth)
  - Only third‑party logins are allowed (no local/password accounts, no verification emails).
- Submit form (Markdown, strips H1/H2 in body, links nofollow)
- Home: Latest posts
- Post detail: 4 main sections + meta/OG
- Report flow and simple admin actions
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
just loaddata                  # load sample submissions fixture

# static files (prod)
just collectstatic             # collect static to STATIC_ROOT
```

3) Environment variables
- `DJANGO_SECRET_KEY` — required in production
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- `DEFAULT_OG_IMAGE` — optional (defaults to placeholder). You can also set `MISERABLEPROJECT_DEFAULT_OG_IMAGE`.

4) Allauth provider setup
- Admin > Sites (`SITE_ID=1`): set your domain
- Admin > Social applications: create Reddit/Google apps and attach to site

## Data Model
- `Submission` — content and meta fields
- `Report` — target, reason, status (open/closed)

## Acceptance Criteria (mapping)
- H1/H2 stripped on save: `apps/submissions/models.py:strip_h1_h2` and form `clean()`
- Submit requires login: `SubmitView(LoginRequiredMixin)`
- Report admin: `apps/submissions/admin.py`
- Canonical + OG: `templates/submissions/detail.html`
- RSS: `/rss.xml`; Sitemap: `/sitemap.xml`
- Form errors: Django form errors are rendered

## Notes
- Markdown sanitize: `apps/submissions/markdown.py` (bleach + markdown)
- Clean URL: `/p/{slug}` (slug = `slugify(title)` + 6‑char id)
- Search and tag filters are tracked for v1.1

## Shared Templates (Partials)
These templates are reused across pages to keep markup consistent:

- `templates/partials/header.html`: Header/nav
- `templates/partials/footer.html`: Footer and RSS
- `templates/partials/messages.html`: Django messages
- `templates/partials/tag_nav.html`: Tag navigation; expects `tag_items`, `active_tag`
- `templates/partials/items_list.html`: Generic list; items need `get_absolute_url`, `title`, `created_at`
- `templates/partials/pagination.html`: Pagination; expects `page_obj`, `prev_url`, `next_url`
- `templates/partials/robots_noindex_if_paginated.html`: Adds `noindex,follow` for page > 1

Example usage:
```
{% include 'partials/tag_nav.html' %}
{% include 'partials/items_list.html' with items=submissions empty_text='No items yet.' date_format='m/Y' %}
{# build prev_url/next_url variables: #}
{% include 'partials/pagination.html' %}
```
