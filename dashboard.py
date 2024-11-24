import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
import re
from fuzzywuzzy import fuzz
from tkinter import font as tkfont

# Load the data
df = pd.read_csv('Zomato data .csv')
print(df.head())  # Add this line to check if data is loaded
print(df.columns)  # This will show us what columns are actually in the dataset

# Convert 'rate' column to float
df['rate'] = df['rate'].apply(lambda x: float(str(x).split('/')[0]) if isinstance(x, str) else x)

# Create the main window
root = tk.Tk()
root.title("Zomato Data Analysis Dashboard")
root.geometry("1200x700")
root.configure(bg='#f0f0f0')

# Create header
header = tk.Frame(root, bg='#2c3e50', height=60)
header.pack(side='top', fill='x')
header_label = tk.Label(header, text="Zomato Analysis Dashboard", bg='#2c3e50', fg='white', font=("Arial", 18, "bold"))
header_label.pack(pady=10)

# Create main content area
content_area = tk.Frame(root, bg='#f0f0f0')
content_area.pack(side='top', fill='both', expand=True)

# Create sidebar
sidebar = tk.Frame(content_area, width=250, bg='#34495e', bd=2, relief=tk.RAISED)
sidebar.pack(side='left', fill='y')
sidebar.pack_propagate(False)

# Create a custom font for the sidebar buttons
sidebar_font = tkfont.Font(family="Arial", size=14, weight="bold")

# Add sidebar options
options = [
    'Restaurant Types',
    'Votes Distribution',
    'Rating Distribution',
    'Online vs Offline Orders',
    'Average Cost for Two',
    'Top Rated Restaurants',
    'Price Range Distribution',
    'Correlation Heatmap',
    'Data Query'
]
option_var = tk.StringVar(value=options[0])

for option in options:
    button = tk.Button(sidebar, text=option, font=sidebar_font, bg='#2c3e50', fg='white',
                       activebackground='#3498db', activeforeground='white', bd=0,
                       command=lambda o=option: option_var.set(o),
                       width=20, height=2, relief=tk.RAISED, borderwidth=2,
                       highlightthickness=2, highlightbackground='#1f2c38',
                       highlightcolor='#3498db')
    button.pack(fill='x', padx=10, pady=5)

# Add a refresh button
refresh_button = tk.Button(sidebar, text="Refresh Data", font=sidebar_font, bg='#2c3e50', fg='white',
                           activebackground='#3498db', activeforeground='white', bd=0,
                           command=lambda: update_content(),
                           width=20, height=2, relief=tk.RAISED, borderwidth=2,
                           highlightthickness=2, highlightbackground='#1f2c38',
                           highlightcolor='#3498db')
refresh_button.pack(side='bottom', pady=20, padx=10, fill='x')

# Create main content frame
main_content = tk.Frame(content_area, bg='white')
main_content.pack(side='right', fill='both', expand=True)

# Function to clear the main content area
def clear_content():
    for widget in main_content.winfo_children():
        widget.destroy()

# Function to plot restaurant types
def plot_restaurant_types():
    clear_content()
    fig, ax = plt.subplots(figsize=(10, 6))
    restaurant_counts = df['listed_in(type)'].value_counts()
    plt.pie(restaurant_counts, labels=restaurant_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title("Distribution of Restaurant Types")
    plt.axis('equal')
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

# Function to plot votes distribution
def plot_votes_distribution():
    clear_content()
    fig, ax = plt.subplots(figsize=(12, 6))
    df_sorted = df.sort_values(by='votes', ascending=False).head(20)
    sns.barplot(x='name', y='votes', data=df_sorted, ax=ax)
    ax.set_title('Top 20 Restaurants by Votes')
    ax.set_xlabel('Restaurant Name')
    ax.set_ylabel('Votes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

# Function to plot rating distribution
def plot_rating_distribution():
    clear_content()
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.hist(df['rate'], bins=20)
    plt.title("Ratings Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Frequency")
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

# Function to plot online vs offline orders
def plot_online_vs_offline():
    clear_content()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='online_order', y='rate', data=df, ax=ax)
    ax.set_title('Online vs Offline Orders - Ratings')
    ax.set_xlabel('Online Order')
    ax.set_ylabel('Rating')
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

# Function to plot average cost for two
def plot_average_cost():
    clear_content()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df['approx_cost(for two people)'], bins=30, kde=True, ax=ax)
    ax.set_title('Distribution of Approximate Cost for Two People')
    ax.set_xlabel('Cost')
    
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

# Function to plot top rated restaurants
def plot_top_rated():
    clear_content()
    fig, ax = plt.subplots(figsize=(12, 6))
    top_rated = df.sort_values(by='rate', ascending=False).head(10)
    sns.barplot(x='name', y='rate', data=top_rated, ax=ax)
    ax.set_title('Top 10 Rated Restaurants')
    ax.set_xlabel('Restaurant Name')
    ax.set_ylabel('Rating')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

