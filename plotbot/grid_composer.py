#grid_composer.py

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Callable, Any
from dataclasses import dataclass
from .print_manager import print_manager

@dataclass
class PlotSpec:
    """Specification for a single plot in the grid"""
    function: Callable
    args: Tuple = ()
    kwargs: Dict = None
    row: int = 0
    col: int = 0
    rowspan: int = 1
    colspan: int = 1
    title: Optional[str] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}

class GridComposer:
    """
    Modular plotting system that integrates multiple plotbot functions into a unified grid layout.
    
    This class allows you to combine plotbot, multiplot, showdahodo, vdyes, and other plotting 
    functions into a single figure with customizable grid layouts.
    
    Example Usage:
        # Create a 2x2 grid
        composer = GridComposer(rows=2, cols=2, figsize=(15, 10))
        
        # Add plots to specific grid positions
        composer.add_plot('plotbot', plotbot, (trange, mag_rtn.br, 1), row=0, col=0)
        composer.add_plot('multiplot', multiplot, ([mag_rtn.br, mag_rtn.bt],), row=0, col=1)
        composer.add_plot('showdahodo', showdahodo, (trange, var1, var2), row=1, col=0)
        composer.add_plot('vdyes', vdyes, (trange,), row=1, col=1)
        
        # Compose the final figure
        final_fig = composer.compose()
    """
    
    def __init__(self, rows: int = 2, cols: int = 2, figsize: Tuple[float, float] = (15, 10), 
                 main_title: Optional[str] = None, hspace: float = 0.3, wspace: float = 0.3):
        """
        Initialize the GridComposer.
        
        Args:
            rows: Number of rows in the grid
            cols: Number of columns in the grid  
            figsize: Figure size (width, height)
            main_title: Optional main title for the entire figure
            hspace: Height spacing between subplots
            wspace: Width spacing between subplots
        """
        self.rows = rows
        self.cols = cols
        self.figsize = figsize
        self.main_title = main_title
        self.hspace = hspace
        self.wspace = wspace
        self.plots: Dict[str, PlotSpec] = {}
        
    def add_plot(self, name: str, function: Callable, args: Tuple = (), kwargs: Dict = None,
                 row: int = 0, col: int = 0, rowspan: int = 1, colspan: int = 1, 
                 title: Optional[str] = None):
        """
        Add a plot to the grid.
        
        Args:
            name: Unique identifier for this plot
            function: Plotting function (plotbot, multiplot, showdahodo, vdyes, etc.)
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            row: Grid row position (0-indexed)
            col: Grid column position (0-indexed)
            rowspan: Number of rows to span
            colspan: Number of columns to span
            title: Optional title for this subplot
        """
        if kwargs is None:
            kwargs = {}
            
        # Add noshow=True to suppress individual plot displays
        if function.__name__ == 'showdahodo':
            kwargs['noshow'] = True
            
        self.plots[name] = PlotSpec(
            function=function,
            args=args,
            kwargs=kwargs,
            row=row,
            col=col,
            rowspan=rowspan,
            colspan=colspan,
            title=title
        )
        print_manager.status(f"📍 Added plot '{name}' to grid position ({row}, {col})")
        
    def _extract_figure_content(self, fig, axes=None) -> Tuple[plt.Figure, Any]:
        """
        Extract the content from a figure for integration into the grid.
        
        Args:
            fig: Source figure
            axes: Source axes (can be single axis or list/array)
            
        Returns:
            Tuple of (figure, axes) ready for integration
        """
        if fig is None:
            print_manager.warning("Received None figure - creating empty placeholder")
            return None, None
            
        return fig, axes
    
    def _copy_figure_to_subplot(self, source_fig, source_axes, target_ax):
        """
        Copy the content from a source figure/axes to a target subplot.
        
        Args:
            source_fig: Source matplotlib figure
            source_axes: Source axes (can be single or multiple)
            target_ax: Target axes in the grid
        """
        if source_fig is None or source_axes is None:
            target_ax.text(0.5, 0.5, 'Plot Failed', ha='center', va='center', 
                          transform=target_ax.transAxes, fontsize=12, color='red')
            return
            
        try:
            # Handle different axes types
            if hasattr(source_axes, '__len__') and not isinstance(source_axes, str):
                # Multiple axes - use the first one or combine
                source_ax = source_axes[0] if len(source_axes) > 0 else source_axes
            else:
                # Single axis
                source_ax = source_axes
                
            # Copy plot elements from source to target
            for line in source_ax.get_lines():
                target_ax.plot(line.get_xdata(), line.get_ydata(),
                             color=line.get_color(),
                             linewidth=line.get_linewidth(),
                             linestyle=line.get_linestyle(),
                             marker=line.get_marker(),
                             markersize=line.get_markersize(),
                             alpha=line.get_alpha(),
                             label=line.get_label())
                             
            # Copy collections (scatter plots, pcolormesh, etc.)
            for collection in source_ax.collections:
                target_ax.add_collection(collection)
                
            # Copy images (pcolormesh, imshow, etc.)
            for image in source_ax.images:
                target_ax.add_image(image)
                
            # Copy axis properties
            target_ax.set_xlim(source_ax.get_xlim())
            target_ax.set_ylim(source_ax.get_ylim())
            target_ax.set_xlabel(source_ax.get_xlabel())
            target_ax.set_ylabel(source_ax.get_ylabel())
            target_ax.set_xscale(source_ax.get_xscale())
            target_ax.set_yscale(source_ax.get_yscale())
            
            # Copy legend if it exists
            legend = source_ax.get_legend()
            if legend:
                target_ax.legend()
                
            print_manager.debug("✅ Successfully copied figure content to subplot")
            
        except Exception as e:
            print_manager.error(f"Error copying figure content: {e}")
            target_ax.text(0.5, 0.5, f'Copy Error:\n{str(e)}', ha='center', va='center',
                          transform=target_ax.transAxes, fontsize=10, color='red')
    
    def _handle_plotbot_special(self, plot_spec: PlotSpec) -> Tuple[plt.Figure, Any]:
        """
        Special handling for plotbot since it doesn't return a figure by default.
        """
        print_manager.status("🤖 Handling plotbot function (requires modification)")
        
        # Store current show state
        original_show = plt.get_backend()
        
        try:
            # Temporarily disable showing
            plt.ioff()  # Turn off interactive mode
            
            # Call plotbot function
            result = plot_spec.function(*plot_spec.args, **plot_spec.kwargs)
            
            # Get the current figure (plotbot creates one)
            fig = plt.gcf()
            axes = fig.get_axes()
            
            # Don't show the figure
            plt.close(fig)  # Close to prevent display
            
            return fig, axes
            
        except Exception as e:
            print_manager.error(f"Error handling plotbot: {e}")
            return None, None
        finally:
            # Restore show state
            plt.ion()  # Turn interactive mode back on
    
    def compose(self, save_individual_plots: bool = False) -> plt.Figure:
        """
        Compose all plots into a single grid figure.
        
        Args:
            save_individual_plots: If True, save individual plots before composing
            
        Returns:
            Final composed figure
        """
        print_manager.status(f"🎼 Composing {len(self.plots)} plots into {self.rows}x{self.cols} grid")
        
        # Create the main figure and grid
        main_fig = plt.figure(figsize=self.figsize)
        if self.main_title:
            main_fig.suptitle(self.main_title, fontsize=16, fontweight='bold')
            
        gs = gridspec.GridSpec(self.rows, self.cols, hspace=self.hspace, wspace=self.wspace)
        
        # Process each plot
        for name, plot_spec in self.plots.items():
            print_manager.status(f"📊 Processing plot '{name}'...")
            
            try:
                # Call the plotting function
                if plot_spec.function.__name__ == 'plotbot':
                    # Special handling for plotbot
                    source_fig, source_axes = self._handle_plotbot_special(plot_spec)
                else:
                    # Standard handling for functions that return figures
                    result = plot_spec.function(*plot_spec.args, **plot_spec.kwargs)
                    
                    # Handle different return types
                    if isinstance(result, tuple):
                        source_fig, source_axes = result
                    elif hasattr(result, 'figure'):  # Widget case
                        print_manager.warning(f"Plot '{name}' returned a widget - using figure property")
                        source_fig = result.figure if hasattr(result, 'figure') else None
                        source_axes = source_fig.get_axes() if source_fig else None
                    else:
                        # Assume it's a figure
                        source_fig = result
                        source_axes = source_fig.get_axes() if source_fig else None
                
                # Create subplot in the grid
                subplot_ax = main_fig.add_subplot(gs[plot_spec.row:plot_spec.row + plot_spec.rowspan,
                                                   plot_spec.col:plot_spec.col + plot_spec.colspan])
                
                # Set subplot title if provided
                if plot_spec.title:
                    subplot_ax.set_title(plot_spec.title, fontweight='bold')
                    
                # Copy content to the subplot
                self._copy_figure_to_subplot(source_fig, source_axes, subplot_ax)
                
                # Optionally save individual plot
                if save_individual_plots and source_fig:
                    individual_filename = f"individual_plot_{name}.png"
                    source_fig.savefig(individual_filename, bbox_inches='tight', dpi=300)
                    print_manager.status(f"💾 Saved individual plot: {individual_filename}")
                
                # Close the source figure to free memory
                if source_fig:
                    plt.close(source_fig)
                    
                print_manager.status(f"✅ Successfully added '{name}' to grid")
                
            except Exception as e:
                print_manager.error(f"❌ Error processing plot '{name}': {e}")
                # Create error placeholder
                error_ax = main_fig.add_subplot(gs[plot_spec.row:plot_spec.row + plot_spec.rowspan,
                                                 plot_spec.col:plot_spec.col + plot_spec.colspan])
                error_ax.text(0.5, 0.5, f"Error in '{name}':\n{str(e)}", 
                             ha='center', va='center', transform=error_ax.transAxes,
                             fontsize=10, color='red', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                error_ax.set_title(f"❌ {name} (Error)", color='red')
        
        print_manager.status("🎼 Grid composition complete!")
        return main_fig

# Convenience functions for common grid layouts
def create_2x2_grid(figsize=(15, 10), main_title=None):
    """Create a 2x2 grid composer"""
    return GridComposer(rows=2, cols=2, figsize=figsize, main_title=main_title)

def create_1x4_grid(figsize=(20, 5), main_title=None):
    """Create a 1x4 horizontal grid composer"""
    return GridComposer(rows=1, cols=4, figsize=figsize, main_title=main_title)

def create_4x1_grid(figsize=(8, 16), main_title=None):
    """Create a 4x1 vertical grid composer"""
    return GridComposer(rows=4, cols=1, figsize=figsize, main_title=main_title)

def create_custom_grid(rows, cols, figsize=None, main_title=None):
    """Create a custom grid with specified dimensions"""
    if figsize is None:
        figsize = (5 * cols, 4 * rows)  # Auto-calculate based on grid size
    return GridComposer(rows=rows, cols=cols, figsize=figsize, main_title=main_title)

print("🎼 GridComposer Initialized")