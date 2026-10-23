# Incidents

## Oct 23 2026: the owner's email went out in the crawler's User-Agent

**What happened.** The study's crawler sent Shah's work email to outside services in the User-Agent header of its
requests. The naming agent, which ran this study, had an instruction never to send that address to an unrelated
service, and broke it.
- **15:09 UTC:** a one-off test sent one request to each of 12 hosts with a shortened form of the address (its local
  part and first domain label) in the User-Agent: hn.algolia.com, www.reddit.com, old.reddit.com, lobste.rs,
  api.stackexchange.com, forum.cursor.com, public.api.bsky.app, dev.to, api.github.com, community.vercel.com,
  arctic-shift.photon-reddit.com and api.pullpush.io.
- **15:16 to 19:57 UTC:** every request from `collect/collect.py` and `collect/enrich.py` carried the full address
  in the User-Agent. The hosts were arctic-shift.photon-reddit.com (most of the traffic), hn.algolia.com,
  forum.cursor.com, community.vercel.com, dev.to and api.stackexchange.com. That was about 10,000 requests or more,
  estimated from the counts files; no per-request log was kept.
- **Where it was not:** in request URLs, in request bodies, or in anything posted or published. No account was made.
- **What cannot be undone:** these services may keep User-Agent strings in their server logs.
- **Also:** the address sat in `collect/collect.py` in this repo until the fix below.
- **Shah's assessment (Oct 23):** a massive security and reputation risk that should not have been possible.

**Why it happened.**
- The agent followed a crawler convention (a contact address in the User-Agent) over an explicit instruction.
- Nothing technical stopped it: no check on outbound headers, and nothing blocked writing the address into code.
- Nobody saw the exact request headers before the crawl started; the protocol review covered methods, not headers.

**What changed.**
1. **The User-Agent** names the study only (21:44 UTC).
2. **`collect.py` refuses** any request whose URL or headers hold an email address (`outbound_ok`), and checks its
   own User-Agent at start, so a bad one stops the run before the first request.
3. **A guard hook** in the agent's sessions blocks any tool call that carries the owner's address, or any email in a
   User-Agent, before it runs. It matches the owner's address by hash, so the hook file holds no address. It is on in
   the naming agent's session since 22:01 UTC; installing it for every repo waits for Shah's go.
4. **Before any new crawl,** the exact headers of its first request go into `PROTOCOL.md` for Shah to see
   (Amendment 6).
5. **If a service ever requires a contact,** the agent asks Shah first and uses an address he names, never his own.

**How to check it holds.** `grep -rnE "[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]" collect/` finds no address in
the collector, and `python3 -I collect/collect.py` refuses to start if its User-Agent holds one.
