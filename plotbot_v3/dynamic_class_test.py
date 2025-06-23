"""
This script demonstrates dynamically creating a data-handling class in Python
based on metadata. It includes dynamic property creation for variables,
a simplified data update mechanism, and basic calculation handling.
"""
import numpy as np
import os

# 1. Dummy Metadata
dummy_metadata = {
    'instrument_short': 'dummy_inst',
    'datatype_name': 'dummy_type1',
    'variables': {
        'var1': {
            'description': 'First dummy variable',
            'units': 'dummy_units_1',
            'plot_options': {
                'y_label': 'Var1 (dummy_units_1)',
                'legend_label': 'Variable 1',
                'color': 'blue'
            }
        },
        'var2': {
            'description': 'Second dummy variable',
            'units': 'dummy_units_2',
            'plot_options': {
                'y_label': 'Var2 (dummy_units_2)',
                'legend_label': 'Variable 2',
                'color': 'red'
            }
        },
        'var3': { # Your NEW variable
            'description': 'Third dummy variable',
            'units': 'dummy_units_3',
            'plot_options': {
                'y_label': 'Var3 (dummy_units_3)',
                'legend_label': 'Variable 3',
                'color': 'purple'
            }
        }
    },
    'calculations': {
        'var_sum': {
            'inputs': ['var1', 'var2'],
            'operation': 'add',
            'plot_options': {
                'y_label': 'Sum (dummy_units_1)',
                'legend_label': 'Var1 + Var2',
                'color': 'green'
            }
        }
    }
}

# 2. Simplified PlotManager for the test
class SimplePlotManager:
    def __init__(self, data_array, plot_options_dict, datetime_array=None):
        self.data = data_array
        self.plot_options = plot_options_dict
        self.datetime_array = datetime_array
        self.name = plot_options_dict.get('legend_label', 'Unknown Variable')

    def __repr__(self):
        dt_info = f"datetime len: {len(self.datetime_array)}" if self.datetime_array is not None else "no datetime"
        data_shape = self.data.shape if hasattr(self.data, 'shape') else type(self.data)
        return f"<SimplePlotManager for '{self.name}', data shape: {data_shape}, {dt_info}>"

from collections import namedtuple
TestDataObject = namedtuple('TestDataObject', ['times', 'data'])

