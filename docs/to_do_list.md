# Plotbot To-Do List

## Primary Goal: Integrate `pyspedas` Data Download

* [X] Install `pyspedas` (Add to `environment.yml` & update `Install_Scripts/`).
* [ ] Test `pyspedas` download functions (using `downloadonly=True`, `notplot=True` in `tests/test_spdf_download.py`).
* [ ] Determine `pyspedas` default download folder structure.
* [ ] Ensure SPDF downloads land in the same structure as Berkeley downloads (configure `pyspedas` path or adjust Plotbot logic).
* [ ] Compare variable names within CDFs downloaded via SPDF vs. Berkeley.

## Installer/Environment Updates (Lower Priority)

* [ ] Add `pytest` to `environment.yml` / installer.
* [ ] Add `termcolor` to `environment.yml` / installer.
* [ ] Add `ipympl` (for `%matplotlib widget`) to `environment.yml` / installer.

## Code Structure / Refactoring

* [ ] Standardize and potentially globalize access to `multiplot` options (`plt.options`) for better consistency and easier configuration across the application.
