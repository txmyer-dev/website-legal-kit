# website-legal-kit

Plain-language website policies for a small business site, plus a **lawyer review packet** the owner hands to their attorney to approve.

From one JSON file it writes:

- privacy policy, terms of use, accessibility statement
- SMS terms (for businesses that text customers), plus the consent line for web forms
- nondiscrimination notice (for healthcare practices)
- a site footer with the links
- `LAWYER-REVIEW.html`: a cover memo, questions for counsel, the assumptions made, every remaining fill-in, each document with review notes, and a sign-off line

**Not legal advice.** The kit gets a small business 90% of the way, so the attorney's hour goes on judgment instead of typing. Nothing goes live until the client's attorney signs the packet.

## Make one

```bash
python build.py examples/maple-street.json out/maple-street-legal
```

Standard library only. Any value that's missing shows as a yellow `[FILL: key]` in every page and is listed when the build finishes, so nothing ships half-filled without someone seeing it.

`examples/maple-street-legal/` is the output for a made-up chiropractic practice. Open `LAWYER-REVIEW.html` first.

## License

MIT
