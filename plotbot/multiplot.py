# Import plotbot components with relative imports
from .data_cubby import data_cubby
from .data_tracker import global_tracker  
from .data_download import download_new_psp_data
from .data_import import import_data_function
from .print_manager import print_manager
from .get_encounter import get_encounter_number
from .plotbot_helpers import time_clip
# Import specific functions from multiplot_helpers instead of using wildcard import
from .multiplot_helpers import get_plot_colors, apply_panel_color, apply_bottom_axis_color
from .multiplot_options import plt, MultiplotOptions

# Import standard libraries
import matplotlib.colors as colors
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def multiplot(plot_list, **kwargs):
    """
    Create multiple time-series plots centered around specific times.
    Uses global plt.options for defaults, with kwargs allowing parameter override.
    
    Args:
        plot_list: List of tuples (time, variable)
        **kwargs: Optional overrides for any MultiplotOptions attributes
    """
    # ====================================================================
    # Initialize options and settings
    # ====================================================================
    # Get options instance
    options = plt.options
    
    # Override any options with provided kwargs
    for key, value in kwargs.items():
        if hasattr(options, key):
            setattr(options, key, value)
    
    print_manager.debug("\n=== Starting Multiplot Function ===")
    print_manager.debug(f"Window: {options.window}, Position: {options.position}")
    
    # Convert window to timedelta
    window_td = pd.Timedelta(options.window)
    print_manager.debug(f"Window timedelta: {window_td}")
    
    # Calculate number of panels needed
    n_panels = len(plot_list)
    print_manager.debug(f"Number of panels: {n_panels}")
    
    # Create figure with subplots
    print_manager.debug("\nCreating figure...")
    fig, axs = plt.subplots(n_panels, 1, 
                           figsize=(options.width, options.height_per_panel*n_panels), 
                           sharex=False)
    
    if n_panels == 1:
        axs = [axs]
    
    # Adjust subplot spacing
    plt.subplots_adjust(right=0.85, hspace=options.hspace)
    
    # Get color scheme based on color_mode
    color_scheme = get_plot_colors(n_panels, options.color_mode, options.single_color)

    # Position descriptions
    pos_desc = {
        'before': 'Region before',
        'around': 'Region around',
        'after': 'Region after'
    }
    # ====================================================================
    # Configure Time Windows and Process Data for Each Panel
    # ====================================================================
    for i, (center_time, var) in enumerate(plot_list):
        print_manager.status('Adding data to plot... \n')
        print_manager.debug(f"\n=== Processing Panel {i+1}/{n_panels} ===")
        print_manager.debug(f"Center time: {center_time}")
        center_dt = pd.Timestamp(center_time)
        
        # Get encounter number automatically
        enc_num = get_encounter_number(center_time)
    
        # Format time range
        if options.position == 'around':
            start_time = center_dt - window_td/2
            end_time = center_dt + window_td/2
        elif options.position == 'before':
            start_time = center_dt - window_td
            end_time = center_dt
        else:  # after
            start_time = center_dt
            end_time = center_dt + window_td
    
        trange = [
            start_time.strftime('%Y-%m-%d/%H:%M:%S.%f'),
            end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
        ]
    
        # ====================================================================
        # Multi-Variable Plot Type Handling (time_series only)
        # ====================================================================
        if isinstance(var, list):
            processed_vars = []
            for single_var in var:
                plot_request = {
                    'data_type': single_var.data_type,
                    'class_name': single_var.class_name,
                    'subclass_name': single_var.subclass_name,
                    'axis_spec': 1
                }
                
                print_manager.debug(f"\nProcessing {plot_request['data_type']} - {plot_request['subclass_name']}")
                download_new_psp_data(trange, plot_request['data_type'])
                class_instance = data_cubby.grab(plot_request['class_name'])
                needs_import = global_tracker.is_import_needed(trange, plot_request['data_type'])
                needs_refresh = False
    
                if hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None:
                    cached_start = np.datetime64(class_instance.datetime_array[0], 's')
                    cached_end = np.datetime64(class_instance.datetime_array[-1], 's')
                    requested_start = np.datetime64(start_time, 's')
                    requested_end = np.datetime64(end_time, 's')
    
                    buffered_start = cached_start - np.timedelta64(10, 's')
                    buffered_end = cached_end + np.timedelta64(10, 's')
    
                    if buffered_start > requested_start or buffered_end < requested_end:
                        needs_refresh = True
    
                if needs_import or needs_refresh:
                    data_obj = import_data_function(trange, plot_request['data_type'])
                    if needs_import:
                        global_tracker.update_imported_range(trange, plot_request['data_type'])
                    if data_obj is not None:
                        class_instance.update(data_obj)
    
                processed_var = class_instance.get_subclass(plot_request['subclass_name'])
                processed_vars.append(processed_var)
            
            var = processed_vars
        else:
            plot_request = {
                'data_type': var.data_type,
                'class_name': var.class_name,
                'subclass_name': var.subclass_name,
                'axis_spec': 1
            }
            
            print_manager.debug(f"\nProcessing {plot_request['data_type']} - {plot_request['subclass_name']}")
            download_new_psp_data(trange, plot_request['data_type'])
            class_instance = data_cubby.grab(plot_request['class_name'])
            needs_import = global_tracker.is_import_needed(trange, plot_request['data_type'])
            needs_refresh = False
    
            if hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None:
                cached_start = np.datetime64(class_instance.datetime_array[0], 's')
                cached_end = np.datetime64(class_instance.datetime_array[-1], 's')
                requested_start = np.datetime64(start_time, 's')
                requested_end = np.datetime64(end_time, 's')
    
                buffered_start = cached_start - np.timedelta64(10, 's')
                buffered_end = cached_end + np.timedelta64(10, 's')
    
                if buffered_start > requested_start or buffered_end < requested_end:
                    needs_refresh = True
    
            if needs_import or needs_refresh:
                data_obj = import_data_function(trange, plot_request['data_type'])
                if needs_import:
                    global_tracker.update_imported_range(trange, plot_request['data_type'])
                if data_obj is not None:
                    class_instance.update(data_obj)
    
            var = class_instance.get_subclass(plot_request['subclass_name'])
    
        # ====================================================================
        # Plot Variables (Multi-Variable) with Plot Type Handling
        # ====================================================================
        panel_color = color_scheme['panel_colors'][i] if color_scheme else None
        
        if isinstance(var, list):
            axis_options = getattr(options, f'ax{i+1}')
            
            for idx, single_var in enumerate(var):
                indices = time_clip(single_var.datetime_array, trange[0], trange[1])
                if len(indices) > 0:
                    if idx == 1 and options.second_variable_on_right_axis:
                        ax2 = axs[i].twinx()
                        if options.color_mode in ['rainbow', 'single'] and panel_color:
                            plot_color = panel_color
                        elif hasattr(axis_options, 'r') and axis_options.r.color is not None:
                            plot_color = axis_options.r.color
                        else:
                            plot_color = single_var.color
    
                        ax2.plot(single_var.datetime_array[indices], 
                                single_var.data[indices],
                                linewidth=single_var.line_width,
                                linestyle=single_var.line_style,
                                label=single_var.legend_label,
                                color=plot_color)
                        
                        if hasattr(axis_options, 'r') and axis_options.r.y_limit is not None:
                            ax2.set_ylim(axis_options.r.y_limit)
                        
                        if panel_color:
                            apply_panel_color(ax2, panel_color, options)
                    
                    else:
                        if options.color_mode in ['rainbow', 'single'] and panel_color:
                            plot_color = panel_color
                        elif hasattr(single_var, 'color') and single_var.color is not None:
                            plot_color = single_var.color
                        elif axis_options.color is not None:
                            plot_color = axis_options.color
                        else:
                            plot_color = None
    
                        axs[i].plot(single_var.datetime_array[indices], 
                                   single_var.data[indices],
                                   linewidth=single_var.line_width,
                                   linestyle=single_var.line_style,
                                   label=single_var.legend_label,
                                   color=plot_color)
                        
                        if panel_color:
                            apply_panel_color(axs[i], panel_color, options)
            
            if len(var) > 1:
                lines_left, labels_left = axs[i].get_legend_handles_labels()
                if options.second_variable_on_right_axis:
                    lines_right, labels_right = ax2.get_legend_handles_labels()
                    axs[i].legend(lines_left + lines_right, 
                                  labels_left + labels_right,
                                  bbox_to_anchor=(1.025, 1),
                                  loc='upper left')
                else:
                    axs[i].legend(bbox_to_anchor=(1.025, 1),
                                  loc='upper left')
        else:
            axis_options = getattr(options, f'ax{i+1}')
            indices = time_clip(var.datetime_array, trange[0], trange[1])
            if len(indices) > 0:
                if hasattr(var, 'plot_type'):
                    if var.plot_type == 'time_series':
                        plot_color = panel_color
                        if not plot_color:
                            plot_color = axis_options.color if axis_options.color else var.color
                        
                        axs[i].plot(var.datetime_array[indices], 
                                    var.data[indices],
                                    linewidth=var.line_width,
                                    linestyle=var.line_style,
                                    color=plot_color)
                        if panel_color:
                            apply_panel_color(axs[i], panel_color, options)
    
                    elif var.plot_type == 'spectral':
                        datetime_clipped = var.datetime_array[indices]
                        data_clipped = np.array(var.data)[indices]
                        additional_data_clipped = np.array(var.additional_data)[indices]
                        
                        colorbar_limits = axis_options.colorbar_limits if hasattr(axis_options, 'colorbar_limits') and axis_options.colorbar_limits else var.colorbar_limits
                        if var.colorbar_scale == 'log':
                            norm = colors.LogNorm(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else colors.LogNorm()
                        elif var.colorbar_scale == 'linear':
                            norm = colors.Normalize(vmin=colorbar_limits[0], vmax=colorbar_limits[1]) if colorbar_limits else None
    
                        im = axs[i].pcolormesh(datetime_clipped, additional_data_clipped, data_clipped,
                                               norm=norm, cmap=var.colormap, shading='auto')
                        
                        pos = axs[i].get_position()
                        cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])
                        cbar = fig.colorbar(im, cax=cax)
    
                        if hasattr(var, 'colorbar_label'):
                            cbar.set_label(var.colorbar_label)
                else:
                    plot_color = panel_color
                    if not plot_color:
                        plot_color = axis_options.color if axis_options.color else var.color
                    
                    axs[i].plot(var.datetime_array[indices], 
                                var.data[indices],
                                linewidth=var.line_width,
                                linestyle=var.line_style,
                                color=plot_color)
                    if panel_color:
                        apply_panel_color(axs[i], panel_color, options)
    
        if axis_options.y_limit:
            axs[i].set_ylim(axis_options.y_limit)
        elif isinstance(var, list):
            all_data = []
            for single_var in var:
                if hasattr(single_var, 'y_limit') and single_var.y_limit:
                    all_data.extend(single_var.y_limit)
            if all_data:
                axs[i].set_ylim(min(all_data), max(all_data))
        elif hasattr(var, 'y_limit') and var.y_limit:
            axs[i].set_ylim(var.y_limit)
        else:
            print_manager.debug("Debug: 'additional_data' or 'datetime_array' attributes not found.")
    
        axs[i].set_xlim(start_time, end_time)
    
        if isinstance(var, list):
            if all(hasattr(v, 'y_label') for v in var):
                y_label = var[0].y_label
            else:
                y_label = ''
        else:
            y_label = var.y_label
    
        if options.y_label_uses_encounter:
            if options.y_label_includes_time:
                y_label = f"{enc_num} Around\n{pd.Timestamp(center_time).strftime('%Y-%m-%d')}\n{pd.Timestamp(center_time).strftime('%H:%M')}"
                axs[i].set_ylabel(y_label, fontsize=options.y_label_size, 
                                  labelpad=options.y_label_pad)
            else:
                y_label = f"$\\mathbf{{{enc_num}}}$"
                axs[i].set_ylabel(y_label, fontsize=options.y_label_size,
                                  rotation=0, ha='right', va='center',
                                  labelpad=options.y_label_pad)
        else:
            axs[i].set_ylabel(y_label, fontsize=options.y_label_size,
                              labelpad=options.y_label_pad)
    
        if isinstance(var, list):
            if hasattr(var[0], 'y_scale') and var[0].y_scale:
                axs[i].set_yscale(var[0].y_scale)
        elif hasattr(var, 'y_scale') and var.y_scale:
            axs[i].set_yscale(var.y_scale)
    
        if options.use_relative_time:
            step_td = pd.Timedelta(value=options.relative_time_step, unit=options.relative_time_step_units)
            current = start_time
            ticks = []
            tick_labels = []
            while current <= end_time:
                ticks.append(current)
                time_from_center = (current - center_dt)
                if options.relative_time_step_units == 'days':
                    value_from_center = time_from_center.total_seconds() / (3600 * 24)
                elif options.relative_time_step_units == 'hours':
                    value_from_center = time_from_center.total_seconds() / 3600
                elif options.relative_time_step_units == 'minutes':
                    value_from_center = time_from_center.total_seconds() / 60
                elif options.relative_time_step_units == 'seconds':
                    value_from_center = time_from_center.total_seconds()
                else:
                    print(f"Unrecognized time step unit: {options.relative_time_step_units}. Please use 'days', 'hours', 'minutes', or 'seconds'.")
                    return
    
                if value_from_center == 0:
                    label = "0"
                else:
                    label = f"{value_from_center:.1f}".rstrip('0').rstrip('.')
                tick_labels.append(label)
                current += step_td
    
            axs[i].set_xticks(ticks)
            
            if options.use_single_x_axis:
                if i < n_panels - 1:
                    axs[i].set_xticklabels([])
                    axs[i].set_xlabel('')
                else:
                    axs[i].set_xticklabels(tick_labels)
                    if options.use_custom_x_axis_label:
                         axs[i].set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        axs[i].set_xlabel(f"Relative Time ({options.relative_time_step_units} from Perihelion)", 
                                        fontweight='bold', fontsize=options.x_label_size)
                   
            else:
                axs[i].set_xticklabels(tick_labels)
                if i < n_panels - 1:
                    axs[i].set_xlabel('')
                else:
                    if options.use_custom_x_axis_label:
                        axs[i].set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        axs[i].set_xlabel(f"Relative Time ({options.relative_time_step_units} from Perihelion)", 
                                        fontweight='bold', fontsize=options.x_label_size)
    
        if options.draw_vertical_line:
            color_to_use = panel_color if panel_color else options.vertical_line_color
            axs[i].axvline(x=center_dt, 
                           color=color_to_use,
                           linestyle=options.vertical_line_style,
                           linewidth=options.vertical_line_width)
    
        if options.use_single_title:
            if i == 0:
                title = (options.single_title_text if options.single_title_text 
                         else f"{enc_num} - {pos_desc[options.position]} - {pd.Timestamp(center_time).strftime('%Y-%m-%d %H:%M')}")
                if options.color_mode in ['rainbow', 'single'] and panel_color:
                    axs[i].set_title(title, fontsize=options.title_fontsize, fontweight='bold', color=panel_color)
                else:
                    axs[i].set_title(title, fontsize=options.title_fontsize, fontweight='bold')
        else:
            title = f"{enc_num} - {pos_desc[options.position]} - {pd.Timestamp(center_time).strftime('%Y-%m-%d %H:%M')}"
            if options.color_mode in ['rainbow', 'single'] and panel_color:
                axs[i].set_title(title, fontsize=options.title_fontsize, color=panel_color)
            else:
                axs[i].set_title(title, fontsize=options.title_fontsize)
    
    if not options.use_relative_time:
        for i, ax in enumerate(axs):
            if options.use_single_x_axis:
                if i < n_panels - 1:
                    ax.set_xticklabels([])
                    ax.set_xlabel('')
                else:
                    if options.use_custom_x_axis_label:
                        ax.set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        ax.set_xlabel("Time", fontweight='bold', fontsize=options.x_label_size)
            else:
                if i == len(axs) - 1:
                    if options.use_custom_x_axis_label:
                        ax.set_xlabel(options.custom_x_axis_label, fontweight='bold', fontsize=options.x_label_size)
                    else:
                        ax.set_xlabel("Time", fontweight='bold', fontsize=options.x_label_size)
                else:
                    ax.set_xlabel('')
    
            ax.tick_params(axis='x', labelsize=options.x_tick_label_size)
            ax.tick_params(axis='y', labelsize=options.y_tick_label_size)
    
    # NEW: Apply dynamic x-axis tick coloring for all panels (changed from only bottom panel)
    if color_scheme:
        for i, ax in enumerate(axs):
            apply_bottom_axis_color(ax, color_scheme['panel_colors'][i])
    
    print_manager.status("Generating multiplot...\n")
    plt.show()
    print_manager.debug("=== Multiplot Complete ===\n")
    
    fig.savefig('multiplot_output.png', dpi=300, bbox_inches='tight', pad_inches=0)
    return fig, axs

print('📈📉 Multiplot Initialized')