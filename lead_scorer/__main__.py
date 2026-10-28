import argparse
import csv
import json
import os
from collections import Counter

from .score import process


def write(path, rows):
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="Gate, dedupe and score a lead CSV against an ICP.")
    ap.add_argument("--input", default="sample_data/leads.csv")
    ap.add_argument("--icp", default="icp.json")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--min-score", type=int, default=60, help="score needed to count as 'send-ready'")
    a = ap.parse_args()

    leads = list(csv.DictReader(open(a.input, newline="")))
    icp = json.load(open(a.icp))
    clean, rejected = process(leads, icp)
    os.makedirs(a.out_dir, exist_ok=True)
    write(os.path.join(a.out_dir, "clean.csv"), clean)
    write(os.path.join(a.out_dir, "rejected.csv"), rejected)

    ready = [r for r in clean if r["score"] >= a.min_score]
    print(f"input leads:      {len(leads)}")
    print(f"rejected:         {len(rejected)}  {dict(Counter(r['reject_reason'] for r in rejected))}")
    print(f"passed the gate:  {len(clean)}")
    print(f"send-ready (>={a.min_score}): {len(ready)}")
    for r in clean[:5]:
        print(f"  {r['score']:>3}  {r['first_name']} {r['last_name']}, {r['title']} @ {r['company']}")


if __name__ == "__main__":
    main()
