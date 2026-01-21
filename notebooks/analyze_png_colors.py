"""
Script to analyze color range in PNG images
Displays unique colors, RGB ranges, and color distribution statistics
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter

def analyze_png_colors(image_path):
    """
    Analyze the color range and distribution in a PNG image
    
    Args:
        image_path: Path to the PNG file
    """
    # Load the image
    img = Image.open(image_path)
    print(f"Image loaded: {image_path}")
    print(f"Image size: {img.size} (width x height)")
    print(f"Image mode: {img.mode}")
    print()
    
    # Convert to numpy array
    img_array = np.array(img)
    print(f"Array shape: {img_array.shape}")
    
    # Handle different image modes
    if len(img_array.shape) == 2:
        # Grayscale image
        print("\nGrayscale Image Analysis:")
        print(f"Value range: {img_array.min()} to {img_array.max()}")
        unique_values = np.unique(img_array)
        print(f"Number of unique values: {len(unique_values)}")
    else:
        # Color image (RGB or RGBA)
        print("\nColor Image Analysis:")
        
        # Get RGB channels (ignore alpha if present)
        if img_array.shape[2] >= 3:
            r_channel = img_array[:, :, 0]
            g_channel = img_array[:, :, 1]
            b_channel = img_array[:, :, 2]
            
            print(f"Red channel range: {r_channel.min()} to {r_channel.max()}")
            print(f"Green channel range: {g_channel.min()} to {g_channel.max()}")
            print(f"Blue channel range: {b_channel.min()} to {b_channel.max()}")
            
            if img_array.shape[2] == 4:
                a_channel = img_array[:, :, 3]
                print(f"Alpha channel range: {a_channel.min()} to {a_channel.max()}")
        
        # Reshape to get all pixels as rows
        pixels = img_array.reshape(-1, img_array.shape[2])
        
        # Get unique colors (only RGB, ignore alpha if present)
        rgb_pixels = pixels[:, :3]
        unique_colors = np.unique(rgb_pixels, axis=0)
        print(f"\nNumber of unique RGB colors: {len(unique_colors)}")
        
        # Display all unique RGB values
        print("\n" + "="*50)
        print("All Unique RGB Values:")
        print("="*50)
        for i, color in enumerate(unique_colors, 1):
            print(f"{i}. RGB({color[0]}, {color[1]}, {color[2]})")
        
        # Show most common colors
        print("\n" + "="*50)
        print("Most Common Colors (RGB):")
        print("="*50)
        pixel_tuples = [tuple(pixel[:3]) for pixel in pixels]
        color_counts = Counter(pixel_tuples)
        
        for i, (color, count) in enumerate(color_counts.most_common(10), 1):
            percentage = (count / len(pixel_tuples)) * 100
            print(f"{i}. RGB{color}: {count} pixels ({percentage:.2f}%)")
        
        # Analyze color distribution
        print("\n" + "="*50)
        print("Color Distribution Statistics:")
        print("="*50)
        
        r_values = pixels[:, 0]
        g_values = pixels[:, 1]
        b_values = pixels[:, 2]
        
        print(f"\nRed channel:")
        print(f"  Mean: {r_values.mean():.2f}")
        print(f"  Std: {r_values.std():.2f}")
        print(f"  Median: {np.median(r_values):.2f}")
        
        print(f"\nGreen channel:")
        print(f"  Mean: {g_values.mean():.2f}")
        print(f"  Std: {g_values.std():.2f}")
        print(f"  Median: {np.median(g_values):.2f}")
        
        print(f"\nBlue channel:")
        print(f"  Mean: {b_values.mean():.2f}")
        print(f"  Std: {b_values.std():.2f}")
        print(f"  Median: {np.median(b_values):.2f}")
        
        # Plot color histograms
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Original image
        axes[0, 0].imshow(img)
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')
        
        # Red channel histogram
        axes[0, 1].hist(r_values, bins=256, color='red', alpha=0.7, range=(0, 255))
        axes[0, 1].set_title('Red Channel Distribution')
        axes[0, 1].set_xlabel('Pixel Value')
        axes[0, 1].set_ylabel('Frequency')
        
        # Green channel histogram
        axes[1, 0].hist(g_values, bins=256, color='green', alpha=0.7, range=(0, 255))
        axes[1, 0].set_title('Green Channel Distribution')
        axes[1, 0].set_xlabel('Pixel Value')
        axes[1, 0].set_ylabel('Frequency')
        
        # Blue channel histogram
        axes[1, 1].hist(b_values, bins=256, color='blue', alpha=0.7, range=(0, 255))
        axes[1, 1].set_title('Blue Channel Distribution')
        axes[1, 1].set_xlabel('Pixel Value')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('color_analysis.png', dpi=150, bbox_inches='tight')
        print(f"\nColor distribution plot saved as 'color_analysis.png'")
        plt.show()
        
        # Create a color palette visualization
        if len(unique_colors) <= 256:
            fig, ax = plt.subplots(figsize=(12, 2))
            palette = unique_colors[:, :3] / 255.0  # Normalize to 0-1 for display
            palette_image = palette.reshape(1, -1, 3)
            ax.imshow(palette_image, aspect='auto', interpolation='nearest')
            ax.set_title(f'All Unique Colors ({len(unique_colors)} colors)')
            ax.axis('off')
            plt.tight_layout()
            plt.savefig('color_palette.png', dpi=150, bbox_inches='tight')
            print(f"Color palette saved as 'color_palette.png'")
            plt.show()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_png_colors.py <path_to_png_file>")
        print("\nExample:")
        print("  python analyze_png_colors.py data/raw/image.png")
    else:
        image_path = sys.argv[1]
        analyze_png_colors(image_path)
