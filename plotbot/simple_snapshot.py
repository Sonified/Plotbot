# plotbot/simple_snapshot.py

import pickle
from datetime import datetime
from .data_cubby import data_cubby
from .data_tracker import global_tracker

def save_simple_snapshot(filename):
    populated_data = {}
    for key, instance in data_cubby.class_registry.items():
        # Check if the instance has a 'datetime_array' attribute,
        # if it's not None, and if its length is greater than 0.
        # This is a common pattern for populated time-series data objects.
        datetime_array_attr = getattr(instance, 'datetime_array', None)
        if datetime_array_attr is not None and len(datetime_array_attr) > 0:
            populated_data[key] = instance
        else:
            # Optional: You could log skipped items for debugging if needed
            # print(f"[save_simple_snapshot] Skipping '{key}' as it appears to have no data or an empty datetime_array.")
            pass

    snapshot = {
        'data': populated_data,  # Only save items deemed to have data
        'tracker': global_tracker.calculated_ranges,
        'timestamp': datetime.now()
    }
    with open(filename, 'wb') as f:
        pickle.dump(snapshot, f)
    # Optional: Confirmation message about how many items were saved
    print(f"✅ Snapshot saved. Included {len(populated_data)} data items from data_cubby.")
    print(f"   Saved keys: {list(populated_data.keys())}")

def load_simple_snapshot(filename):
    with open(filename, 'rb') as f:
        snapshot = pickle.load(f)
    
    print(f"ℹ️  Loading snapshot. Keys found in snapshot['data']: {list(snapshot['data'].keys())}")

    # Restore the core state
    data_cubby.class_registry.update(snapshot['data'])
    global_tracker.calculated_ranges.update(snapshot['tracker'])
    
    import plotbot
    
    # Mapping of data_cubby keys to plotbot attributes
    data_mappings = {
        'proton': 'proton',
        'ham': 'ham', 
        'epad': 'epad',
        'epad_hr': 'epad_hr',
        'mag_rtn_4sa': 'mag_rtn_4sa',
        'mag_rtn': 'mag_rtn',
        'mag_sc_4sa': 'mag_sc_4sa',
        'mag_sc': 'mag_sc',
        'proton_hr': 'proton_hr',
        'proton_fits': 'proton_fits'
    }
    
    # Restore each data type
    for cubby_key_from_snapshot in snapshot['data'].keys():
        if cubby_key_from_snapshot in data_mappings: # Check if this loaded key is one we know how to map
            plotbot_attr = data_mappings[cubby_key_from_snapshot]
            if hasattr(plotbot, plotbot_attr):
                # Ensure we are getting the instance that was updated in data_cubby from the snapshot
                if cubby_key_from_snapshot in data_cubby.class_registry:
                    loaded_instance = data_cubby.class_registry[cubby_key_from_snapshot]
                    plotbot_instance = getattr(plotbot, plotbot_attr)
                    
                    # Use built-in restore method if available, otherwise manual copy
                    if hasattr(plotbot_instance, 'restore_from_snapshot'):
                        plotbot_instance.restore_from_snapshot(loaded_instance)
                    else:
                        # Manual attribute copying for classes without restore method
                        print(f"   [LOAD] Attempting manual attribute copy for: {cubby_key_from_snapshot}") # DEBUG
                        for attr_name, attr_value in loaded_instance.__dict__.items():
                            # print(f"      Setting {attr_name} on {plotbot_attr}") # DEBUG Intensive
                            object.__setattr__(plotbot_instance, attr_name, attr_value)
                    
                    # Recreate plot managers
                    if hasattr(plotbot_instance, 'set_plot_config'):
                        print(f"   [LOAD] Calling set_plot_config for: {cubby_key_from_snapshot}") # DEBUG
                        plotbot_instance.set_plot_config()
                else:
                    print(f"   [LOAD WARNING] Key '{cubby_key_from_snapshot}' was in snapshot but not in data_cubby after update. Skipping.")
            else:
                print(f"   [LOAD WARNING] Plotbot module does not have attribute '{plotbot_attr}' for cubby key '{cubby_key_from_snapshot}'. Skipping.")
        else:
            print(f"   [LOAD WARNING] Key '{cubby_key_from_snapshot}' from snapshot is not in data_mappings. Skipping.")
    
    print("✅ Snapshot loaded! Your variables should work immediately.")