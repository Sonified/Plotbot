# Captain's Log - April 30, 2025

## Activities & Learnings 

-   **Proton FITS Naming Convention & Type Hints:** Aligned naming conventions for several `proton_fits_class` attributes where the attribute name included a `_pfits` suffix (e.g., `vdrift_va_pfits`, `valfven_pfits`, `vsw_mach_pfits`, `beta_ppar_pfits`, `beta_pperp_pfits`) while the internal `var_name` did not. Updated the `psp_proton_fits_classes.pyi` stub file to match the actual attribute names used in `psp_proton_fits_classes.py`. This ensures correct type hinting for these attributes. Also adjusted the attribute name for absolute heat flux to `abs_qz_p` in both the `.py` and `.pyi` files for consistency and user preference. 

### Git Push ###
Version: 2025-04-30_v1.14
Commit Message: feat: Align proton fits naming & type hints (2025-04-30_v1.14) 