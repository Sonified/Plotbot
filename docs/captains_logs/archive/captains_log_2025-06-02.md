# Captain's Log - 2025-06-02

## Changes and Updates

- **Integrated HAM data with Data Cubby:**
    - Modified relevant files to ensure HAM data products (`ham_class`, `ham` instance) are properly registered and managed by the `data_cubby` system.
    - Ensured HAM data can be loaded, cached, and retrieved via `data_cubby.grab('ham')`.
    - Updated `plotbot/__init__.py` to include `ham` and `ham_class` in exports and `data_cubby` registration.
- **Removed Critical Debug Functionality:**
    - Modified `plotbot/print_manager.py` to remove special handling for "CRITICAL DEBUG" and "DBG-CRITICAL" messages within the `debug` method. All debug messages are now treated uniformly and controlled by the `debug_mode` flag.
    - Removed the `level_critical` attribute from `print_manager_class`.
    - Updated `plotbot/plotbot_main.py` and `plotbot/plotbot_main.py.backup` to remove "CRITICAL DEBUG - " and "DBG-CRITICAL: " prefixes from all `print_manager.debug` calls.
    - Confirmed that `README.md` no longer contains documentation for critical debug messages.

This change simplifies the debugging output and ensures that all debug messages are consistently managed by the `print_manager`'s `debug_mode`.

**Commit Message:** v2.55 Feature: Integrated HAM data with Data Cubby and removed critical debug 