# Naming Conventions

Use short, stable, descriptive sprite names.

## Recommended pattern

`feature_subject_variant`

Examples:

- `plot_tab_list`
- `plot_tab_messages`
- `plot_card_empty`
- `plot_card_occupied`
- `plot_button_apply_visit`
- `plot_avatar_ring`

## Sorting expectation

The bundled script sorts from top to bottom, then left to right.

Prepare names files in that same order.

## Unity notes

- Prefer ASCII filenames unless the project explicitly wants localized filenames.
- Avoid spaces.
- Avoid version words inside asset names unless you truly need parallel variants.
- Keep filenames stable after references are wired in Prefabs.
