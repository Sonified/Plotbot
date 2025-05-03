import os
import matplotlib.pyplot as plt_mod
from plotbot.multiplot import multiplot
from plotbot.multiplot_options import plt as pbplt
from plotbot import mag_rtn_4sa, proton
import numpy as np

center_time = '2024-03-30 12:00:00.000'
plot_data = [
    (center_time, mag_rtn_4sa.br),
    (center_time, mag_rtn_4sa.bt),
    (center_time, mag_rtn_4sa.bn),
    (center_time, proton.density),
    (center_time, proton.anisotropy)
]

def test_hspace_exploration():
    output_dir = os.path.join(os.path.dirname(__file__), 'output', 'tests_154am')
    os.makedirs(output_dir, exist_ok=True)
    hspace_values = [2, 1, 0.5, 0, -1]
    for hspace in hspace_values:
        # Reset all options
        pbplt.options.reset()
        pbplt.options.use_single_title = False
        pbplt.options.use_default_plot_settings = False
        pbplt.options.constrained_layout = False
        pbplt.options.title_pad = 2
        pbplt.options.width = 12
        pbplt.options.height_per_panel = 2
        pbplt.options.hspace = hspace
        # Print all relevant settings
        settings = {
            'hspace': hspace,
            'constrained_layout': pbplt.options.constrained_layout,
            'use_default_plot_settings': pbplt.options.use_default_plot_settings,
            'title_pad': pbplt.options.title_pad,
            'width': pbplt.options.width,
            'height_per_panel': pbplt.options.height_per_panel,
            'use_single_title': pbplt.options.use_single_title,
        }
        fig, axs = multiplot(plot_data)
        if isinstance(axs, np.ndarray):
            axs = axs.flatten().tolist()
        elif not isinstance(axs, list):
            axs = [axs]
        label = '\n'.join(f"{k}={v}" for k, v in settings.items())
        for ax in axs:
            ax.text(0.98, 0.98, label, transform=ax.transAxes, fontsize=10, color='black',
                    ha='right', va='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        fig.canvas.draw()
        fname = f"five_panel_hspace_{hspace}.png"
        fig.savefig(os.path.join(output_dir, fname), dpi=150)
        plt_mod.close(fig)
        print(f"Saved {fname} with settings: {settings}")

test_hspace_exploration() 