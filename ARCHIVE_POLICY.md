# OpenSmell — Archive Policy

**The Christman AI Project / Luma Cognify AI**  
**Effective:** 2026-07-17  
**Law:** We never erase the past. We never ship stubs, truncated bodies, or placeholders as finished work.

---

## 1. Never erase the past

When code, docs, scripts, or claims are **moved, corrected, renamed, or retired**:

1. Capture the **full previous file body** (not a summary, not a diff alone).  
2. Package into a **zip** with a dated name.  
3. Deposit that zip into the **storage GitHub repo**:  
   - Remote: `https://github.com/EverettNC/storage`  
   - Path convention: `OpenSmell/archives/<ArchiveID>/` and matching `.zip`  
4. Keep a copy under this project’s `archives/` directory when practical.  
5. Write a **MANIFEST.md** inside the archive that states why the change happened and lists every path.

Git history is necessary but **not sufficient**. Storage zip is the durable, browseable record for corrections that rewrite claim language or remove outdated material from the working tree.

---

## 2. Never use stubs, truncated files, or placeholders

| Forbidden | Required instead |
|-----------|------------------|
| `TODO: implement later` as the body of a shipped function | Real implementation or do not add the file |
| `*(next)* file will be written` in docs | Full document with complete sections |
| `TBD`, `lorem ipsum`, `...` standing in for metrics | Measured number or explicit “not measured yet” sentence with no fake figure |
| Truncated exports presented as full reports | Complete report or labeled partial with exact cycle counts |
| Empty `pass` / `NotImplementedError` in production paths | Working code or omit the path |

**Claim lock and simulation numbers still apply:** “not measured yet” is honest; inventing a number is a lie.

---

## 3. Archive naming

```
OpenSmell_<reason>_<YYYYMMDD>.zip
```

Examples:

- `OpenSmell_claimlock_precorrection_20260717.zip`  
- `OpenSmell_license_alignment_<date>.zip`  

Inside each zip:

```
git_HEAD_before_<change>/   # full pre-change file bodies when from git
existing_bak_files/         # any .bak preserved
post_<change>_snapshot/     # state after correction (optional but preferred)
meta/MANIFEST.md
meta/FILE_LIST.txt
meta/SHA256SUMS.txt
```

---

## 4. Storage repo procedure

```bash
# After building STAGE and ZIP under /tmp or OpenSmell/archives:
STORAGE="${HOME}/storage"   # clone of EverettNC/storage
mkdir -p "$STORAGE/OpenSmell/archives"
cp -p archives/OpenSmell_*.zip "$STORAGE/OpenSmell/archives/"
# Optional: unpacked tree for browsing
# Then commit on storage repo with a clear message and push.
```

Commit message pattern:

```
OpenSmell archive: <reason> <YYYY-MM-DD>

Preserves full pre-change file bodies. No past erased.
```

---

## 5. Archives already deposited

| Archive ID | Zip | Why |
|------------|-----|-----|
| `20260717_claimlock_precorrection` | `OpenSmell/archives/OpenSmell_claimlock_precorrection_20260717.zip` in EverettNC/storage, branch `opensmell-archives` | Claim-lock removed inflated 2,401/2400+ counts; prior bodies preserved |
| `20261011_flagship_correction` | `OpenSmell/archives/OpenSmell_flagship_correction_20261011.zip` in EverettNC/storage, branch `opensmell-archives` | Cycle double-count fixed (23,686 reported, 11,843 real); ground-truth logging finished; mixed-schema log removed; labeled accuracy settled at 87.2% exact / 89.1% group |

Local mirrors: `OpenSmell/archives/OpenSmell_claimlock_precorrection_20260717.zip`, `OpenSmell/archives/OpenSmell_flagship_correction_20261011.zip`

Storage note (2026-10-11): `main` on EverettNC/storage is locked (branch lock, enforced for admins). Both archives were deposited on 2026-10-11 to branch `opensmell-archives` (commit dcf1b20), each as the zip plus an unpacked folder `OpenSmell/archives/<ArchiveID>/`. The 2026-07-17 archive had been listed here as deposited but was not in the storage repo before that date.

---

## 6. Relationship to CLAIM_LOCK

`CLAIM_LOCK.md` governs **what may be said publicly**.  
`ARCHIVE_POLICY.md` governs **how the past is kept when the working tree is corrected**.

Both bind every session.

---

© 2025–2026 The Christman AI Project. All Rights Reserved.
