# listings/

One file per job listing, named `<company>-<role>.md` (kebab-case, e.g.
`example-corp-software-engineer.md`). Created by `/intake` — paste the
listing text (and any application questions) into chat and it writes the
file here.

Frontmatter: `company`, `role`, `url`, `date_added`. Body is the verbatim
paste, plus a `## Questions` section holding only the short-answer,
application-specific questions (contact fields, uploads, sponsorship /
EEO, yes-no / multiple-choice etc. are dropped at intake).

When `/process` generates output for a listing, the listing file moves to
`listings/completed/` (the folder is the status — no `status` field).
Output itself stays in `output/`, not here.

Everything in this folder is gitignored except this README and
`completed/.gitkeep` — listings are personal data, not template content.
