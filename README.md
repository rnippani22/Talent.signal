# Talent Signal update bundle

This bundle changes Talent Signal from a static mockup into a public-source signal board.

## What changes

- The date in the page header is generated in the visitor's local timezone each time the page opens.
- Latest public articles, topic counts, topic-filtered competitive evidence and named vendor mentions load from `data/updates.json`.
- Vendor evidence is a source-linked watchlist, not a ranking; the radar does not invent comparable CSAT or implementation scores.
- A searchable market map lists 75 known recruiting and talent-acquisition providers, with current analyst report coverage and publicly disclosed vendor positions where available.
- Gartner and Everest public abstracts identify research scope and participating vendor counts, but most detailed vendor positions and scores require their full reports. Those are marked as unavailable rather than guessed.
- Analyst report links are checked during each six-hour refresh. Analyst ratings themselves change on analyst publication cycles, not every six hours; source-link checks do not imply a new rating.
- Radar stories are deduplicated by normalized headline and assigned one primary topic. Employee spotlights, generic week-in-review roundups, and other clearly non-market feed items are filtered out.
- A global events panel shows upcoming conferences, verified organizer details, and recaps from recent major events. Event details refresh from organizer pages when those pages expose structured event data; linked curated dates remain as fallback.
- The event panel also surfaces new event-related stories found in monitored feeds.
- GitHub Actions is configured to rebuild that JSON snapshot every six hours, and on manual dispatch.
- The dashboard does not calculate market share, rankings, customer ratings, implementation estimates, or adoption scores from news volume.
- The vendor directory is a broad market map assembled from named analyst research and additional known recruiting products; it is not a definitive registry of every global provider.

## Files to add/update in the repository

Copy `index.html` to the repository root. Keep `scripts/refresh_sources.py`, `scripts/market_map.js`, `data/updates.json`, `data/events.json`, and `data/analyst_assessments.json` in their matching paths.

## GitHub Actions setting

The repository's Actions settings must allow workflows to write repository contents. If Actions are restricted to read-only tokens, the collector cannot commit an updated snapshot.

The workflow refreshes public feeds, event sources, and analyst source-link checks every six hours, commits the latest JSON snapshots, and GitHub Pages republishes the site from the updated repository. The page reads all three JSON snapshots with cache-busting requests. Analyst link checks do not extract or guess new report ratings; public positions are updated when a new report cycle or attributable vendor announcement is confirmed.

## Current public sources

- HR Dive public RSS feed
- HR Tech Feed public RSS feed
- Public analyst report pages from Gartner, Fosway Group, and Everest Group (source-link status only; report positions are recorded only when publicly disclosed)

The dashboard shows how many public sources reported successfully. Coverage is limited to free sources; failures are surfaced. Topic and vendor matching is keyword-based, so verify important claims against the linked original source.

No paid analyst report content or customer-rating feeds are reproduced. The dashboard links to analyst sources and labels public vendor-reported positions separately.
