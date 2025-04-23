# To run this specific test file:
# conda run -n plotbot_env python -m pytest tests/test_package_dependencies.py -v -s

import pytest
from plotbot.test_pilot import phase, system_check

# Attempt to import all major dependencies listed in environment.yml
# This acts as a basic smoke test to ensure the environment is set up correctly.

@pytest.mark.mission("Package Dependency Check") # Updated mission name
def test_package_imports_and_usage(): # Updated function name
    """Verify that essential packages can be imported and perform a basic operation."""
    
    phase(1, "Importing Core Packages") # Updated phase description slightly
    
    imports_ok = True # Flag to track if all imports succeeded
    
    try:
        import numpy as np
        system_check("Import numpy", True, "Failed to import numpy")
    except ImportError as e:
        system_check("Import numpy", False, f"Failed to import numpy: {e}")
        imports_ok = False

    try:
        import pandas as pd
        system_check("Import pandas", True, "Failed to import pandas")
    except ImportError as e:
        system_check("Import pandas", False, f"Failed to import pandas: {e}")
        imports_ok = False

    try:
        import matplotlib
        system_check("Import matplotlib", True, "Failed to import matplotlib")
    except ImportError as e:
        system_check("Import matplotlib", False, f"Failed to import matplotlib: {e}")
        imports_ok = False

    try:
        import ipympl
        system_check("Import ipympl", True, "Failed to import ipympl")
    except ImportError as e:
        system_check("Import ipympl", False, f"Failed to import ipympl: {e}")
        imports_ok = False

    try:
        import ipywidgets as widgets
        system_check("Import ipywidgets", True, "Failed to import ipywidgets")
    except ImportError as e:
        system_check("Import ipywidgets", False, f"Failed to import ipywidgets: {e}")
        imports_ok = False

    try:
        import cdflib
        system_check("Import cdflib", True, "Failed to import cdflib")
    except ImportError as e:
        system_check("Import cdflib", False, f"Failed to import cdflib: {e}")
        imports_ok = False
        
    try:
        import bs4 # from beautifulsoup4
        system_check("Import bs4 (BeautifulSoup)", True, "Failed to import bs4")
    except ImportError as e:
        system_check("Import bs4 (BeautifulSoup)", False, f"Failed to import bs4: {e}")
        imports_ok = False

    try:
        import requests
        system_check("Import requests", True, "Failed to import requests")
    except ImportError as e:
        system_check("Import requests", False, f"Failed to import requests: {e}")
        imports_ok = False

    try:
        import dateutil.parser # from python-dateutil
        system_check("Import dateutil.parser", True, "Failed to import dateutil.parser")
    except ImportError as e:
        system_check("Import dateutil.parser", False, f"Failed to import dateutil.parser: {e}")
        imports_ok = False

    try:
        import scipy.constants
        system_check("Import scipy.constants", True, "Failed to import scipy.constants")
    except ImportError as e:
        system_check("Import scipy.constants", False, f"Failed to import scipy.constants: {e}")
        imports_ok = False

    try:
        import termcolor
        system_check("Import termcolor", True, "Failed to import termcolor")
    except ImportError as e:
        system_check("Import termcolor", False, f"Failed to import termcolor: {e}")
        imports_ok = False

    try:
        import pyspedas
        system_check("Import pyspedas", True, "Failed to import pyspedas")
    except ImportError as e:
        system_check("Import pyspedas", False, f"Failed to import pyspedas: {e}")
        imports_ok = False

    # Only proceed to phase 2 if all imports were successful
    if not imports_ok:
        pytest.fail("One or more essential packages failed to import. Skipping basic usage check.")

    phase(2, "Basic Package Usage Check") # Updated phase description slightly

    try:
        _ = np.array([1, 2, 3])
        system_check("Use numpy (np.array)", True, "Failed basic numpy usage")
    except Exception as e:
        system_check("Use numpy (np.array)", False, f"Failed basic numpy usage: {e}")

    try:
        _ = pd.Series([1, 2, 3])
        system_check("Use pandas (pd.Series)", True, "Failed basic pandas usage")
    except Exception as e:
        system_check("Use pandas (pd.Series)", False, f"Failed basic pandas usage: {e}")

    try:
        _ = matplotlib.get_backend()
        system_check("Use matplotlib (get_backend)", True, "Failed basic matplotlib usage")
    except Exception as e:
        system_check("Use matplotlib (get_backend)", False, f"Failed basic matplotlib usage: {e}")
        
    try:
        _ = ipympl.__version__
        system_check("Use ipympl (__version__)", True, "Failed basic ipympl usage")
    except Exception as e:
        system_check("Use ipympl (__version__)", False, f"Failed basic ipympl usage: {e}")

    try:
        _ = widgets.Button()
        system_check("Use ipywidgets (Button)", True, "Failed basic ipywidgets usage")
    except Exception as e:
        system_check("Use ipywidgets (Button)", False, f"Failed basic ipywidgets usage: {e}")

    try:
        _ = cdflib.__version__
        system_check("Use cdflib (__version__)", True, "Failed basic cdflib usage")
    except Exception as e:
        system_check("Use cdflib (__version__)", False, f"Failed basic cdflib usage: {e}")
        
    try:
        _ = bs4.BeautifulSoup('<a></a>', 'html.parser')
        system_check("Use bs4 (BeautifulSoup)", True, "Failed basic bs4 usage")
    except Exception as e:
        system_check("Use bs4 (BeautifulSoup)", False, f"Failed basic bs4 usage: {e}")

    try:
        _ = requests.__version__
        system_check("Use requests (__version__)", True, "Failed basic requests usage")
    except Exception as e:
        system_check("Use requests (__version__)", False, f"Failed basic requests usage: {e}")

    try:
        _ = dateutil.parser.parse('2023-01-01')
        system_check("Use dateutil.parser (parse)", True, "Failed basic dateutil.parser usage")
    except Exception as e:
        system_check("Use dateutil.parser (parse)", False, f"Failed basic dateutil.parser usage: {e}")

    try:
        _ = scipy.constants.pi
        system_check("Use scipy.constants (pi)", True, "Failed basic scipy.constants usage")
    except Exception as e:
        system_check("Use scipy.constants (pi)", False, f"Failed basic scipy.constants usage: {e}")

    try:
        _ = termcolor.colored('hello', 'red')
        system_check("Use termcolor (colored)", True, "Failed basic termcolor usage")
    except Exception as e:
        system_check("Use termcolor (colored)", False, f"Failed basic termcolor usage: {e}")

    try:
        _ = pyspedas.psp.config # Check if psp submodule loads
        system_check("Use pyspedas (psp.config)", True, "Failed basic pyspedas usage")
    except Exception as e:
        system_check("Use pyspedas (psp.config)", False, f"Failed basic pyspedas usage: {e}") 