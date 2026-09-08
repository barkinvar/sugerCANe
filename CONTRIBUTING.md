# Repository and generated-file policy

[Overview](README.md) · [Revision map](REVISIONS.md) · [Tool setup](TOOLS.md)

## Choose a revision before editing

Root design directories belong to Rev A. Work in `rev_b/` for the compact DigiKey/hand-assembly design or `rev_b2/` for the China factory variant. Use `rev_c/` for the simplified 6–22 V Lite successor with protocol v2. Use `rev_d/` for the regulated 12 V / 5 V SC12 board and protocol v3. Use `rev_d2/` for the China SMT / user hand-solder variant of D, with removable voltage jumpers and the same protocol v3. Use `rev_e/` for software-selectable input bias, hardware 5 and protocol v4. The native schematic and routed PCB are authoritative; scripts and structured circuit data must agree with them. Do not regenerate a routed board from an old placement/router experiment.

Use the matching BOM, firmware and wiring documentation. Preserve prior revision packages. A change that affects circuit behavior, pads, pinout or procurement must update the corresponding model, native CAD, BOM and manufacturing evidence before a new package is released.

## What belongs in Git

Keep native KiCad sources and local libraries, original scripts and firmware sources, pinned dependency manifests/licenses, BOMs, Gerbers/drills, final STEP/PDF/HTML/PNG deliverables, flashable firmware ELF/HEX/BIN/MAP files, engineering reports and release/order ZIPs. These exports are intentionally tracked so a reviewer or assembler can use the project without recreating the full toolchain.

Ignore local virtual environments, caches, browser sessions, editor state, compiler objects and dependency files, downloaded host-test dependencies, executable test runners, routing scratch files and large raw simulation waveforms. Recreate dependencies from the pinned manifests and raw traces from the included SPICE decks. Final sampled waveforms and analysis reports remain available.

After changing `.gitignore`, inspect already-tracked matches:

```bash
git ls-files -ci --exclude-standard
```

Remove approved matches from **tracking only**, using `git rm --cached -- path/to/file`; keep working copies as needed. Never use `git clean` to do this. Ordinary commits preserve earlier versions in history. Raw simulation traces no longer require Git LFS in the current tree; older commits can still refer to LFS objects.

## Review and refresh

Run the revision's checks appropriate to the change. Electrical or layout changes need native ERC/DRC, model parity and exported manufacturing checks. Documentation changes need link and PDF review. A 3D-only correction needs model provenance, pin alignment and regenerated board renders/STEP; it does not establish physical fit.

Rebuild the affected handbook and release ZIP after updating maintained documentation. The root Rev A package maps `REV_A.md` to its internal `README.md`, so a standalone A archive has an A-specific overview. Repository-wide navigation uses explicit revision links; historical archives are left intact.

Check `git diff --check`, local documentation links and archive checksums before committing. Push the reviewed commit to the configured remote; do not rewrite prior revision history to remove files newly covered by `.gitignore`.
