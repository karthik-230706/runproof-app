# RunProof Combined — Merge Notes

This zip combines all four uploaded projects:

- `RunProof_FullStack_Pro.zip`
- `RunProof_Ultimate_FullStack.zip`
- `RunProof_Ultimate_v3_Fully_Wired.zip`
- `RunProof_Ultimate_v4_Premium_Dashboard.zip`

## How they were combined

**The three "Ultimate" versions are one evolving codebase.** File-by-file comparison
confirmed `Ultimate_v4` is a strict superset of `v3`, which is a strict superset of
the original `Ultimate_FullStack` — same architecture, same file layout, each version
just adding more. So **`Ultimate_v4` (the newest, most complete one) is used as the
main project**, at the root of this zip. Nothing from v2/v3 was lost — there was
nothing in them that v4 didn't already have.

**`FullStack_Pro` is a genuinely different implementation, not an earlier draft of
the same one.** It has its own separate backend (`auth.py`, `otp.py`, `database.py`,
`storage.py`), its own separate core engine (`engine.py`, `executor.py`, `evidence.py`,
`sbom.py`, `report.py` — files that don't exist in the Ultimate lineage at all), and
even the modules with matching names (e.g. `verifier.py`, `detector.py`) contain
different code with different function signatures — not the same functions rewritten.

Merging those files directly into `Ultimate_v4`'s folders by name would have silently
overwritten files in both directions and broken both apps (mismatched imports,
missing functions). So instead, **`FullStack_Pro` is preserved completely intact**
in its own subfolder:

```
RunProof_Combined/
├── (Ultimate_v4 — the main app, at the root: backend/, frontend/, run.py, etc.)
└── legacy_fullstack_pro/
    └── (FullStack_Pro — fully intact, runnable as its own separate project)
```

## How to run each one

**Main app (Ultimate_v4):**
```
cd RunProof_Combined
pip install -r requirements.txt
python run.py
```

**Legacy app (FullStack_Pro), as its own independent project:**
```
cd RunProof_Combined/legacy_fullstack_pro
pip install -r requirements.txt
python run.py
```

They are independent Flask apps and use different ports/config by default — don't
run both at once unless you've set different `RUNPROOF_PORT` values in each `.env`.
