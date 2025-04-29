import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from collections import Counter
import re

class BollywoodDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Bollywood Movies Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        self.df = None
        self.year_min = tk.IntVar(value=1950)
        self.year_max = tk.IntVar(value=2025)
        self.min_movies = tk.IntVar(value=1)  # Minimum number of movies by director
        self.selected_director = tk.StringVar(value="All Directors")  # Selected director
        self.setup_ui()
    
    def setup_ui(self):
        # Create header
        header_frame = tk.Frame(self.root, bg="#FF9933")
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="Bollywood Movies Analysis Dashboard", 
                 font=("Arial", 18, "bold"), bg="#FF9933", fg="white", pady=10).pack()
        
        # Create main content area
        content_frame = tk.Frame(self.root, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        left_panel = tk.Frame(content_frame, bg="#f0f0f0", width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Load data button
        tk.Button(left_panel, text="Load CSV File", command=self.load_csv,
                 bg="#138808", fg="white", font=("Arial", 12), padx=10, pady=5).pack(pady=10)
        
        # Year range selector
        year_frame = tk.LabelFrame(left_panel, text="Year Range", bg="#f0f0f0", font=("Arial", 12))
        year_frame.pack(pady=10, fill=tk.X)
        
        # Year range dropdown
        tk.Label(year_frame, text="From:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        year_min_values = list(range(1950, 2026, 5))
        self.year_min_dropdown = ttk.Combobox(year_frame, values=year_min_values, textvariable=self.year_min, width=6)
        self.year_min_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(year_frame, text="To:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5)
        year_max_values = list(range(1950, 2026, 5))
        self.year_max_dropdown = ttk.Combobox(year_frame, values=year_max_values, textvariable=self.year_max, width=6)
        self.year_max_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # Apply button for year range
        tk.Button(year_frame, text="Apply Filter", command=self.update_chart,
                 bg="#FF9933", fg="white", font=("Arial", 10)).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Director selection frame
        director_frame = tk.LabelFrame(left_panel, text="Director Filter", bg="#f0f0f0", font=("Arial", 12))
        director_frame.pack(pady=10, fill=tk.X)
        
        # Minimum movies slider
        tk.Label(director_frame, text="Min. Movies:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.min_movies_slider = tk.Scale(director_frame, from_=1, to=10, orient=tk.HORIZONTAL, 
                                          variable=self.min_movies, command=self.update_director_list)
        self.min_movies_slider.grid(row=0, column=1, padx=5, pady=5)
        
        # Director dropdown
        tk.Label(director_frame, text="Select Director:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5)
        self.director_dropdown = ttk.Combobox(director_frame, textvariable=self.selected_director, width=15)
        self.director_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # Apply button for director filter
        tk.Button(director_frame, text="Apply Director Filter", command=self.update_chart,
                 bg="#FF9933", fg="white", font=("Arial", 10)).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Chart selection
        tk.Label(left_panel, text="Select Chart:", bg="#f0f0f0", font=("Arial", 12)).pack(pady=(20, 5))
        
        charts = ["Movies by Year", "Genre Distribution", "Director Analysis", "Cast Network"]
        
        self.chart_var = tk.StringVar(value=charts[0])
        for chart in charts:
            tk.Radiobutton(left_panel, text=chart, variable=self.chart_var, value=chart,
                          bg="#f0f0f0", font=("Arial", 11), command=self.update_chart).pack(anchor=tk.W, pady=5)
        
        # Right panel for visualizations
        self.right_panel = tk.Frame(content_frame, bg="white", padx=10, pady=10)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message when no data is loaded
        self.message_label = tk.Label(self.right_panel, text="Please load a CSV file to begin analysis", 
                                    font=("Arial", 14), bg="white")
        self.message_label.pack(expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select Bollywood Movies CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return
            
        try:
            self.status_var.set("Loading data...")
            self.root.update()
            
            self.df = pd.read_csv(filepath)
            
            # Check if required columns exist
            required_columns = ['movie_id', 'movie_name', 'year', 'genre', 'director', 'cast']
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            
            if missing_columns:
                messagebox.showerror("Missing Columns", 
                                     f"The CSV file is missing these required columns: {', '.join(missing_columns)}")
                self.df = None
                self.status_var.set("Error loading data")
                return
                
            # Clean data
            if 'year' in self.df.columns:
                self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')
            
            # Update year range dropdowns
            if len(self.df) > 0:
                min_year = int(self.df['year'].min())
                max_year = int(self.df['year'].max())
                
                self.year_min.set(min_year)
                self.year_max.set(max_year)
                
                year_range = list(range(min_year, max_year + 1))
                self.year_min_dropdown['values'] = year_range
                self.year_max_dropdown['values'] = year_range
            
            # Initialize director dropdown
            self.update_director_list()
            
            self.message_label.pack_forget()
            self.status_var.set(f"Loaded {len(self.df)} movies")
            
            # Display first chart
            self.update_chart()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")
            self.status_var.set("Error loading data")
    
    def update_director_list(self, *args):
        if self.df is None:
            return
            
        try:
            # Count movies by director
            director_counts = self.df['director'].value_counts()
            
            # Filter by minimum number of movies
            min_movies = self.min_movies.get()
            qualified_directors = director_counts[director_counts >= min_movies].index.tolist()
            
            # Update dropdown values
            director_values = ["All Directors"] + sorted(qualified_directors)
            self.director_dropdown['values'] = director_values
            
            # Reset to "All Directors" if current selection is not in the list
            if self.selected_director.get() not in director_values:
                self.selected_director.set("All Directors")
                
            # Update status
            self.status_var.set(f"Found {len(qualified_directors)} directors with {min_movies}+ movies")
            
        except Exception as e:
            self.status_var.set(f"Error updating director list: {str(e)}")
    
    def clear_right_panel(self):
        for widget in self.right_panel.winfo_children():
            widget.destroy()
    
    def filter_by_year_range(self):
        if self.df is None:
            return None
            
        year_min = self.year_min.get()
        year_max = self.year_max.get()
        
        filtered_df = self.df[(self.df['year'] >= year_min) & (self.df['year'] <= year_max)]
        
        # Apply director filter if selected
        if self.selected_director.get() != "All Directors":
            filtered_df = filtered_df[filtered_df['director'] == self.selected_director.get()]
        
        return filtered_df
    
    def update_chart(self, *args):
        if self.df is None:
            return
            
        self.clear_right_panel()
        chart_type = self.chart_var.get()
        
        try:
            filtered_df = self.filter_by_year_range()
            if filtered_df.empty:
                tk.Label(self.right_panel, text="No data in selected range", 
                        font=("Arial", 14), bg="white").pack(expand=True)
                return
                
            if chart_type == "Movies by Year":
                self.plot_movies_by_year(filtered_df)
            elif chart_type == "Genre Distribution":
                self.plot_genre_distribution(filtered_df)
            elif chart_type == "Director Analysis":
                self.plot_director_analysis(filtered_df)
            elif chart_type == "Cast Network":
                self.plot_cast_analysis(filtered_df)
            
            # Update status with current filters
            director_info = f", Director: {self.selected_director.get()}" if self.selected_director.get() != "All Directors" else ""
            self.status_var.set(f"Displayed {chart_type} chart for years {self.year_min.get()}-{self.year_max.get()}{director_info}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create chart: {str(e)}")
            self.status_var.set(f"Error creating {chart_type} chart")
    
    def plot_movies_by_year(self, df):
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot data
        year_counts = df['year'].value_counts().sort_index()
        ax.plot(year_counts.index, year_counts.values, marker='o', linewidth=2, color='#FF9933')
        
        # Customize plot
        title = 'Number of Bollywood Movies Released by Year'
        if self.selected_director.get() != "All Directors":
            title = f'Movies by {self.selected_director.get()} by Year'
            
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Number of Movies', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Embed in tkinter
        self.embed_matplotlib_plot(fig)
        
        # Add summary statistics
        stats_frame = tk.Frame(self.right_panel, bg="white")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Calculate statistics
        total_movies = len(df)
        year_range = f"{int(df['year'].min())} to {int(df['year'].max())}" if not df.empty else "N/A"
        
        if not year_counts.empty:
            peak_year = year_counts.idxmax()
            peak_count = year_counts.max()
            peak_info = f"Peak Year: {peak_year} ({peak_count} movies)"
        else:
            peak_info = "Peak Year: N/A"
        
        # Display statistics
        tk.Label(stats_frame, text=f"Total Movies: {total_movies}", 
                bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=20)
        tk.Label(stats_frame, text=f"Year Range: {year_range}", 
                bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=20)
        tk.Label(stats_frame, text=peak_info, 
                bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=20)
    
    def plot_genre_distribution(self, df):
        # Extract all genres
        all_genres = []
        for genres in df['genre'].dropna():
            # Split genres (assuming they're comma or pipe separated)
            genre_list = re.split(r'[,|]', genres)
            all_genres.extend([g.strip() for g in genre_list])
        
        # Count genres
        genre_counts = Counter(all_genres)
        top_genres = dict(genre_counts.most_common(10))
        
        if not top_genres:
            tk.Label(self.right_panel, text="No genre data available for the selected filters", 
                    font=("Arial", 14), bg="white").pack(expand=True)
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            top_genres.values(), 
            labels=top_genres.keys(),
            autopct='%1.1f%%',
            startangle=90,
            explode=[0.05] * len(top_genres),
            shadow=True,
            colors=plt.cm.Paired(range(len(top_genres)))
        )
        
        # Style the chart
        plt.setp(autotexts, size=9, weight="bold")
        
        title = 'Top 10 Bollywood Movie Genres'
        if self.selected_director.get() != "All Directors":
            title = f'Genres in {self.selected_director.get()} Movies'
            
        ax.set_title(title, fontsize=16)
        plt.tight_layout()
        
        # Embed in tkinter
        self.embed_matplotlib_plot(fig)
    
    def plot_director_analysis(self, df):
        if self.selected_director.get() != "All Directors":
            # Show movies by this director over time
            director_df = df[df['director'] == self.selected_director.get()]
            
            # Group by year
            movies_by_year = director_df['year'].value_counts().sort_index()
            
            if movies_by_year.empty:
                tk.Label(self.right_panel, text=f"No data available for director: {self.selected_director.get()}", 
                        font=("Arial", 14), bg="white").pack(expand=True)
                return
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create bar chart
            ax.bar(movies_by_year.index, movies_by_year.values, color='#138808')
            
            # Add labels
            ax.set_title(f'Movies by {self.selected_director.get()} Over Time', fontsize=16)
            ax.set_xlabel('Year', fontsize=12)
            ax.set_ylabel('Number of Movies', fontsize=12)
            
            # Adjust layout
            plt.tight_layout()
            
            # Embed in tkinter
            self.embed_matplotlib_plot(fig)
            
            # Add movie list
            movie_list_frame = tk.Frame(self.right_panel, bg="white")
            movie_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Create scrollable list
            tk.Label(movie_list_frame, text=f"Movies by {self.selected_director.get()}:", 
                    font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, pady=(0, 10))
            
            # Create scrollable list
            list_frame = tk.Frame(movie_list_frame, bg="white")
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            movie_listbox = tk.Listbox(list_frame, width=70, height=10, 
                                      font=("Arial", 11), yscrollcommand=scrollbar.set)
            movie_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=movie_listbox.yview)
            
            # Add movies to list
            for _, movie in director_df.sort_values('year').iterrows():
                movie_text = f"{int(movie['year'])} - {movie['movie_name']}"
                movie_listbox.insert(tk.END, movie_text)
            
        else:
            # Count movies by director
            director_counts = df['director'].value_counts().head(10)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create horizontal bar chart
            bars = ax.barh(director_counts.index, director_counts.values, color='#138808', alpha=0.8)
            
            # Add labels
            ax.set_title('Top 10 Bollywood Directors by Number of Movies', fontsize=16)
            ax.set_xlabel('Number of Movies', fontsize=12)
            ax.set_ylabel('Director', fontsize=12)
            
            # Add value labels
            for i, v in enumerate(director_counts.values):
                ax.text(v + 0.1, i, str(v), va='center')
            
            # Adjust layout
            plt.tight_layout()
            
            # Embed in tkinter
            self.embed_matplotlib_plot(fig)
    
    def plot_cast_analysis(self, df):
        # Extract top actors
        all_actors = []
        for cast in df['cast'].dropna():
            # Split cast (assuming they're comma or pipe separated)
            actor_list = re.split(r'[,|]', cast)
            all_actors.extend([a.strip() for a in actor_list])
        
        # Count actors
        actor_counts = Counter(all_actors)
        top_actors = dict(actor_counts.most_common(10))
        
        if not top_actors:
            tk.Label(self.right_panel, text="No cast data available for the selected filters", 
                    font=("Arial", 14), bg="white").pack(expand=True)
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar chart
        x = range(len(top_actors))
        bars = ax.bar(x, top_actors.values(), width=0.7, color=plt.cm.tab10(range(len(top_actors))))
        
        # Add labels
        title = 'Top 10 Bollywood Actors by Movie Appearances'
        if self.selected_director.get() != "All Directors":
            title = f'Top Actors in {self.selected_director.get()} Movies'
            
        ax.set_title(title, fontsize=16)
        ax.set_ylabel('Number of Movies', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(top_actors.keys(), rotation=45, ha='right')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.0f}', ha='center', va='bottom')
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed in tkinter
        self.embed_matplotlib_plot(fig)
    
    def embed_matplotlib_plot(self, figure):
        # Create canvas
        canvas = FigureCanvasTkAgg(figure, master=self.right_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = BollywoodDashboard(root)
    root.mainloop()
