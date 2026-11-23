# Talent Signal update bundle

This bundle changes Talent Signal from a static mockup into a public-source signal board.

## What changes

- The date in the page header is generated in the visitor's local timezone each time the page opens.
- Latest public articles, topic counts and vendor mentions load from `data/updates.json`.
- A global events panel shows upcoming conferences, verified organizer details, and recaps from recent major events. Event details refresh from organizer pages when those pages expose structured event data; linked curated dates remain as fallback.
- The event panel also surfaces new event-related stories found in monitored feeds.
- GitHub Actions is configured to rebuild that JSON snapshot every six hours, and on manual dispatch.
- The dashboard no longer displays invented customer ratings, implementation estimates, adoption scores, or stale event dates.
- The vendor list is a watchlist of public mentions, not a comparative performance ranking.

## Files to add/update in the repository

Copy `index.html` to the repository root, and add `.github/workflows/refresh-sources.yml`, `scripts/refresh_sources.py`, `data/updates.json`, and `data/events.json` in the matching paths.

## GitHub Actions setting

The repository's Actions settings must allow workflows to write repository contents. If Actions are restricted to read-only tokens, the collector cannot commit an updated snapshot.

The workflow refreshes the feed every six hours. It does not update the static Pages site build; the page reads the latest JSON snapshot directly from the repository's raw file URL with a cache-busting query parameter.

## Current public sources

- HR Dive public RSS feed
- HR Executive public RSS feed
- iCIMS Hiring Insights public blog feed

The dashboard shows which sources reported successfully. Coverage is intentionally limited at first; feed failures are surfaced instead of hidden. Vendor mention matching is simple keyword matching and should be expanded as the source list grows.

No paid analyst scores or customer-rating feeds are included.
