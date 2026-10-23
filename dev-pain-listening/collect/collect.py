"""Collect the candidate pool for the listening study (PROTOCOL.md sections 5 and 6).

Usage: python3 -I collect/collect.py <source>
  source: reddit_posts | reddit_comments | hn | hn_weekly | discourse | devto | so

Each source writes raw items to data/raw/<source>.jsonl and match counts to
data/raw/counts_<source>.jsonl. Finished request keys go to data/raw/_done_<source>.txt, so a
rerun resumes where it stopped. Stdlib only.
"""

import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
Q = json.loads((ROOT / "collect" / "queries.json").read_text())
SALT = (ROOT / "collect" / "salt.txt").read_text().strip()
UA = "pulp-listening-study/1.0 (research)"
CAP = 300
# No request may carry an email address (incident, Oct 23 2026: the owner's address went out in the User-Agent).
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)*")


def outbound_ok(url, headers):
    """Stop the run before sending a request whose URL or headers hold an email address."""
    for where, text in [("URL", urllib.parse.unquote(url))] + [(f"{k} header", v) for k, v in headers.items()]:
        if EMAIL_RE.search(text):
            raise SystemExit(f"refusing to send: an email address is in the {where}")


outbound_ok("https://example.invalid/", {"User-Agent": UA})  # a bad User-Agent stops the run at start

WINDOWS = [(w, int(datetime.fromisoformat(a).replace(tzinfo=timezone.utc).timestamp()),
            int(datetime.fromisoformat(b).replace(tzinfo=timezone.utc).timestamp()))
           for w, a, b in Q["windows"]]
START, END = WINDOWS[0][1], WINDOWS[-1][2]

_last = {}


def window_of(ts):
    for w, a, b in WINDOWS:
        if a <= ts < b:
            return w
    return None


def author_hash(name):
    if not name or name in ("[deleted]", "AutoModerator"):
        return None
    return hashlib.sha256((SALT + name.lower()).encode()).hexdigest()[:12]


