"""Configuration for Instagram viral video research.

Two research tracks:
  1. VIRAL_QUERIES  — what's going viral in the account's niches (format/hook study)
  2. HOT_TAKE_QUERIES — trending news & culture topics to react to with an
     opinionated "angry breakdown" commentary style
"""

# ---------------------------------------------------------------------------
# Account niches — the lanes this account lives in.
# Personal brand stays, but the account is re-centering around an
# entertaining, opinion-driven lifestyle voice: luxury villas, dating,
# Ibiza, travel, and nightlife.
# ---------------------------------------------------------------------------
NICHES = [
    "personal branding",
    "content creator business",
    "luxury villas and real estate",
    "Bali villa lifestyle",
    "modern dating and relationships",
    "Ibiza party and club scene",
    "luxury and boutique travel",
    "nightlife and festival culture",
    "digital nomad and expat life",
]

# ---------------------------------------------------------------------------
# Track 1: viral content research — study hooks, formats, pacing.
# ---------------------------------------------------------------------------
VIRAL_QUERIES = [
    "viral Instagram Reels personal brand 2025",
    "viral Instagram Reels luxury villa tour",
    "viral Instagram Reels Bali villa real estate",
    "viral Instagram Reels modern dating hot takes",
    "viral Instagram Reels Ibiza nightlife",
    "trending Instagram Reels luxury travel",
    "viral Instagram Reels nightlife festival",
    "viral Instagram hooks opinion rant commentary",
    "viral Instagram Reels digital nomad lifestyle",
]

# ---------------------------------------------------------------------------
# Track 2: hot-take / commentary research — trending topics in the news and
# in each niche that lend themselves to a strong, entertaining opinion take
# ("angry breakdown" / rant style). These surface *what to talk about*, not
# *how it's formatted*.
# ---------------------------------------------------------------------------
HOT_TAKE_QUERIES = [
    "trending controversy modern dating apps this week",
    "viral debate relationships dating discourse news",
    "Ibiza news controversy prices crackdown this week",
    "luxury travel controversy tourism backlash news",
    "nightlife club scene controversy news trending",
    "digital nomad expat backlash controversy news",
    "luxury real estate villa market controversy news",
    "trending internet culture debate hot take this week",
]

# Angles that reliably make commentary content entertaining and shareable.
HOT_TAKE_ANGLES = [
    "the thing everyone's doing wrong",
    "unpopular opinion / contrarian take",
    "calling out a trend or scam",
    "insider truth outsiders don't see",
    "ranking / tier list with strong opinions",
    "'we need to talk about...' callout",
]

ANALYSIS_DIMENSIONS = [
    "hook",
    "content_format",
    "niche",
    "engagement_drivers",
    "video_length",
    "caption_style",
    "trending_audio_or_text",
    "call_to_action",
    "commentary_angle",
]

REPORT_OUTPUT_DIR = "reports"

# Backwards-compat aliases (older report runs referenced these names).
PERSONAL_BRAND_NICHES = NICHES
RESEARCH_QUERIES = VIRAL_QUERIES
