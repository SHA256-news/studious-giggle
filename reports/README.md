# AI Analysis Reports

> **Note:** Generated reports are now written to `docs/reports/` so they can be picked up by the GitHub Pages workflow. This directory only contains legacy documentation about the reporting feature.

## Report Structure

Each generated report saved under `docs/reports/` follows the naming convention `YYYYMMDD_HHMMSS_title_slug.md` and includes:

- YAML front matter describing the article metadata (title, permalink, source link, AI model).
- A Markdown body with the analysis summary, supporting sections, and generation notice.

Reports are automatically created when the bot processes new articles or when `generate_reports.py` is run as part of the publishing workflow.