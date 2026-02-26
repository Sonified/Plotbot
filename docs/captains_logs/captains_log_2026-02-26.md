# Captain's Log - 2026-02-26

## v3.84 Bugfix: pyspedas 2.x compatibility shim and y_limit style sync fix

### Changes

**1. pyspedas 2.x compatibility shim (4 locations)**
- pyspedas 2.x removed top-level mission shortcuts (`pyspedas.psp`, `pyspedas.wind`), moving them under `pyspedas.projects`
- Added compatibility shim after every `import pyspedas` that re-attaches the mission modules if missing
- Files: `data_download_pyspedas.py` (2 locations), `vdyes.py`, `plotbot_interactive_vdf.py`

**2. y_limit bug fix in plotbot_main.py**
- Fixed issue where user-set style attributes (e.g. `my_var.y_limit = [0, 3000]`) were lost between plotbot() calls
- Root cause: After the first plotbot() call, `get_data()` replaces the container's variable copy, so the user's local reference becomes stale
- Fix: Store the user's original variable reference in `plot_requests`, then sync style attributes from it onto the fresh container variable before plotting
- Synced attributes: color, y_label, legend_label, plot_type, y_scale, y_limit, line_style, marker_size, marker_style, line_width, alpha, colormap, colorbar_scale, colorbar_limits