# New plot functions

def plot_cuisine_wordcloud():
    clear_content()
    if 'cuisines' not in df.columns:
        tk.Label(main_content, text="Cuisine data not available in the dataset").pack()
        return
    print(df['cuisines'].value_counts())  # Keep this for debugging
    text = ' '.join(df['cuisines'].dropna())
    if not text:
        tk.Label(main_content, text="No cuisine data available").pack()
        return
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Cuisine Word Cloud', fontsize=16)
    
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

def plot_location_analysis():
    clear_content()
    if 'location' not in df.columns:
        tk.Label(main_content, text="Location data not available in the dataset").pack()
        return
    print(df['location'].value_counts())  # Keep this for debugging
    top_locations = df['location'].value_counts().head(10)
    if top_locations.empty:
        tk.Label(main_content, text="No location data available").pack()
        return
    # ... rest of the function

def plot_price_range_distribution():
    clear_content()
    df['price_range'] = pd.cut(df['approx_cost(for two people)'], bins=[0, 500, 1000, 1500, 2000, np.inf], labels=['0-500', '501-1000', '1001-1500', '1501-2000', '2000+'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x='price_range', data=df, ax=ax)
    ax.set_title('Price Range Distribution', fontsize=16)
    ax.set_xlabel('Price Range (for two people)')
    ax.set_ylabel('Number of Restaurants')
    
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

def plot_correlation_heatmap():
    clear_content()
    numeric_df = df[['rate', 'votes', 'approx_cost(for two people)']]
    corr = numeric_df.corr()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Correlation Heatmap', fontsize=16)
    
    canvas = FigureCanvasTkAgg(fig, master=main_content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

def create_data_query_page():
    clear_content()
    
    query_frame = tk.Frame(main_content, bg='white')
    query_frame.pack(pady=20, padx=20, fill='x')
    
    query_label = tk.Label(query_frame, text="Enter your question about the Zomato data:", 
                           bg='white', font=("Arial", 12, "bold"))
    query_label.pack(side='top', pady=(0, 10))
    
    query_entry = tk.Entry(query_frame, width=50, font=("Arial", 11))
    query_entry.pack(side='left', expand=True, fill='x')
    
    query_button = tk.Button(query_frame, text="Submit", command=lambda: process_query(query_entry.get()),
                             bg='#3498db', fg='white', font=("Arial", 11, "bold"), 
                             activebackground='#2980b9', activeforeground='white')
    query_button.pack(side='right', padx=(10, 0))
    
    global result_frame
    result_frame = tk.Frame(main_content, bg='white')
    result_frame.pack(pady=20, padx=20, fill='both', expand=True)

def process_query(query):
    clear_frame(result_frame)
    
    # Normalize the query
    query = query.lower()
    
    # Define keyword mappings
    keyword_mappings = {
        'top rated': ['top', 'best', 'highest rated'],
        'online vs offline': ['online', 'offline', 'delivery'],
        'cost': ['price', 'expensive', 'cheap'],
        'type': ['category', 'cuisine'],
        'rating': ['rate', 'score'],
        'votes': ['popular', 'likes'],
        'location': ['area', 'place'],
        'book table': ['reservation', 'booking'],
    }
    
    # Function to check for keyword matches
    def keyword_match(keywords):
        return any(fuzz.partial_ratio(keyword, query) > 80 for keyword in keywords)
    
    # Determine the type of analysis based on the query
    if keyword_match(keyword_mappings['top rated']):
        plot_top_rated_restaurants()
    elif keyword_match(keyword_mappings['online vs offline']):
        plot_online_vs_offline_orders()
    elif keyword_match(keyword_mappings['cost']):
        plot_cost_analysis()
    elif keyword_match(keyword_mappings['type']):
        plot_restaurant_types()
    elif keyword_match(keyword_mappings['rating']):
        plot_rating_analysis()
    elif keyword_match(keyword_mappings['votes']):
        plot_votes_analysis()
    elif keyword_match(keyword_mappings['location']):
        plot_location_analysis()
    elif keyword_match(keyword_mappings['book table']):
        plot_book_table_analysis()
    else:
        tk.Label(result_frame, text="I'm sorry, I couldn't understand your query. Please try again with a different question.", bg='white', wraplength=500).pack(pady=20)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# Modify these plotting functions to work with the result_frame
def plot_top_rated_restaurants():
    fig, ax = plt.subplots(figsize=(10, 6))
    top_rated = df.sort_values(by='rate', ascending=False).head(10)
    sns.barplot(x='name', y='rate', data=top_rated, ax=ax)
    ax.set_title('Top 10 Rated Restaurants')
    ax.set_xlabel('Restaurant Name')
    ax.set_ylabel('Rating')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=result_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    explanation = "This chart shows the top 10 highest-rated restaurants in the Zomato dataset."
    tk.Label(result_frame, text=explanation, bg='white', wraplength=500).pack(pady=10)

# New plotting functions

def plot_cost_analysis():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Histogram of costs
    sns.histplot(df['approx_cost(for two people)'], bins=30, kde=True, ax=ax1)
    ax1.set_title('Distribution of Costs for Two People')
    ax1.set_xlabel('Cost')
    ax1.set_ylabel('Frequency')
    
    # Scatter plot of cost vs rating
    sns.scatterplot(x='approx_cost(for two people)', y='rate', data=df, ax=ax2)
    ax2.set_title('Cost vs Rating')
    ax2.set_xlabel('Cost for Two People')
    ax2.set_ylabel('Rating')
    
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=result_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    explanation = "The left chart shows the distribution of costs for two people. The right chart shows the relationship between cost and rating."
    tk.Label(result_frame, text=explanation, bg='white', wraplength=500).pack(pady=10)

def plot_rating_analysis():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Rating distribution
    sns.histplot(df['rate'], bins=20, kde=True, ax=ax1)
    ax1.set_title('Distribution of Ratings')
    ax1.set_xlabel('Rating')
    ax1.set_ylabel('Frequency')
    
    # Top 10 highest rated restaurants
    top_rated = df.sort_values('rate', ascending=False).head(10)
    sns.barplot(x='rate', y='name', data=top_rated, ax=ax2)
    ax2.set_title('Top 10 Highest Rated Restaurants')
    ax2.set_xlabel('Rating')
    ax2.set_ylabel('Restaurant Name')
    
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=result_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    explanation = "The left chart shows the distribution of ratings. The right chart shows the top 10 highest rated restaurants."
    tk.Label(result_frame, text=explanation, bg='white', wraplength=500).pack(pady=10)

def plot_votes_analysis():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Votes distribution
    sns.histplot(df['votes'], bins=30, kde=True, ax=ax1)
    ax1.set_title('Distribution of Votes')
    ax1.set_xlabel('Number of Votes')
    ax1.set_ylabel('Frequency')
    ax1.set_xscale('log')
    
    # Top 10 most voted restaurants
    top_voted = df.sort_values('votes', ascending=False).head(10)
    sns.barplot(x='votes', y='name', data=top_voted, ax=ax2)
    ax2.set_title('Top 10 Most Voted Restaurants')
    ax2.set_xlabel('Number of Votes')
    ax2.set_ylabel('Restaurant Name')
    
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=result_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    explanation = "The left chart shows the distribution of votes (log scale). The right chart shows the top 10 restaurants with the most votes."
    tk.Label(result_frame, text=explanation, bg='white', wraplength=500).pack(pady=10)

def plot_book_table_analysis():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Pie chart of book table options
    book_table_counts = df['book_table'].value_counts()
    ax1.pie(book_table_counts, labels=book_table_counts.index, autopct='%1.1f%%')
    ax1.set_title('Proportion of Restaurants Offering Table Booking')
    
    # Comparison of ratings for restaurants with and without table booking
    sns.boxplot(x='book_table', y='rate', data=df, ax=ax2)
    ax2.set_title('Ratings for Restaurants With and Without Table Booking')
    ax2.set_xlabel('Table Booking Available')
    ax2.set_ylabel('Rating')
    
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=result_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    explanation = "The left chart shows the proportion of restaurants offering table booking. The right chart compares ratings for restaurants with and without table booking."
    tk.Label(result_frame, text=explanation, bg='white', wraplength=500).pack(pady=10)

# Define update_content function
def update_content(*args):
    selected_option = option_var.get()
    if selected_option == 'Restaurant Types':
        plot_restaurant_types()
    elif selected_option == 'Votes Distribution':
        plot_votes_distribution()
    elif selected_option == 'Rating Distribution':
        plot_rating_distribution()
    elif selected_option == 'Online vs Offline Orders':
        plot_online_vs_offline()
    elif selected_option == 'Average Cost for Two':
        plot_average_cost()
    elif selected_option == 'Top Rated Restaurants':
        plot_top_rated()
    elif selected_option == 'Price Range Distribution':
        plot_price_range_distribution()
    elif selected_option == 'Correlation Heatmap':
        plot_correlation_heatmap()
    elif selected_option == 'Data Query':
        create_data_query_page()

# Apply a modern theme to the Tkinter widgets
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Arial', 11, 'bold'))
style.configure('TEntry', font=('Arial', 11))

# Add footer
footer = tk.Frame(root, height=30, bg='#2c3e50')
footer.pack(side='bottom', fill='x')
footer_label = tk.Label(footer, text="© 2024 Zomato Data Analysis Dashboard", bg='#2c3e50', fg='white')
footer_label.pack(pady=5)

# Initial content update
update_content()

# Start the Tkinter main loop
root.mainloop()
