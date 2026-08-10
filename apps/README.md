# 💾 The Overthinking Suite™

24 tiny y2k-styled web apps that answer the questions you've already asked your group chat.

Open `apps/index.html` in a browser. That's it — no build step, no server, no dependencies,
no network requests of any kind. Every score is computed in the page you're looking at.

## The apps

| # | App | What it actually does |
|---|-----|-----------------------|
| 01 | Does She Like Me or My Money? | Real Pearson correlation between per-date spend and post-date affection, plus a cheap-vs-expensive control group |
| 02 | Are We Dating or Am I Just Convenient? | Weights travel distance, initiation share, notice period, and daylight visibility |
| 03 | Could I Afford This Relationship? | 5-year compounding forecast with milestone years and a lifestyle-inflation term |
| 04 | Who's Settling? | Two-phase private answers on one device (partner A's are sealed in `localStorage`, revealed and erased when B answers) |
| 05 | Am I Hot — or Is This Just Vacation Lighting? | Canvas pixel analysis (luminance, saturation, warmth, laplacian sharpness, subject fill, clipping) run through 5 dating-app weightings, then subtracts the lighting |
| 06 | Is He Emotionally Unavailable or Just Not That Into Me? | Separates "can't with anyone" from "can, just not with you" |
| 07 | Would We Still Be Friends Without the Group Chat? | Simulates the chat vanishing |
| 08 | Which Friend Secretly Hates Me? | Multi-friend suspect board, ranked, with an anxiety-calibration adjustment |
| 09 | Am I the Broke Friend? | Restaurant-suggestion gap, Venmo timing, split-evenly tax in $/yr |
| 10 | Do My Parents Have a Favorite Child? | Ranks all siblings across money, praise, visits, photos, calls, blame |
| 11 | Should I Attend This Wedding? | Bond score vs. cash + PTO, with a reciprocity term |
| 12 | Is This Networking or Flirting? | Regex-scans pasted messages for flirt vs. business markers, renders the split |
| 13 | Will This Situationship Ruin My Life? | Risk model + projected recovery time in months |
| 14 | How Replaceable Am I at Work? | Bus factor, plus a "trapped index" for irreplaceable-but-unpromotable |
| 15 | Does My Boss Like Me — or Am I Just Useful? | Sponsorship vs. extraction, and the praise-to-action gap |
| 16 | Can I Quit Dramatically Yet? | Runway math, with drama scored as a separate, stricter budget |
| 17 | How Much Is This Meeting Stealing From My Life? | Room cost, fragmentation penalty, career months lost, converted into sleep/workouts/novels |
| 18 | Am I Successful or Just Good at LinkedIn? | Buzzword scan vs. income, happiness, and unstructured free time |
| 19 | Is Buying a House Actually My Dream — or My Parents'? | Intrinsic vs. inherited motivation, with an era-gap comparison |
| 20 | Can I Afford a Baby — or Just the Announcement Photos? | Itemized year one + 5-year total including career drag |
| 21 | When Should I Stop Supporting This Friend's Business? | Obligation load and how many launches you can still skip |
| 22 | Who Owes Whom Emotionally? | Weighted double-entry friendship ledger with a capacity adjustment |
| 23 | Is My Therapist Proud of Me? | XP bar, quest log, and an approval-seeking index that is the actual point |
| 24 | What's My Personal Nepo-Baby Score? | Splits outcomes across talent, luck, geography, parents, introductions |

## Structure

```
apps/
  index.html          the portal
  assets/y2k.css      the whole aesthetic
  assets/y2k.js       a ~250-line engine: declare a spec, get a website
  NN-name.html        one app each
```

Most apps are pure declarations — fields plus a `compute(v)` that returns a score, a verdict,
stat tiles, and "receipts". Four go beyond the engine with their own widgets: `01` and `08`/`10`
(editable data tables), `05` (canvas image analysis), `22` (a two-column ledger).

Adding a new one means copying an app file and rewriting the spec.

## Privacy

There is no server, no analytics, no account, and no external asset — not even a webfont
(the `@import` was removed precisely so these pages make zero network requests). Photos in
app 05 are read via `FileReader` into a `<canvas>` and never leave the page. The only thing
written anywhere is a fake visitor counter in `localStorage`, and app 04's sealed answers,
which are deleted the moment they're revealed.

## Disclaimer

These are toys. Every weight was made up on purpose, and each app will state something
confident about your life on the basis of nine sliders. That's the joke. What they're
genuinely useful for is turning a vague 2am feeling into a sentence specific enough to say
out loud — the number doesn't matter, the conversation after it does.

Not advice, therapy, diagnosis, or a financial product.
