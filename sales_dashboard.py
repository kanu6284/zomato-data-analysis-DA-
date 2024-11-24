import pygame
import sys
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Initialize Pygame
pygame.init()

# Set up screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sales Data Visualization Dashboard")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Function to display text
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# Function to plot restaurant votes data
def plot_sales_data():
    data = pd.read_csv('Zomato data .csv')  # Correct file path
    
    # Set up seaborn style for a cleaner look
    sns.set(style="whitegrid")
    
    # Create a larger figure to handle many labels
    plt.figure(figsize=(15, 8))
    
    # Plot with better readability and style
    sns.barplot(x='name', y='votes', data=data, palette="Blues_d")
    
    # Improve x-axis labels
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=10)
    plt.xlabel("Restaurant Name", fontsize=12)
    plt.ylabel("Votes", fontsize=12)
    
    # Add title and tighten layout
    plt.title("Votes for Restaurants", fontsize=16)
    plt.tight_layout()
    
    # Save the plot to an image
    plt.savefig('C:/Users/bkani/OneDrive/文档/Desktop/Sales_Visualization/votes_plot_cleaned.png')  # Updated path

    # Load the plot image into Pygame
    plot_image = pygame.image.load('C:/Users/bkani/OneDrive/文档/Desktop/Sales_Visualization/votes_plot_cleaned.png')  # Updated path
    return plot_image

# Main loop
def main():
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()
    
    # Plot sales data and load it as a Pygame image
    sales_plot = plot_sales_data()

    while True:
        screen.fill(WHITE)
        
        draw_text('Restaurant Votes Dashboard', font, BLACK, screen, 20, 20)

        # Display sales plot
        screen.blit(sales_plot, (50, 100))  # Adjust as needed for positioning

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()
