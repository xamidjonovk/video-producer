"""Track quoted Higgsfield submissions inside one video job. Uses no network."""

import argparse
import json
import sqlite3
import sys
from contextlib import closing
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path


def amount(text):
    try:
        value = Decimal(text)
        if not value.is_finite() or value < 0 or value > 10**12:
            raise ValueError
        return int(value.to_integral_value(rounding=ROUND_CEILING))
    except (InvalidOperation, ValueError):
        raise argparse.ArgumentTypeError("Expected a non-negative credit amount up to 10^12.")


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("job", type=Path)
    commands = cli.add_subparsers(dest="action", required=True)
    init = commands.add_parser("init")
    init.add_argument("--cap", type=int, required=True)
    init.add_argument("--spent", type=amount, default=0)
    init.add_argument("--reserve", type=amount, default=0)
    hold = commands.add_parser("hold")
    hold.add_argument("shot")
    hold.add_argument("quote", help="Unique provider quote reference for this exact request")
    hold.add_argument("total", type=amount, help="Full quoted cost including all variants")
    hold.add_argument("--retry", action="store_true")
    link = commands.add_parser("link")
    link.add_argument("quote")
    link.add_argument("jobs", nargs="+", help="All returned provider job IDs")
    finish = commands.add_parser("finish")
    finish.add_argument("quote")
    finish.add_argument("outcome", choices=("kept", "rejected", "failed"))
    finish.add_argument("charged", type=amount, help="Confirmed net charge")
    finish.add_argument("note", help="Chosen take ID, QA timestamp, or provider confirmation")
    refund = commands.add_parser("refund", help="Reconcile a provider-confirmed refund")
    refund.add_argument("quote")
    refund.add_argument("net_charge", type=amount, help="Total charge remaining after the refund")
    refund.add_argument("receipt", help="Provider billing confirmation")
    commands.add_parser("status")
    return cli


def balance(db):
    cap, spent, reserve = db.execute("SELECT cap, spent, reserve FROM budget").fetchone()
    held, charged = db.execute(
        "SELECT COALESCE(SUM(CASE WHEN charged IS NULL THEN total END), 0), "
        "COALESCE(SUM(charged), 0) FROM takes"
    ).fetchone()
    return dict(cap=cap, spent=spent + charged, held=held, reserve=reserve,
                available=cap - spent - charged - held - reserve)


def update(db, args):
    db.execute("BEGIN IMMEDIATE")
    if args.action == "init":
        if not 0 <= args.cap <= 10**12 or args.spent + args.reserve > args.cap:
            raise ValueError("Starting spend and reserve must fit the authorized whole-credit cap.")
        db.execute("CREATE TABLE IF NOT EXISTS budget (cap INTEGER, spent INTEGER, reserve INTEGER)")
        db.execute("CREATE TABLE IF NOT EXISTS takes (shot TEXT NOT NULL, quote TEXT PRIMARY KEY, "
                   "total INTEGER NOT NULL, jobs TEXT, outcome TEXT, charged INTEGER, note TEXT)")
        settings = (args.cap, args.spent, args.reserve)
        existing = db.execute("SELECT * FROM budget").fetchone()
        if existing and tuple(existing) != settings:
            raise ValueError("This job already has a budget. Reuse its ledger and cap.")
        if not existing:
            db.execute("INSERT INTO budget VALUES (?, ?, ?)", settings)
    elif args.action == "hold":
        if not args.shot.strip() or not args.quote.strip():
            raise ValueError("Supply a stable shot ID and an exact quote reference.")
        if db.execute("SELECT 1 FROM takes WHERE quote=?", (args.quote,)).fetchone():
            raise ValueError("This quote already has a receipt. Check status before any submission.")
        previous = db.execute("SELECT outcome FROM takes WHERE shot=? ORDER BY rowid DESC LIMIT 1",
                              (args.shot,)).fetchone()
        if previous and (previous[0] in (None, "kept") or not args.retry):
            raise ValueError("Reuse the existing receipt. Only a closed unsuccessful take can be retried.")
        if balance(db)["available"] < args.total:
            raise ValueError("Quote exceeds the available budget after outstanding holds and reserve.")
        db.execute("INSERT INTO takes (shot, quote, total) VALUES (?, ?, ?)", (args.shot, args.quote, args.total))
    elif args.action in ("link", "finish", "refund"):
        take = db.execute("SELECT * FROM takes WHERE quote=?", (args.quote,)).fetchone()
        if take is None:
            raise ValueError("Unknown quote. Check the job and its receipts.")
        if args.action == "refund":
            if take["charged"] is None or args.net_charge > take["charged"] or not args.receipt.strip():
                raise ValueError("Supply the confirmed lower net cost and a billing receipt for a closed take.")
            db.execute("CREATE TABLE IF NOT EXISTS refunds (receipt TEXT PRIMARY KEY, quote TEXT, "
                       "before_charge INTEGER, net_charge INTEGER)")
            previous = db.execute("SELECT quote, net_charge FROM refunds WHERE receipt=?", (args.receipt,)).fetchone()
            if previous and tuple(previous) != (args.quote, args.net_charge):
                raise ValueError("This refund receipt is already recorded with different billing details.")
            if not previous:
                db.execute("INSERT INTO refunds VALUES (?, ?, ?, ?)",
                           (args.receipt, args.quote, take["charged"], args.net_charge))
                db.execute("UPDATE takes SET charged=? WHERE quote=?", (args.net_charge, args.quote))
        elif args.action == "link":
            jobs = json.dumps(args.jobs)
            if take["jobs"] != jobs:
                if take["jobs"] or take["outcome"]:
                    raise ValueError("This receipt already has a different result.")
                db.execute("UPDATE takes SET jobs=? WHERE quote=?", (jobs, args.quote))
        else:
            if not args.note.strip() or (args.outcome != "failed" and not take["jobs"]):
                raise ValueError("Record provider job IDs for a completed take and a short QA or billing note.")
            values = (args.outcome, args.charged, args.note)
            if take["outcome"] and values != (take["outcome"], take["charged"], take["note"]):
                raise ValueError("This receipt was already closed with different evidence.")
            db.execute("UPDATE takes SET outcome=?, charged=?, note=? WHERE quote=?", (*values, args.quote))
    result = balance(db)
    if args.action == "status":
        result["takes"] = [dict(row) for row in db.execute("SELECT * FROM takes ORDER BY rowid")]
        for take in result["takes"]:
            take["jobs"] = json.loads(take["jobs"]) if take["jobs"] else []
    return result


def main():
    args = parser().parse_args()
    try:
        if not args.job.is_dir():
            raise ValueError("Supply the existing production job directory.")
        directory = args.job / ".video-producer"
        path = directory / "higgsfield.sqlite"
        if not path.resolve().is_relative_to(args.job.resolve()):
            raise ValueError("The ledger must stay inside the production job.")
        if args.action == "init":
            directory.mkdir(exist_ok=True)
        elif not path.is_file():
            raise ValueError("Initialize this job with its authorized credit cap first.")
        with closing(sqlite3.connect(path)) as db, db:
            db.row_factory = sqlite3.Row
            result = update(db, args)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, sqlite3.Error) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
