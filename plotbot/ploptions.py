# Plotbot Options - Global configuration for figure behavior
"""
Global options class for controlling plotbot figure behavior.
Similar to audifier pattern - simple, direct property access.
"""

class PlotbotOptions:
    """Global options for controlling plotbot figure behavior."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all options to defaults."""
        self.return_figure = True     # Whether plotting functions return the figure object
        self.display_figure = False   # Whether to display the figure (plt.show())
        
    def __repr__(self):
        return (f"PlotbotOptions(return_figure={self.return_figure}, "
                f"display_figure={self.display_figure})")

# Create global instance
ploptions = PlotbotOptions()

print('🎛️ initialized ploptions')
