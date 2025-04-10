# Define a palette with more navy blue and a smooth transition to white
palette = [
    (0, 0, 0.5),             # Navy blue (lowest values)
    (0.1, 0.05, 0.4),        # Dark purplish-blue
    (0.3, 0.2, 0.5),         # Muted blue-purple
    (0.5, 0.3, 0.4),         # Dark ham pink
    (0.75, 0.45, 0.45),      # Medium ham pink
    (0.85, 0.6, 0.6),        # Light ham pink
    (0.95, 0.75, 0.75),      # Very light ham pink
    (1, 0.92, 0.92),         # Pale pink-white
    (1, 1, 1),               # White (highest values)
]

# Adjust the distribution to emphasize navy blue on the lower end
nodes = [
    0.0, 0.001, 0.4, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0
]

# Create the custom colormap with non-linear spacing
cmap1 = colors.LinearSegmentedColormap.from_list("navy_to_ham_white", list(zip(nodes, palette)), N=256)
# Define colors transitioning from navy blue to lighter blue, ham shades, and white
palette = [
    (0, 0, 0.5),             # Navy blue (lowest values)
    (0.2, 0.4, 0.8),         # Lighter blue
    (0.5, 0.7, 0.9),         # Very light blue
    (0.75, 0.45, 0.45),      # Medium ham pink
    (0.85, 0.6, 0.6),        # Light ham pink
    (0.95, 0.75, 0.75),      # Very light ham pink
    (1, 0.92, 0.92),         # Pale pink-white
    (1, 1, 1),               # Pure white (highest values)
]

# Adjust the distribution to emphasize transitions from blue to ham and then to white
nodes = [
    0.0, 0.2, 0.4, 0.6, 0.75, 0.85, 0.95, 1.0
]

# Create the custom colormap with non-linear spacing
cmap2 = colors.LinearSegmentedColormap.from_list("blue_to_ham_white", list(zip(nodes, palette)), N=256)
# Define colors transitioning from navy blue to purple, ham, and white
palette = [
    (0, 0, 0),                # Black
    (0, 0, 0.5),             # Navy blue (lowest values)
    (0.2, 0.1, 0.6),         # Dark purple
    (0.5, 0.3, 0.7),         # Medium purple
    (0.75, 0.5, 0.8),        # Soft lavender-purple
    (0.85, 0.6, 0.6),        # Light ham pink
    (0.95, 0.75, 0.75),      # Very light ham pink
    (1, 0.92, 0.92),         # Pale pink-white
    (1, 1, 1),               # Pure white (highest values)
]

# Adjust the distribution to emphasize navy, purple, and ham
nodes = [
    0.0, 0.01, 0.3, 0.5, 0.6, 0.75, 0.85, 0.95, 1.0
]

# Create the custom colormap with non-linear spacing
cmap3 = colors.LinearSegmentedColormap.from_list("navy_to_purple_ham_white", list(zip(nodes, palette)), N=256)