# 3. Factory function to create data classes
def create_data_class(class_name_str, metadata, auto_generate_pyi=True, pyi_filename_template="{class_name}.pyi"):
    def __init__(self_instance, imported_data_obj=None):
        object.__setattr__(self_instance, '_metadata', metadata)
        object.__setattr__(self_instance, 'class_name', metadata.get('instrument_short', 'UnknownInst') + "_" + metadata.get('datatype_name', 'UnknownType'))
        object.__setattr__(self_instance, 'data_type', metadata.get('datatype_name', 'UnknownType'))
        object.__setattr__(self_instance, '_raw_data_arrays', {})
        object.__setattr__(self_instance, 'datetime_array', np.array([]))
        object.__setattr__(self_instance, '_plot_managers', {})

        all_vars_to_initialize = list(metadata.get('variables', {}).keys()) + list(metadata.get('calculations', {}).keys())
        for var_key in all_vars_to_initialize:
            var_meta_lookup = metadata.get('variables', {}).get(var_key) or metadata.get('calculations', {}).get(var_key)
            if var_meta_lookup:
                plot_opts = var_meta_lookup.get('plot_options', {}).copy()
                plot_opts['legend_label'] = plot_opts.get('legend_label', var_key)
                self_instance._plot_managers[var_key] = SimplePlotManager(
                    data_array=np.array([]),
                    plot_options_dict=plot_opts,
                    datetime_array=self_instance.datetime_array
                )
        if imported_data_obj:
            self_instance.update(imported_data_obj)
    def update(self_instance, imported_data_obj):
        print(f"Updating {self_instance.class_name}...")
        if not imported_data_obj or not hasattr(imported_data_obj, 'times') or not hasattr(imported_data_obj, 'data'):
            print("  Update failed: Invalid imported_data_obj.")
            return
        self_instance.datetime_array = np.array(imported_data_obj.times if imported_data_obj.times is not None else [])
        print(f"  Updated datetime_array, length: {len(self_instance.datetime_array)}")
        for var_name in self_instance._metadata.get('variables', {}).keys():
            if var_name in imported_data_obj.data:
                self_instance._raw_data_arrays[var_name] = np.asarray(imported_data_obj.data[var_name])
            else:
                print(f"  Warning: Variable '{var_name}' from metadata not found in imported data.")
                self_instance._raw_data_arrays[var_name] = np.array([])
        for calc_name, calc_meta in self_instance._metadata.get('calculations', {}).items():
            inputs = calc_meta.get('inputs', [])
            operation = calc_meta.get('operation')
            input_data_arrays = [self_instance._raw_data_arrays.get(i) for i in inputs]
            if all(arr is not None and len(arr) > 0 for arr in input_data_arrays):
                if operation == 'add' and len(input_data_arrays) == 2:
                    min_len = min(len(input_data_arrays[0]), len(input_data_arrays[1]))
                    if len(input_data_arrays[0]) != min_len or len(input_data_arrays[1]) != min_len:
                        print(f"  Warning for '{calc_name}': Input arrays have different lengths. Truncating for operation.")
                    self_instance._raw_data_arrays[calc_name] = input_data_arrays[0][:min_len] + input_data_arrays[1][:min_len]
                elif operation == 'magnitude' and len(input_data_arrays) >= 2:
                    # Calculate magnitude: sqrt(x^2 + y^2 + z^2 + ...)
                    min_len = min(len(arr) for arr in input_data_arrays)
                    if not all(len(arr) == min_len for arr in input_data_arrays):
                        print(f"  Warning for '{calc_name}': Input arrays have different lengths. Truncating for operation.")
                    
                    # Truncate all arrays to minimum length and calculate magnitude
                    truncated_arrays = [arr[:min_len] for arr in input_data_arrays]
                    magnitude_squared = np.zeros(min_len)
                    for arr in truncated_arrays:
                        magnitude_squared += arr**2
                    self_instance._raw_data_arrays[calc_name] = np.sqrt(magnitude_squared)
                else:
                    print(f"  Skipping calculation for '{calc_name}': unsupported operation or wrong number of inputs.")
                    self_instance._raw_data_arrays[calc_name] = np.array([])
            else:
                print(f"  Skipping calculation for '{calc_name}': Missing or empty input data.")
                self_instance._raw_data_arrays[calc_name] = np.array([])
        all_var_keys = list(self_instance._metadata.get('variables', {}).keys()) + list(self_instance._metadata.get('calculations', {}).keys())
        for var_key in all_var_keys:
            var_config = self_instance._metadata.get('variables', {}).get(var_key) or self_instance._metadata.get('calculations', {}).get(var_key)
            if var_config:
                plot_opts = var_config.get('plot_options', {}).copy()
                plot_opts['legend_label'] = plot_opts.get('legend_label', var_key)
                data_array_for_pm = self_instance._raw_data_arrays.get(var_key, np.array([]))
                current_dt_array = self_instance.datetime_array
                if len(current_dt_array) > 0 and len(data_array_for_pm) > 0 and len(current_dt_array) != len(data_array_for_pm):
                    print(f"  Warning: Length mismatch for PlotManager '{var_key}'. Datetime: {len(current_dt_array)}, Data: {len(data_array_for_pm)}. Adjusting data to datetime length.")
                    data_array_for_pm = data_array_for_pm[:len(current_dt_array)]
                self_instance._plot_managers[var_key] = SimplePlotManager(
                    data_array=data_array_for_pm,
                    plot_options_dict=plot_opts,
                    datetime_array=current_dt_array
                )
        print(f"Update for {self_instance.class_name} complete.")
    def _create_property_for_variable(var_name_key):
        def getter(self_instance) -> SimplePlotManager | None:
            if var_name_key in self_instance._plot_managers:
                return self_instance._plot_managers[var_name_key]
            else:
                print(f"Error: Plot manager for '{var_name_key}' not found in _plot_managers cache.")
                var_meta_lookup = self_instance._metadata.get('variables', {}).get(var_name_key) or self_instance._metadata.get('calculations', {}).get(var_name_key)
                if var_meta_lookup:
                    plot_opts = var_meta_lookup.get('plot_options', {}).copy()
                    plot_opts['legend_label'] = plot_opts.get('legend_label', var_name_key)
                    return SimplePlotManager(np.array([]), plot_opts, self_instance.datetime_array)
                return None
        return property(getter)
    def __dir__(self_instance):
        # Start with default dir attributes (methods, built-ins, etc.)
        default_attrs = set(object.__dir__(self_instance))
        # Add keys from our metadata (variables and calculations)
        if hasattr(self_instance, '_metadata') and self_instance._metadata is not None:
            default_attrs.update(self_instance._metadata.get('variables', {}).keys())
            default_attrs.update(self_instance._metadata.get('calculations', {}).keys())
        return sorted(list(default_attrs))
    class_attributes = {
        '__init__': __init__,
        'update': update,
        '__dir__': __dir__
    }
    for var_name in metadata.get('variables', {}).keys():
        class_attributes[var_name] = _create_property_for_variable(var_name)
    for calc_name in metadata.get('calculations', {}).keys():
        class_attributes[calc_name] = _create_property_for_variable(calc_name)
    NewClass = type(class_name_str, (object,), class_attributes)

    if auto_generate_pyi:
        actual_pyi_filename = pyi_filename_template.format(class_name=class_name_str)
        # Ensure the class name used in the stub matches the one being created.
        generate_pyi_stub(metadata, class_name_for_stub=class_name_str, pyi_filename=actual_pyi_filename)

    return NewClass

