# plotbot/plotbot_interactive_options.py
# Options system for plotbot_interactive()

class PlotbotInteractiveOptions:
    """
    Options for controlling plotbot_interactive() behavior.
    
    Usage:
        from plotbot import pbi
        pbi.options.web_display = False  # Disable web interface, use matplotlib instead
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all options to defaults"""
        self.web_display = True  # True = separate browser, False = inline in Jupyter/VS Code
        
    def __repr__(self):
        return f"PlotbotInteractiveOptions(web_display={self.web_display})"

class EnhancedPlotbotInteractive:
    """Enhanced plotbot_interactive with options support, following plt.options pattern"""
    
    def __init__(self):
        # Add the options attribute
        self.options = PlotbotInteractiveOptions()

# Create global instance
pbi = EnhancedPlotbotInteractive()
