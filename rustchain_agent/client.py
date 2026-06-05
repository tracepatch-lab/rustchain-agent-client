from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class AgentClientError(RuntimeError):
    """Base SDK error."""


class AgentHttpError(AgentClientError):
    """Raised when the RustChain node returns a non-2xx HTTP response."""

    def __init__(self, status: int, message: str, body: Any = None):
        super().__init__(f"RustChain API returned HTTP {status}: {message}")
        self.status = status
        self.body = body


@dataclass(frozen=True)
class AgentClient:
    """Small stdlib client for the RIP-302 Agent Economy API."""

    base_url: str = "https://50.28.86.131"
    timeout: float = 20.0
    verify_tls: bool = False

    def _url(self, path: str, query: dict[str, Any] | None = None) -> str:
        base = self.base_url.rstrip("/")
        if not path.startswith("/"):
            path = f"/{path}"
        url = f"{base}{path}"
        if query:
            clean = {k: v for k, v in query.items() if v is not None}
            if clean:
                url = f"{url}?{urlencode(clean, doseq=True)}"
        return url

    def _context(self) -> ssl.SSLContext | None:
        if self.verify_tls:
            return None
        return ssl._create_unverified_context()

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None, query: dict[str, Any] | None = None) -> Any:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = Request(self._url(path, query), data=body, headers=headers, method=method.upper())
        try:
            with urlopen(req, timeout=self.timeout, context=self._context()) as res:
                raw = res.read().decode("utf-8")
                return json.loads(raw) if raw else None
        except HTTPError as err:
            raw = err.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            message = parsed.get("error") if isinstance(parsed, dict) and parsed.get("error") else raw[:300]
            raise AgentHttpError(err.code, message or err.reason, parsed) from err
        except URLError as err:
            raise AgentClientError(f"Could not reach RustChain API: {err.reason}") from err
        except json.JSONDecodeError as err:
            raise AgentClientError(f"RustChain API returned invalid JSON: {err}") from err

    def list_jobs(self, *, status: str | None = None, category: str | None = None, limit: int = 50, offset: int = 0) -> Any:
        return self.request("GET", "/agent/jobs", query={"status": status, "category": category, "limit": limit, "offset": offset})

    def get_job(self, job_id: str) -> Any:
        return self.request("GET", f"/agent/jobs/{job_id}")

    def post_job(self, poster_wallet: str, title: str, description: str, category: str, reward_rtc: float, tags: list[str] | None = None, ttl_hours: int | None = None) -> Any:
        return self.request("POST", "/agent/jobs", {
            "poster_wallet": poster_wallet,
            "title": title,
            "description": description,
            "category": category,
            "reward_rtc": reward_rtc,
            "tags": tags or [],
            **({"ttl_hours": ttl_hours} if ttl_hours is not None else {}),
        })

    def claim_job(self, job_id: str, worker_wallet: str) -> Any:
        return self.request("POST", f"/agent/jobs/{job_id}/claim", {"worker_wallet": worker_wallet})

    def deliver_job(self, job_id: str, worker_wallet: str, deliverable_url: str, result_summary: str) -> Any:
        return self.request("POST", f"/agent/jobs/{job_id}/deliver", {
            "worker_wallet": worker_wallet,
            "deliverable_url": deliverable_url,
            "result_summary": result_summary,
        })

    def accept_delivery(self, job_id: str, poster_wallet: str, note: str | None = None) -> Any:
        payload = {"poster_wallet": poster_wallet}
        if note:
            payload["note"] = note
        return self.request("POST", f"/agent/jobs/{job_id}/accept", payload)

    def dispute_delivery(self, job_id: str, poster_wallet: str, reason: str) -> Any:
        return self.request("POST", f"/agent/jobs/{job_id}/dispute", {"poster_wallet": poster_wallet, "reason": reason})

    def cancel_job(self, job_id: str, poster_wallet: str, reason: str | None = None) -> Any:
        payload = {"poster_wallet": poster_wallet}
        if reason:
            payload["reason"] = reason
        return self.request("POST", f"/agent/jobs/{job_id}/cancel", payload)

    def reputation(self, wallet: str) -> Any:
        return self.request("GET", f"/agent/reputation/{wallet}")

    def stats(self) -> Any:
        return self.request("GET", "/agent/stats")