def generate_pyi_stub(metadata, class_name_for_stub: str, pyi_filename: str = "dynamic_class_test.pyi"):
    """Generates a .pyi stub file content based on metadata."""
    lines = []
    lines.append("# This is an auto-generated .pyi file. Do not edit manually.")
    lines.append("import numpy as np")
    lines.append("from collections import namedtuple")
    lines.append("")

    # SimplePlotManager definition (assuming it's relatively stable or also describable)
    lines.append("class SimplePlotManager:")
    lines.append("    data: np.ndarray")
    lines.append("    plot_options: dict")
    lines.append("    datetime_array: np.ndarray | None")
    lines.append("    name: str")
    lines.append("    def __init__(self, data_array: np.ndarray, plot_options_dict: dict, datetime_array: np.ndarray | None = ..., /) -> None: ...")
    lines.append("    def __repr__(self) -> str: ...")
    lines.append("")

    lines.append("TestDataObject = namedtuple('TestDataObject', ['times', 'data'])")
    lines.append("dummy_metadata: dict # Or more specific type if metadata structure is fixed")
    lines.append("")

    lines.append(f"def create_data_class(class_name_str: str, metadata: dict) -> type[{class_name_for_stub}]: ...")
    lines.append("")

    lines.append(f"class {class_name_for_stub}:")
    # Internal attributes (optional, but can be good for completeness)
    lines.append("    _metadata: dict")
    lines.append("    class_name: str")
    lines.append("    data_type: str")
    lines.append("    _raw_data_arrays: dict")
    lines.append("    datetime_array: np.ndarray")
    lines.append("    _plot_managers: dict")
    lines.append("")

    # Dynamically created properties
    variables = metadata.get('variables', {})
    calculations = metadata.get('calculations', {})
    all_dynamic_members = list(variables.keys()) + list(calculations.keys())

    if not all_dynamic_members:
        lines.append("    pass  # No dynamic members defined in metadata")
    else:
        for member_name in all_dynamic_members:
            lines.append(f"    {member_name}: SimplePlotManager")
    lines.append("")

    # Method signatures
    lines.append("    def __init__(self, imported_data_obj: TestDataObject | None = ..., /) -> None: ...")
    lines.append("    def update(self, imported_data_obj: TestDataObject, /) -> None: ...")
    lines.append("    def __dir__(self) -> list[str]: ...")
    lines.append("")
    
    pyi_content_new = "\n".join(lines)
    
    # Check if file exists and content is the same to avoid unnecessary writes
    existing_content = ""
    if os.path.exists(pyi_filename):
        try:
            with open(pyi_filename, 'r') as f_read:
                existing_content = f_read.read()
        except IOError as e:
            print(f"Warning: Could not read existing {pyi_filename} for comparison: {e}")

    if existing_content == pyi_content_new:
        print(f"{pyi_filename} is already up-to-date.")
        return pyi_content_new # Or just return

    try:
        with open(pyi_filename, 'w') as f_write:
            f_write.write(pyi_content_new)
        print(f"Successfully generated/updated {pyi_filename}")
    except IOError as e:
        print(f"Error writing {pyi_filename}: {e}")
    
    return pyi_content_new

