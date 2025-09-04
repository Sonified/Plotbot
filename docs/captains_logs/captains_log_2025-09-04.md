# Captain's Log - 2025-09-04

## Version: v3.23

## Major Installation System Overhaul

### Problems Identified and Fixed:

**1. Directory Case Sensitivity Issue (CRITICAL)**
- **Problem**: Had both `Install_Scripts` (git-tracked) and `install_scripts` (local duplicate) directories
- **Impact**: Caused git confusion, Cursor UI glitches, and installation path conflicts  
- **Solution**: Resolved case sensitivity, standardized on `Install_Scripts`
- **Result**: Clean git state, proper file tracking

**2. Environment Naming Confusion**
- **Problem**: Both installation methods created environments named `plotbot_env`
- **Impact**: Users couldn't distinguish between micromamba and anaconda environments
- **Solution**: Implemented clear naming convention:
  - Micromamba: `plotbot_micromamba` → "Plotbot (Micromamba)" kernel
  - Anaconda: `plotbot_anaconda` → "Plotbot (Anaconda)" kernel
- **Result**: Clear separation, no naming conflicts

**3. Misleading Documentation and Priority**
- **Problem**: README positioned micromamba as "Option 2" for "restricted environments only"
- **Impact**: Users avoided the easier installation method
- **Solution**: Complete README restructure:
  - Micromamba now "Option 1: Recommended for ALL users"
  - Anaconda now "Option 2: Traditional method"
  - Accurate prerequisite documentation (git requirement, not "zero prerequisites")
- **Result**: Users get the easiest path by default

**4. Installation Script Priority Mismatch**
- **Problem**: `install.sh` still promoted anaconda as "Option 1"
- **Impact**: Script contradicted README recommendations
- **Solution**: Updated installer to match README:
  - Option 1: Micromamba Installation ⭐ (Recommended for ALL users)
  - Option 2: Anaconda Installation (Traditional method)
- **Result**: Consistent messaging across all documentation

**5. Prerequisite Requirements Clarification**
- **Problem**: Confusing claims about what each installation method needs
- **Impact**: Users unclear about actual requirements
- **Solution**: Accurate documentation:
  - Both methods need working git (various sources available)
  - No compilation tools needed for our specific package set
  - Removed misleading "zero prerequisites" claims
- **Result**: Honest, accurate user expectations

### Technical Improvements:

**1. Enhanced Error Handling**
- Added retry loops for invalid user input
- No more crashes on accidental Enter presses
- Clear error messages with guidance

**2. Robust Installation Flow**
- End-to-end testing confirmed working
- Both installation paths complete successfully  
- Proper environment creation and kernel registration

**3. Installer Script Fixes**
- Fixed micromamba argument order issues
- Improved environment detection logic
- Updated all references to new naming convention

### Testing Results:
- ✅ Complete installation flow (install.sh) works from start to finish
- ✅ Both micromamba and anaconda paths create proper environments
- ✅ Jupyter kernels register with correct descriptive names
- ✅ Plotbot imports and runs successfully in both environments
- ✅ Error handling gracefully handles user input mistakes

### User Experience Impact:
- **Dramatically simplified** installation process for majority of users
- **Clear documentation** about what's actually needed  
- **Robust error handling** prevents frustrating crashes
- **Professional naming** makes environment selection obvious
- **Honest prerequisites** - no misleading "zero prerequisites" claims

This overhaul transforms Plotbot from having a confusing, error-prone installation process to a professional, user-friendly setup experience that works reliably for all user types.

## Repository Size Optimization

### Issue: Large test data files tracked by Git
- **Problem**: `tests/data/` directory containing large .cdf files (8.8MB and 4.5MB) were being tracked by Git
- **Impact**: Increased repository download size for new users
- **Solution**: Added `tests/data/` to `.gitignore` and removed from Git index using `git rm --cached -r tests/data/`
- **Version Fix**: Corrected erroneous v1.00 commit to proper v3.23
- **Result**: Reduced repository size for new user downloads

**Commit Message**: "v3.23 Removed tests/data from Git index as per .gitignore"
**Version Tag**: v3.23
