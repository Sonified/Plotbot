import os
import matplotlib.pyplot as plt_mod
from plotbot.multiplot import multiplot
from plotbot.multiplot_options import plt as pbplt
from plotbot import mag_rtn_4sa, proton
import numpy as np

# Use a known time for data availability
center_time = '2024-03-30 12:00:00.000'
plot_data = [
    (center_time, mag_rtn_4sa.br),
    (center_time, mag_rtn_4sa.bt),
    (center_time, mag_rtn_4sa.bn),
    (center_time, proton.density),  # Use .density instead of .np
    (center_time, proton.anisotropy)
]

def overlay_settings_label(axs, settings):
    # Determine margin mode for overlay
    margin_mode = 'default' if settings.get('use_default_plot_settings', False) else 'custom'
    label = (f"title_pad={settings['title_pad']}\n"
             f"constrained_layout={settings['constrained_layout']}\n"
             f"margins={margin_mode}")
    # Flatten axs if it's a numpy array
    if isinstance(axs, np.ndarray):
        axs = axs.flatten().tolist()
    elif not isinstance(axs, list):
        axs = [axs]
    print(f"Overlaying label on {len(axs)} axes: {label}")
    for ax in axs:
        ax.text(0.98, 0.98, label, transform=ax.transAxes, fontsize=10, color='black',
                ha='right', va='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

def test_constrained_layout_true_false_only():
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Only use True/False for constrained_layout, and default/2 for title_pad
    title_pad_options = [None, 2]  # None means use default
    constrained_layout_options = [True, False]

    for title_pad in title_pad_options:
        for constrained_layout in constrained_layout_options:
            pbplt.options.reset()
            pbplt.options.use_single_title = False
            pbplt.options.single_title_text = None
            settings = {}
            # Set options and record for overlay/filename
            if title_pad is not None:
                pbplt.options.title_pad = title_pad
                settings['title_pad'] = title_pad
            else:
                settings['title_pad'] = 'default'
            pbplt.options.constrained_layout = constrained_layout
            settings['constrained_layout'] = constrained_layout
            # Build filename
            fname = (
                f"five_panel_"
                f"titlepad_{settings['title_pad']}__"
                f"constrained_{settings['constrained_layout']}.png"
            )
            fig, axs = multiplot(plot_data)
            overlay_settings_label(axs, settings)
            fig.savefig(os.path.join(output_dir, fname), dpi=150)
            plt_mod.close(fig)
            print(f"Saved {fname}")

def demo_per_panel_titlepad():
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    pbplt.options.reset()
    pbplt.options.use_single_title = False
    pbplt.options.constrained_layout = False
    # Set a default title_pad, but we'll override per panel
    pbplt.options.title_pad = 2
    fig, axs = multiplot(plot_data)
    # Flatten axs if needed
    if isinstance(axs, np.ndarray):
        axs = axs.flatten().tolist()
    elif not isinstance(axs, list):
        axs = [axs]
    # Per-panel title_pad values
    title_pads = [2, 1, 0.5, 0, -2]
    for ax, pad in zip(axs, title_pads):
        # Get current title text
        title = ax.get_title()
        # Re-set the title with new pad
        ax.set_title(title, pad=pad)
        # Overlay the pad value
        ax.text(0.98, 0.98, f"title_pad={pad}", transform=ax.transAxes, fontsize=10, color='black',
                ha='right', va='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    fig.canvas.draw()
    fig.savefig(os.path.join(output_dir, 'five_panel_per_panel_titlepad_demo.png'), dpi=150)
    plt_mod.close(fig)
    print("Saved five_panel_per_panel_titlepad_demo.png")

def both_false_per_panel_titlepad():
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    pbplt.options.reset()
    pbplt.options.use_single_title = False
    pbplt.options.use_default_plot_settings = False
    pbplt.options.constrained_layout = False
    pbplt.options.title_pad = 2  # Default, will override per panel
    fig, axs = multiplot(plot_data)
    if isinstance(axs, np.ndarray):
        axs = axs.flatten().tolist()
    elif not isinstance(axs, list):
        axs = [axs]
    # Per-panel title_pad values
    title_pads = [2, 1, 0.5, 0, -1]
    for ax, pad in zip(axs, title_pads):
        title = ax.get_title()
        ax.set_title(title, pad=pad)
        # Overlay pad and margin mode
        margin_mode = 'custom'  # Both options are False
        label = f"title_pad={pad}\nmargins={margin_mode}"
        ax.text(0.98, 0.98, label, transform=ax.transAxes, fontsize=10, color='black',
                ha='right', va='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    fig.canvas.draw()
    fig.savefig(os.path.join(output_dir, 'five_panel_both_false_per_panel_titlepad.png'), dpi=150)
    plt_mod.close(fig)
    print("Saved five_panel_both_false_per_panel_titlepad.png")

def both_false_compare():
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    pbplt.options.reset()
    pbplt.options.use_single_title = False
    pbplt.options.use_default_plot_settings = False
    pbplt.options.constrained_layout = False
    pbplt.options.title_pad = 2
    pbplt.options.width = 12
    pbplt.options.height_per_panel = 2
    fig, axs = multiplot(plot_data)
    if isinstance(axs, np.ndarray):
        axs = axs.flatten().tolist()
    elif not isinstance(axs, list):
        axs = [axs]
    label = f"use_default_plot_settings=False\nconstrained_layout=False\ntitle_pad=2\nwidth=12\nheight_per_panel=2"
    for ax in axs:
        ax.text(0.98, 0.98, label, transform=ax.transAxes, fontsize=10, color='black',
                ha='right', va='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    fig.canvas.draw()
    fig.savefig(os.path.join(output_dir, 'five_panel_both_false_compare.png'), dpi=150)
    plt_mod.close(fig)
    print("Saved five_panel_both_false_compare.png")

test_constrained_layout_true_false_only()
demo_per_panel_titlepad()
both_false_per_panel_titlepad()
both_false_compare() 