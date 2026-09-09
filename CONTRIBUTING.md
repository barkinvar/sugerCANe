# Editing and generated-file policy

[Overview](README.md) · [Revision map](REVISIONS.md) · [Tools](current/TOOLS.md)

Work in `current/`, the maintained Rev H project. Native KiCad schematic/PCB are authoritative; the explicit circuit model, BOM, firmware identity and instructions must agree. Do not rebuild a routed board from historical placement experiments. Prior released ZIPs under `archive/` are immutable; make a new revision when electrical behavior or compatibility changes.

Keep native CAD/local libraries, original sources, licenses and pinned manifests, BOMs, Gerbers/drills, final STEP/PDF/HTML/PNG exports, programming images, engineering reports and release/order ZIPs in Git. These deliverables let reviewers and assemblers use the project without recreating its toolchain.

Ignore environments, downloaded dependencies, compiler objects, executable test runners, caches and scratch captures. The archived source tree and Git history preserve removed old revisions and experiments. Do not use `git clean` or rewrite history for routine cleanup. If a tracked file becomes ignored, inspect it before removing it from tracking; retain useful local work.

For electrical/layout changes, run native ERC/DRC, model parity, circuit constraints and independent manufacturing checks. Refresh affected firmware tests, BOM, factory packet and release archive. Review generated documents and board renders visually; a test result does not establish physical qualification. Update the documented prototype gates when behavior changes.

Before committing, run `git diff --check`, check local links and archive hashes, and verify the extracted current release. Push reviewed commits to the configured remote. Preserve the byte identity of every historical release package.
