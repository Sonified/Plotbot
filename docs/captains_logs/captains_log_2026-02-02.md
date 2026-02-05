# Captain's Log - 2026-02-02

## v3.80 Maintenance: Zenodo release prep - repo cleanup

### Summary
Massive repository cleanup in preparation for v1.0 Zenodo release for ApJ paper.

### Results
- **Files**: 751 → 362 tracked files (52% reduction)
- **Size**: 171 MB → ~25 MB tracked content (85% reduction)

### What was cleaned
- 175 CDF metadata cache files (runtime-generated, now gitignored)
- 5 timing report CSVs
- 34 archived captain's logs
- 26 docs/archive dev artifacts (mystery HTML debugging pages, old to-dos)
- 37 debug scripts (one-off diagnostics)
- 18 implementation plans (completed + aspirational)
- ~67 SCRIPT/OTHER test files → `tests/archive/`
- 7 test output PNGs
- Unused HAM JSON files and large example images
- 8 orphan tracked-but-deleted files
- Stale `run_tests.py` references removed from README.md and tests/__init__.py

### .gitignore additions
- `plotbot/cache/cdf_metadata/`
- `tests/timing_reports/`
- `docs/captains_logs/archive/`
- `docs/archive/`
- `tests/debug_scripts/`
- `docs/implementation_plans/`

### Verification
- `pytest tests/test_stardust.py::test_stardust_audifier_initialization` passed
- All test infrastructure intact (test_pilot.py confirmed active, 15+ importers)
