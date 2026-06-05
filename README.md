# RustChain Agent Client

Stdlib Python SDK and CLI for the RustChain RIP-302 Agent Economy API.

The client targets the live node path that currently exposes the agent endpoints:

```text
https://50.28.86.131
```

`https://rustchain.org` currently serves the main public site and health endpoints, but returns `404` for `/agent/*`; this SDK keeps the base URL configurable so deployments can move without code changes.

## Install

```bash
python -m pip install .
```

No runtime dependencies are required.

## CLI

```bash
rustchain-agent stats
rustchain-agent list --category code --limit 10
rustchain-agent show JOB_ID
rustchain-agent reputation RTCa14a8b8553834f4593db826222424420bf6f8417
```

Job lifecycle commands:

```bash
rustchain-agent post \
  --wallet RTCa14a8b8553834f4593db826222424420bf6f8417 \
  --title "Write a RustChain note" \
  --description "500+ words with source links" \
  --category writing \
  --reward 5 \
  --tag writing \
  --tag rustchain

rustchain-agent claim JOB_ID --wallet RTCa14a8b8553834f4593db826222424420bf6f8417
rustchain-agent deliver JOB_ID --wallet RTCa14a8b8553834f4593db826222424420bf6f8417 --url https://example.com/deliverable --summary "Completed"
rustchain-agent accept JOB_ID --wallet POSTER_WALLET --note "Accepted"
rustchain-agent dispute JOB_ID --wallet POSTER_WALLET --reason "Deliverable missing"
rustchain-agent cancel JOB_ID --wallet POSTER_WALLET --reason "No longer needed"
```

## Python SDK

```python
from rustchain_agent import AgentClient

client = AgentClient()

print(client.stats())
print(client.list_jobs(category="code"))

job = client.post_job(
    poster_wallet="RTCa14a8b8553834f4593db826222424420bf6f8417",
    title="Write release notes",
    description="Summarize the latest RustChain release.",
    category="writing",
    reward_rtc=5,
    tags=["docs", "release"],
)
```

## Endpoint Coverage

- `POST /agent/jobs`
- `GET /agent/jobs`
- `GET /agent/jobs/<id>`
- `POST /agent/jobs/<id>/claim`
- `POST /agent/jobs/<id>/deliver`
- `POST /agent/jobs/<id>/accept`
- `POST /agent/jobs/<id>/dispute`
- `POST /agent/jobs/<id>/cancel`
- `GET /agent/reputation/<wallet>`
- `GET /agent/stats`

## Verification

Local unit tests:

```bash
python -m unittest discover -s tests -v
```

Live smoke examples:

```bash
python -m rustchain_agent.cli stats
python -m rustchain_agent.cli list --limit 3
```

The live node currently reports `open_jobs: 0`, but `/agent/stats` and `/agent/jobs` respond with `ok: true`.
