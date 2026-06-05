from __future__ import annotations

import argparse
import json
import sys

from .client import AgentClient, AgentClientError


def print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rustchain-agent", description="RustChain RIP-302 Agent Economy CLI")
    parser.add_argument("--base-url", default="https://50.28.86.131", help="RustChain API base URL")
    parser.add_argument("--verify-tls", action="store_true", help="Verify TLS certificates")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="List jobs")
    list_cmd.add_argument("--status")
    list_cmd.add_argument("--category")
    list_cmd.add_argument("--limit", type=int, default=50)
    list_cmd.add_argument("--offset", type=int, default=0)

    show_cmd = sub.add_parser("show", help="Show one job")
    show_cmd.add_argument("job_id")

    post_cmd = sub.add_parser("post", help="Post a job")
    post_cmd.add_argument("--wallet", required=True)
    post_cmd.add_argument("--title", required=True)
    post_cmd.add_argument("--description", required=True)
    post_cmd.add_argument("--category", default="other")
    post_cmd.add_argument("--reward", type=float, required=True)
    post_cmd.add_argument("--tag", action="append", default=[])
    post_cmd.add_argument("--ttl-hours", type=int)

    claim_cmd = sub.add_parser("claim", help="Claim a job")
    claim_cmd.add_argument("job_id")
    claim_cmd.add_argument("--wallet", required=True)

    deliver_cmd = sub.add_parser("deliver", help="Deliver a claimed job")
    deliver_cmd.add_argument("job_id")
    deliver_cmd.add_argument("--wallet", required=True)
    deliver_cmd.add_argument("--url", required=True)
    deliver_cmd.add_argument("--summary", required=True)

    accept_cmd = sub.add_parser("accept", help="Accept a delivery")
    accept_cmd.add_argument("job_id")
    accept_cmd.add_argument("--wallet", required=True)
    accept_cmd.add_argument("--note")

    dispute_cmd = sub.add_parser("dispute", help="Dispute a delivery")
    dispute_cmd.add_argument("job_id")
    dispute_cmd.add_argument("--wallet", required=True)
    dispute_cmd.add_argument("--reason", required=True)

    cancel_cmd = sub.add_parser("cancel", help="Cancel a job")
    cancel_cmd.add_argument("job_id")
    cancel_cmd.add_argument("--wallet", required=True)
    cancel_cmd.add_argument("--reason")

    rep_cmd = sub.add_parser("reputation", help="Show wallet reputation")
    rep_cmd.add_argument("wallet")

    sub.add_parser("stats", help="Show marketplace stats")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = AgentClient(base_url=args.base_url, timeout=args.timeout, verify_tls=args.verify_tls)
    try:
        if args.command == "list":
            print_json(client.list_jobs(status=args.status, category=args.category, limit=args.limit, offset=args.offset))
        elif args.command == "show":
            print_json(client.get_job(args.job_id))
        elif args.command == "post":
            print_json(client.post_job(args.wallet, args.title, args.description, args.category, args.reward, args.tag, args.ttl_hours))
        elif args.command == "claim":
            print_json(client.claim_job(args.job_id, args.wallet))
        elif args.command == "deliver":
            print_json(client.deliver_job(args.job_id, args.wallet, args.url, args.summary))
        elif args.command == "accept":
            print_json(client.accept_delivery(args.job_id, args.wallet, args.note))
        elif args.command == "dispute":
            print_json(client.dispute_delivery(args.job_id, args.wallet, args.reason))
        elif args.command == "cancel":
            print_json(client.cancel_job(args.job_id, args.wallet, args.reason))
        elif args.command == "reputation":
            print_json(client.reputation(args.wallet))
        elif args.command == "stats":
            print_json(client.stats())
        return 0
    except AgentClientError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