def strip_html(s):
    s = re.sub(r"<(br|p|/p|li)[^>]*>", "\n", s or "")
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def get_json(url, gap=1.0, tries=6):
    host = urllib.parse.urlparse(url).netloc
    for i in range(tries):
        wait = gap - (time.time() - _last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()
        try:
            headers = {"User-Agent": UA, "Accept": "application/json"}
            outbound_ok(url, headers)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
            if isinstance(data, dict) and data.get("error") and data.get("data") is None:
                raise RuntimeError(data["error"])
            return data
        except Exception as e:  # network, 429, archive timeouts
            print(f"retry {i + 1} {url[:120]} {e}", file=sys.stderr)
            time.sleep(min(60, 2 ** (i + 1)))
    print(f"GAVE UP {url}", file=sys.stderr)
    return None


class Sink:
    def __init__(self, source):
        RAW.mkdir(parents=True, exist_ok=True)
        self.items = open(RAW / f"{source}.jsonl", "a")
        self.counts = open(RAW / f"counts_{source}.jsonl", "a")
        self.done_path = RAW / f"_done_{source}.txt"
        self.done = set(self.done_path.read_text().split("\n")) if self.done_path.exists() else set()
        self.done_f = open(self.done_path, "a")

    def item(self, rec):
        self.items.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def count(self, rec):
        self.counts.write(json.dumps(rec) + "\n")

    def mark(self, key):
        self.done_f.write(key + "\n")
        for f in (self.items, self.counts, self.done_f):
            f.flush()


def months(a, b):
    """Split [a, b) into chunks of about 30 days."""
    out, t = [], a
    while t < b:
        out.append((t, min(b, t + 30 * 86400)))
        t += 30 * 86400
    return out


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


ARCTIC = "https://arctic-shift.photon-reddit.com/api"
RECOUNT_KEYS = None  # weeks finished before Amendment 3; reddit_recount visits only these
COUNTS_ONLY = False  # set by reddit_recount: count text availability again for weeks crawled before Amendment 3


FAM_RE = {f: (re.compile(v["regex"], re.I), re.compile(v["pain_regex"], re.I) if v.get("pain_regex") else None,
              v.get("ai_required", False)) for f, v in Q["families"].items()}
AI_RE = re.compile(Q["ai_regex"], re.I)


def match_families(text, cluster):
    """The query families a text matches under the frozen regexes (PROTOCOL.md section 6).

    AI families need an AI term in the text, except in the AI cluster where the community supplies it.
    """
    out = []
    has_ai = cluster == "ai" or bool(AI_RE.search(text))
    for f, (topic, pain, ai_req) in FAM_RE.items():
        if topic.search(text) and (pain is None or pain.search(text)) and (not ai_req or has_ai):
            out.append(f)
    return out


def reddit_posts(s, only=None):
    """Every post in each community, week by week; matches are kept, totals are counted (Amendment 1).

    `only` limits the run to one cluster so clusters can run as parallel workers with their own files.
    """
    fields = "id,title,selftext,created_utc,score,num_comments,author,subreddit,link_flair_text,author_flair_text"
    subs_only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
    for cluster in ((only,) if only else ("dev", "learner", "ai")):
        for sub in Q["reddit"][cluster]:
            if subs_only and sub not in subs_only:
                continue
            t = START
            while t < END:
                wk_end = min(END, t + 7 * 86400)
                key = f"{sub}|{t}"
                if key in s.done or (RECOUNT_KEYS is not None and key not in RECOUNT_KEYS):
                    t = wk_end
                    continue
                total, fam_n, cursor, seen, failed = 0, {}, t, set(), False
                n_text, n_removed, fam_text, fam_title = 0, 0, {}, {}
                while True:
                    url = (f"{ARCTIC}/posts/search?subreddit={sub}&after={cursor}&before={wk_end}"
                           f"&limit=100&sort=asc&fields={fields}")
                    d = get_json(url, gap=1.5, tries=8)
                    if d is None:
                        failed = True
                        break
                    rows = [p for p in (d.get("data") or []) if p["id"] not in seen]
                    for p in rows:
                        seen.add(p["id"])
                        total += 1
                        text = (p.get("title") or "") + "\n" + (p.get("selftext") or "")
                        fams = match_families(text, cluster)
                        for f in fams:
                            fam_n[f] = fam_n.get(f, 0) + 1
                        body = (p.get("selftext") or "").strip()
                        if body in ("[removed]", "[deleted]"):
                            n_removed += 1
                        elif body:
                            n_text += 1
                            for f in fams:
                                fam_text[f] = fam_text.get(f, 0) + 1
                        for f in match_families(p.get("title") or "", cluster):
                            fam_title[f] = fam_title.get(f, 0) + 1
                        if fams and not COUNTS_ONLY:
                            s.item({"src": "reddit", "kind": "post", "id": "t3_" + p["id"],
                                    "community": p.get("subreddit") or sub, "cluster": cluster,
                                    "families": fams, "window": window_of(p["created_utc"]),
                                    "created_utc": p["created_utc"], "title": p.get("title") or "",
                                    "text": p.get("selftext") or "", "score": p.get("score"),
                                    "num_comments": p.get("num_comments"),
                                    "flair": p.get("link_flair_text"), "author_flair": p.get("author_flair_text"),
                                    "author_hash": author_hash(p.get("author")),
                                    "url": f"https://www.reddit.com/r/{p.get('subreddit') or sub}/comments/{p['id']}/"})
                    raw = d.get("data") or []
                    if len(raw) < 100:
                        break
                    nxt = max(p["created_utc"] for p in raw)
                    cursor = nxt if nxt > cursor else cursor + 1
                s.count({"src": "reddit_posts", "community": sub, "cluster": cluster, "week_start": iso(t)[:10],
                         "window": window_of(t), "total": total, "family_counts": fam_n, "failed": failed,
                         "n_text": n_text, "n_removed": n_removed, "family_counts_text": fam_text,
                         "family_counts_title": fam_title})
                if not failed:
                    s.mark(key)
                t = wk_end


def reddit_recount(s, only=None):
    """Recount weeks crawled before the text availability counts existed; writes counts, never items."""
    global COUNTS_ONLY, RECOUNT_KEYS
    COUNTS_ONLY = True
    snap = RAW / "_recount_keys.txt"
    if not snap.exists():  # frozen once: the weeks done under the old counts
        keys = set()
        for f in RAW.glob("_done_reddit_posts*.txt"):
            keys |= set(f.read_text().split())
        snap.write_text("\n".join(sorted(keys)))
    RECOUNT_KEYS = set(snap.read_text().split())
    reddit_posts(s, only)


def reddit_comments(s, only=None):
    """Comments by keyword in about 30 day chunks. `only` is one community, for a parallel lane.

    A chunk is marked done only when its request succeeded, so a failure is retried on the next run and
    never stands as a zero. Done keys are shared across lanes; chunks that gave up before this fix are
    read from the logs and retried.
    """
    fields = "id,body,created_utc,score,author,link_id,subreddit,author_flair_text"
    ai = set(Q["reddit"]["ai"])
    for f in RAW.glob("_done_reddit_comments*.txt"):
        s.done |= set(f.read_text().split("\n"))
    for f in RAW.glob("log_reddit_comments*.txt"):
        for m in re.finditer(r"GAVE UP \S*subreddit=([^&]+)&body=([^&]+)&after=(\d+)", f.read_text()):
            s.done.discard(f"{m.group(1)}|{urllib.parse.unquote(m.group(2))}|{m.group(3)}")
    for sub in Q["reddit"]["comment_subs"]:
        if only and sub != only:
            continue
        cluster = "ai" if sub in ai else ("learner" if sub in Q["reddit"]["learner"] else "dev")
        for kw in Q["reddit"]["comment_keywords"]:
            for w, a, b in WINDOWS:
                total = 0
                for ca, cb in months(a, b):
                    key = f"{sub}|{kw}|{ca}"
                    if key in s.done:
                        continue
                    url = (f"{ARCTIC}/comments/search?subreddit={sub}&body={urllib.parse.quote(kw)}"
                           f"&after={ca}&before={cb}&limit=100&fields={fields}")
                    d = get_json(url, gap=2.0, tries=8)
                    if d is None:
                        continue  # not marked: retried on the next run
                    rows = d.get("data") or []
                    for c in rows:
                        s.item({"src": "reddit", "kind": "comment", "id": "t1_" + c["id"],
                                "community": c.get("subreddit") or sub, "cluster": cluster,
                                "family": None, "kw": kw, "window": window_of(c["created_utc"]),
                                "created_utc": c["created_utc"], "title": "", "text": c.get("body") or "",
                                "score": c.get("score"), "num_comments": None, "parent_link": c.get("link_id"),
                                "author_flair": c.get("author_flair_text"),
                                "author_hash": author_hash(c.get("author")),
                                "url": f"https://www.reddit.com/r/{c.get('subreddit') or sub}/comments/{(c.get('link_id') or 't3_')[3:]}/_/{c['id']}/"})
                    total += len(rows)
                    s.count({"src": "reddit_comments", "community": sub, "kw": kw, "window": w,
                             "chunk_start": ca, "count": len(rows), "capped": len(rows) >= 100})
                    s.mark(key)


HN = "https://hn.algolia.com/api/v1"


def hn(s):
    for fam, spec in Q["families"].items():
        for kw in spec["keywords"]:
            for w, a, b in WINDOWS:
                for tag in ("story", "comment"):
                    key = f"{fam}|{kw}|{w}|{tag}"
                    if key in s.done:
                        continue
                    url = (f"{HN}/search?query={urllib.parse.quote(kw)}&tags={tag}&hitsPerPage={CAP}"
                           f"&numericFilters=created_at_i>={a},created_at_i<{b}")
                    d = get_json(url, gap=0.6) or {}
                    for h in d.get("hits", []):
                        txt = strip_html(h.get("comment_text") or h.get("story_text") or "")
                        s.item({"src": "hn", "kind": tag, "id": "hn_" + h["objectID"], "community": "hackernews",
                                "cluster": "hn", "family": fam, "kw": kw, "window": window_of(h["created_at_i"]),
                                "created_utc": h["created_at_i"], "title": h.get("title") or h.get("story_title") or "",
                                "text": txt, "score": h.get("points"), "num_comments": h.get("num_comments"),
                                "author_hash": author_hash(h.get("author")), "story_url": h.get("url"),
                                "url": f"https://news.ycombinator.com/item?id={h['objectID']}"})
                    s.count({"src": "hn", "family": fam, "kw": kw, "window": w, "tag": tag,
                             "count": d.get("nbHits"), "capped": False})
                    s.mark(key)


def hn_weekly(s):
    for kw in Q["hn_weekly_keywords"]:
        t = START
        while t < END:
            key = f"{kw}|{t}"
            if key not in s.done:
                url = (f"{HN}/search?query={urllib.parse.quote(kw)}&tags=(story,comment)&hitsPerPage=0"
                       f"&numericFilters=created_at_i>={t},created_at_i<{t + 7 * 86400}")
                d = get_json(url, gap=0.4) or {}
                s.count({"src": "hn_weekly", "kw": kw, "week_start": iso(t)[:10], "count": d.get("nbHits")})
                s.mark(key)
            t += 7 * 86400


def hn_weekly_listed(s):
    """Weekly counts from hits actually listed, because Algolia's nbHits is approximate (Amendment 2)."""
    for kw in Q["hn_weekly_keywords"]:
        t = START
        while t < END:
            key = f"{kw}|{t}"
            if key not in s.done:
                n, page, ok = 0, 0, True
                while True:
                    url = (f"{HN}/search_by_date?query={urllib.parse.quote(kw)}&tags=(story,comment)"
                           f"&hitsPerPage=1000&page={page}&numericFilters=created_at_i>={t},created_at_i<{t + 7 * 86400}")
                    d = get_json(url, gap=0.5)
                    if d is None:
                        ok = False
                        break
                    hits = d.get("hits") or []
                    n += len(hits)
                    page += 1
                    if len(hits) < 1000 or page >= (d.get("nbPages") or 1):
                        break
                s.count({"src": "hn_weekly_listed", "kw": kw, "week_start": iso(t)[:10], "count": n, "ok": ok})
                if ok:
                    s.mark(key)
            t += 7 * 86400


def discourse(s):
    for host, kws in Q["discourse"].items():
        for kw in kws:
            for w, a, b in WINDOWS:
                key = f"{host}|{kw}|{w}"
                if key in s.done:
                    continue
                n = 0
                for page in range(1, 7):
                    q = f"{kw} after:{iso(a)[:10]} before:{iso(b)[:10]}"
                    d = get_json(f"https://{host}/search.json?q={urllib.parse.quote(q)}&page={page}", gap=1.5) or {}
                    posts = d.get("posts") or []
                    topics = {t["id"]: t for t in d.get("topics") or []}
                    for p in posts:
                        ts = int(datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")).timestamp())
                        t = topics.get(p.get("topic_id"), {})
                        s.item({"src": "discourse", "kind": "post", "id": f"{host}_{p['id']}", "community": host,
                                "cluster": "forum", "family": None, "kw": kw, "window": window_of(ts),
                                "created_utc": ts, "title": t.get("title") or "", "text": p.get("blurb") or "",
                                "text_is_blurb": True, "post_id": p["id"], "post_number": p.get("post_number"),
                                "score": p.get("like_count"), "num_comments": t.get("posts_count"),
                                "author_hash": author_hash(p.get("username")),
                                "url": f"https://{host}/t/{t.get('slug', 'x')}/{p.get('topic_id')}/{p.get('post_number', 1)}"})
                    n += len(posts)
                    if not (d.get("grouped_search_result") or {}).get("more_full_page_results"):
                        break
                s.count({"src": "discourse", "community": host, "kw": kw, "window": w, "count": n,
                         "capped": n >= 300})
                s.mark(key)


def devto(s):
    for tag in Q["devto_tags"]:
        page = 1
        while True:
            key = f"{tag}|{page}"
            if key in s.done:
                page += 1
                continue
            d = get_json(f"https://dev.to/api/articles?tag={tag}&per_page=1000&page={page}", gap=1.0)
            if not d:
                break
            oldest = END
            for x in d:
                ts = int(datetime.fromisoformat(x["published_at"].replace("Z", "+00:00")).timestamp())
                oldest = min(oldest, ts)
                if not (START <= ts < END):
                    continue
                s.item({"src": "devto", "kind": "article", "id": f"devto_{x['id']}", "community": "dev.to",
                        "cluster": "devto", "family": None, "kw": tag, "window": window_of(ts), "created_utc": ts,
                        "title": x.get("title") or "", "text": x.get("description") or "", "text_is_blurb": True,
                        "tags": x.get("tag_list"), "score": x.get("positive_reactions_count"),
                        "num_comments": x.get("comments_count"),
                        "author_hash": author_hash((x.get("user") or {}).get("username")), "url": x.get("url")})
            s.mark(key)
            if len(d) < 1000 or oldest < START:
                break
            page += 1


def so(s):
    for tag in Q["stackoverflow"]["tags"]:
        for q in Q["stackoverflow"]["q"][:2]:
            for w, a, b in WINDOWS:
                key = f"{tag}|{q}|{w}"
                if key in s.done:
                    continue
                url = ("https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=votes"
                       f"&q={urllib.parse.quote(q)}&tagged={urllib.parse.quote(tag)}&fromdate={a}&todate={b}"
                       "&site=stackoverflow&pagesize=100&filter=withbody")
                d = get_json(url, gap=1.0) or {}
                for x in d.get("items", []):
                    s.item({"src": "stackoverflow", "kind": "question", "id": f"so_{x['question_id']}",
                            "community": "stackoverflow", "cluster": "so", "family": None, "kw": f"{tag}:{q}",
                            "window": window_of(x["creation_date"]), "created_utc": x["creation_date"],
                            "title": html.unescape(x.get("title") or ""), "text": strip_html(x.get("body")),
                            "tags": x.get("tags"), "score": x.get("score"), "num_comments": x.get("answer_count"),
                            "author_hash": author_hash(str((x.get("owner") or {}).get("user_id") or "")),
                            "url": x.get("link")})
                s.count({"src": "so", "tag": tag, "q": q, "window": w, "count": len(d.get("items", [])),
                         "capped": bool(d.get("has_more")), "quota_remaining": d.get("quota_remaining")})
                s.mark(key)
                if d.get("backoff"):
                    time.sleep(int(d["backoff"]) + 1)


if __name__ == "__main__":
    src = sys.argv[1]
    only = sys.argv[2] if len(sys.argv) > 2 else None
    if src == "reddit_comments" and only:
        globals()[src](Sink(f"{src}_{only}"), only)
    elif only:  # the dev worker keeps the original file names, so its finished weeks are not refetched
        name = src if only == "dev" else f"{src}_{only}"
        if len(sys.argv) > 4:  # a lane for some of a cluster's communities: `<cluster> <sub,sub> <lane>`
            name = f"{name}_{sys.argv[4]}"
        globals()[src](Sink(name), only)
    else:
        globals()[src](Sink(src))
    print("DONE", src)
