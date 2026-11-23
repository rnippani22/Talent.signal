# Talent Signal update bundle

This bundle changes Talent Signal from a static mockup into a public-source signal board.

## What changes

- The date in the page header is generated in the visitor's local timezone each time the page opens.
- Latest public articles, topic counts, topic-filtered competitive evidence and named vendor mentions load from `data/updates.json`.
- Vendor evidence is a source-linked watchlist, not a ranking; the radar does not invent comparable CSAT or implementation scores.
- A global events panel shows upcoming conferences, verified organizer details, and recaps from recent major events. Event details refresh from organizer pages when those pages expose structured event data; linked curated dates remain as fallback.
- The event panel also surfaces new event-related stories found in monitored feeds.
- GitHub Actions is configured to rebuild that JSON snapshot every six hours, and on manual dispatch.
- The dashboard no longer displays invented customer ratings, implementation estimates, adoption scores, or stale event dates.
- The vendor list is a watchlist of public mentions, not a comparative performance ranking.

## Files to add/update in the repository

Copy `index.html` to the repository root, and add `.github/workflows/refresh-sources.yml`, `scripts/refresh_sources.py`, `data/updates.json`, and `data/events.json` in the matching paths.

## GitHub Actions setting

The repository's Actions settings must allow workflows to write repository contents. If Actions are restricted to read-only tokens, the collector cannot commit an updated snapshot.

The workflow refreshes public feeds and event sources every six hours, commits the latest JSON snapshots, and GitHub Pages republishes the site from the updated repository. The page reads `data/updates.json` and `data/events.json` from the deployed site with cache-busting requests.

## Current public sources

- HR Dive public RSS feed
- HR Tech Feed public RSS feed

The dashboard shows how many public sources reported successfully. Coverage is limited to free sources; failures are surfaced. Topic and vendor matching is keyword-based, so verify important claims against the linked original source.

No paid analyst scores or customer-rating feeds are included.