if __name__ == "__main__":
    print("Creating DynamicDataHandler (which will now auto-generate .pyi stub if enabled)...")
    DynamicDataHandler = create_data_class(
        'DynamicDataHandler', 
        dummy_metadata, 
        auto_generate_pyi=True, # Explicitly enable for this test run
        pyi_filename_template="dynamic_class_test.pyi" # Ensure it uses the correct file for this module
    )

    # The rest of the test code from the original if __name__ == "__main__" block:
    print("Instantiating dynamic class (no data yet)...")
    dynamic_instance = DynamicDataHandler()
    print(f"Accessing dynamic_instance.var1 (before data): {dynamic_instance.var1}")
    print(f"Accessing dynamic_instance.var2 (before data): {dynamic_instance.var2}")
    print(f"Accessing dynamic_instance.var_sum (before data): {dynamic_instance.var_sum}")
    print("-" * 30)
    print("Simulating data import...")
    simulated_times = np.array([f'2024-01-01T00:00:0{i}Z' for i in range(5)], dtype='datetime64[s]')
    simulated_data_dict = {
        'var1': np.array([10, 11, 12, 13, 14]),
        'var2': np.array([20, 22, 24, 26, 28])
    }
    simulated_imported_data = TestDataObject(times=simulated_times, data=simulated_data_dict)
    dynamic_instance.update(simulated_imported_data)
    print("-" * 30)
    print("Accessing properties after data load:")
    var1_pm = dynamic_instance.var1
    var2_pm = dynamic_instance.var2
    var_sum_pm = dynamic_instance.var_sum
    print(f"dynamic_instance.var1: {var1_pm}")
    print(f"  var1 data: {var1_pm.data if var1_pm else 'N/A'}")
    print(f"  var1 plot options: {var1_pm.plot_options if var1_pm else 'N/A'}")
    print(f"dynamic_instance.var2: {var2_pm}")
    print(f"  var2 data: {var2_pm.data if var2_pm else 'N/A'}")
    print(f"dynamic_instance.var_sum: {var_sum_pm}")
    print(f"  var_sum data: {var_sum_pm.data if var_sum_pm else 'N/A'}")
    print(f"  var_sum plot options: {var_sum_pm.plot_options if var_sum_pm else 'N/A'}")
    print("-" * 30)
    print("\nSimulating data import with different length for one variable...")
    simulated_times_2 = np.array([f'2024-01-01T00:00:0{i}Z' for i in range(3)], dtype='datetime64[s]')
    simulated_data_dict_2 = {
        'var1': np.array([100, 110, 120, 130]),
        'var2': np.array([200, 220, 240])
    }
    simulated_imported_data_2 = TestDataObject(times=simulated_times_2, data=simulated_data_dict_2)
    dynamic_instance.update(simulated_imported_data_2)
    print("Accessing properties after second data load (with mismatched lengths):")
    var1_pm_2 = dynamic_instance.var1
    var2_pm_2 = dynamic_instance.var2
    var_sum_pm_2 = dynamic_instance.var_sum
    print(f"dynamic_instance.var1: {var1_pm_2}")
    print(f"  var1 data after second update: {var1_pm_2.data if var1_pm_2 else 'N/A'}")
    print(f"dynamic_instance.var2: {var2_pm_2}")
    print(f"  var2 data after second update: {var2_pm_2.data if var2_pm_2 else 'N/A'}")
    print(f"dynamic_instance.var_sum: {var_sum_pm_2}")
    print(f"  var_sum data after second update: {var_sum_pm_2.data if var_sum_pm_2 else 'N/A'}")
    print("\nTest complete.")
