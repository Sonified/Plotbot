#!/usr/bin/env python3
"""
Simple test script to validate the GridComposer system works.
This creates a basic grid without requiring complex data setup.
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Add plotbot to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Import the new grid composer
from plotbot.grid_composer import GridComposer, create_2x2_grid

def create_test_plot(*args, **kwargs):
    """Simple test function that creates a basic matplotlib plot"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Generate some test data
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(0, 0.1, 100)
    
    ax.plot(x, y, 'b-', linewidth=2, label='Test Data')
    ax.set_xlabel('X Values')
    ax.set_ylabel('Y Values')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig, ax

def create_scatter_plot(*args, **kwargs):
    """Test function that creates a scatter plot"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Generate test scatter data
    x = np.random.normal(0, 1, 50)
    y = 2 * x + np.random.normal(0, 0.5, 50)
    
    ax.scatter(x, y, c='red', alpha=0.6, s=30)
    ax.set_xlabel('X Values')
    ax.set_ylabel('Y Values')
    ax.grid(True, alpha=0.3)
    
    return fig, ax

def test_basic_grid():
    """Test basic 2x2 grid functionality"""
    print("🧪 Testing basic 2x2 grid...")
    
    # Create a 2x2 grid
    composer = create_2x2_grid(figsize=(12, 10), main_title="Grid Composer Test")
    
    # Add test plots
    composer.add_plot(
        name='plot1',
        function=create_test_plot,
        row=0, col=0,
        title="Test Plot 1"
    )
    
    composer.add_plot(
        name='plot2', 
        function=create_test_plot,
        row=0, col=1,
        title="Test Plot 2"
    )
    
    composer.add_plot(
        name='scatter1',
        function=create_scatter_plot,
        row=1, col=0,
        title="Scatter Plot 1"
    )
    
    composer.add_plot(
        name='scatter2',
        function=create_scatter_plot, 
        row=1, col=1,
        title="Scatter Plot 2"
    )
    
    # Compose the grid
    final_fig = composer.compose()
    
    # Save the result
    output_file = 'test_grid_output.png'
    final_fig.savefig(output_file, bbox_inches='tight', dpi=150)
    print(f"✅ Grid composition successful! Saved to {output_file}")
    
    # Show the plot
    plt.show()
    
    return final_fig

def test_custom_grid():
    """Test custom grid with spanning"""
    print("🧪 Testing custom grid with spanning...")
    
    # Create a 2x3 grid
    composer = GridComposer(rows=2, cols=3, figsize=(15, 8), 
                           main_title="Custom Grid Test")
    
    # Large plot spanning 2 columns
    composer.add_plot(
        name='large_plot',
        function=create_test_plot,
        row=0, col=0, colspan=2,
        title="Large Plot (2 cols)"
    )
    
    # Small plot in top right
    composer.add_plot(
        name='small_plot',
        function=create_scatter_plot,
        row=0, col=2,
        title="Small Plot"
    )
    
    # Bottom row plots
    for i in range(3):
        composer.add_plot(
            name=f'bottom_{i}',
            function=create_scatter_plot,
            row=1, col=i,
            title=f"Bottom {i+1}"
        )
    
    # Compose and save
    custom_fig = composer.compose()
    custom_output = 'test_custom_grid.png'
    custom_fig.savefig(custom_output, bbox_inches='tight', dpi=150)
    print(f"✅ Custom grid successful! Saved to {custom_output}")
    
    plt.show()
    
    return custom_fig

if __name__ == "__main__":
    print("🎼 Starting GridComposer Tests...\n")
    
    try:
        # Test basic functionality
        basic_fig = test_basic_grid()
        print("")
        
        # Test custom grid
        custom_fig = test_custom_grid()
        print("")
        
        print("🎉 All tests completed successfully!")
        print("📁 Check the generated PNG files to see the results.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()