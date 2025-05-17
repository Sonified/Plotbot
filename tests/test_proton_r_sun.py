# test_proton_r_sun.py

# These imports are based on the notebook's 'from plotbot import *'
# and subsequent usage of these names.
# It's assumed that 'plotbot/__init__.py' makes 'plt' available,
# likely as an alias or wrapper for pytplot.
from plotbot import print_manager, config, plotbot, mag_rtn_4sa, proton, plt

def main():
    # Configure plotting options via 'plt.options'
    try:
        if hasattr(plt, 'options'):
            if hasattr(plt.options, 'reset'):
                plt.options.reset()
            else:
                print("Warning: plt.options does not have 'reset' method.")
            
            if hasattr(plt.options, 'use_single_title'):
                plt.options.use_single_title = True
            else:
                print("Warning: plt.options does not have 'use_single_title' attribute.")
        else:
            print("Warning: 'plt' does not have 'options' attribute. Plotting options (reset, use_single_title) skipped.")
            print("         This might indicate 'plt' was not imported or exposed correctly from 'plotbot'.")
            print("         Consider importing 'pytplot.options' directly if issues persist.")

    except AttributeError as e:
        print(f"Warning: Could not set plotting options via 'plt.options': {e}")
        print("         Ensure 'plt' is correctly imported and configured from 'plotbot'.")
    except Exception as e:
        print(f"An unexpected error occurred while setting plt.options: {e}")


    # Configure print_manager
    # print_manager.show_status = True # This line is in the notebook but immediately overridden
    print_manager.show_datacubby = True
    print_manager.show_dependency_management = True
    print_manager.show_debug = False    # For WALL OF TEXT print
    print_manager.show_status = True   # As per notebook (final value)

    # Configure data server
    config.data_server = 'berkeley'
    # Server options are 'default', 'spdf' or 'berkeley'

    # Define time range from the notebook
    # Original notebook variable name was Jaye_epad_trange
    time_range_for_plot = ['2021/04/26 00:00:00.000', '2021/04/26 00:01:00.000']

    print(f"--- [test_proton_r_sun] Initializing plotbot call ---")
    print(f"--- [test_proton_r_sun] Time range: {time_range_for_plot} ---")
    print(f"--- [test_proton_r_sun] Variables: mag_rtn_4sa.br, mag_rtn_4sa.pmag, proton.sun_dist_rsun ---")
    print(f"--- [test_proton_r_sun] Print Manager: show_debug={print_manager.show_debug}, show_status={print_manager.show_status} ---")
    print(f"--- [test_proton_r_sun] Config: data_server='{config.data_server}' ---")

    # Call the main plotbot function, replicating the notebook's call
    plotbot(time_range_for_plot,
            mag_rtn_4sa.br, 1,
            mag_rtn_4sa.pmag, 2,
            proton.sun_dist_rsun, 3)

    print(f"--- [test_proton_r_sun] plotbot call completed. ---")

if __name__ == "__main__":
    main() 