# Captain's Log - 2025-05-01

---

*   **Bug Fix: SPDF Data Download Completeness:** Resolved an issue where the SPDF download mechanism (used in `spdf` and `dynamic` modes) would incorrectly stop if *any* local file matching the data type was found within the requested time range, even if the local files didn't cover the *entire* range. This could lead to incomplete datasets being loaded. The fix involved removing the initial local-only check (`no_update=True`) in `plotbot/data_download_pyspedas.py`, ensuring that the function now always proceeds to the `no_update=False` check, which correctly assesses local files against the required range and downloads missing data or newer versions from the server as needed. 

*   **Enhancement: Case-Insensitive Server Config:** Modified `plotbot/get_data.py` to handle the `config.data_server` setting (`'spdf'`, `'berkeley'`, `'dynamic'`) in a case-insensitive manner. It now converts the value to lowercase before checking it, preventing potential issues caused by inconsistent capitalization in the configuration. 