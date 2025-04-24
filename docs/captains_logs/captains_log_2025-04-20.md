# Captain's Log - Stardate 2025_04_20

**Session Summary:**

Today's session focused heavily on understanding and documenting the data acquisition and caching mechanisms within Plotbot, particularly the distinction between standard and custom variables.

**Key Activities & Findings:**

1. **ASCII Diagram Refinement:** Reviewed and cleaned up the ASCII flowchart in `README.md` depicting the data acquisition pipeline (`get_data` -> `data_tracker` -> `data_download` -> `data_import` -> class update).
2. **Caching Investigation:** Conducted a deep dive into how data is cached and when calculations occur.
   * Confirmed that **standard variables** (e.g., `mag_rtn_4sa`) store their **calculated results** within the main class instance. This instance is cached in `data_cubby`.
   * Recalculation for standard variables is triggered only when `data_tracker` indicates a need to **import new raw data** for the requested time range. Otherwise, the previously calculated results stored in the cached instance are reused.
   * Confirmed that **custom variables** use a distinct mechanism involving `data_tracker.is_calculation_needed` and `data_tracker.update_calculated_range` to explicitly track and manage the caching of their **calculated results** based on their specific variable name and time range.
3. **README Updates:** Significantly updated the "Technical Notes For Developers" section in `README.md` to accurately reflect these findings, including detailed explanations of both standard and custom variable caching logic.
4. **File Cleanup:** Deleted the apparently outdated `docs/refactoring_history/` directory and its contents (`README.md`, `derived_to_custom_refactoring.py`).
5. **Log Initiation:** Created this `docs/captains_logs/` directory to begin logging our development sessions.

**Outcome:** Achieved a much clearer understanding and documentation of Plotbot's current caching strategy. Ready for potential future refactoring work on caching mechanisms with accurate baseline knowledge.

---

**Push to GitHub:**

* Version Tag: `2025_04_20_v1.00`
* Commit Message: `Docs: Clarify caching, add logs`

---

**LOG CLOSED**
