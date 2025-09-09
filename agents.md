# Agents Guidelines

- After every implementation, the code must be tested.
- Prefer automated checks (linters, tests) and run the app for sanity.
- Keep changes minimal, focused, and reversible.

## UI Text and Fonts

- Use ASCII-only characters in all user-facing templates and copy. Avoid smart quotes, en/em dashes, typographic bullets, and non-ASCII punctuation. Use a plain hyphen `-` as a separator when needed.

## Forms

- Wrap every individual form field block with a `div.field` containing label, optional help text, the input, and errors.
- Wrap submit buttons at the bottom of forms in a `div.actions`.
- Prefer plain text help messages (strip HTML lists from built-in help texts in templates where needed).
