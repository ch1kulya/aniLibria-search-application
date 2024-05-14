import customtkinter as ctk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import requests
from PIL import Image, ImageTk
import io

class AniLibriaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AniLibria Search")
        self.geometry("1000x800")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.create_widgets()

    def create_widgets(self):
        self.search_label = ctk.CTkLabel(self, text="Search Anime:")
        self.search_label.pack(pady=10)
        
        self.search_entry = ctk.CTkEntry(self, width=400)
        self.search_entry.pack(pady=5)
        
        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_anime)
        self.search_button.pack(pady=10)
        
        self.results_frame = ctk.CTkScrollableFrame(self, width=980, height=600)
        self.results_frame.pack(pady=20, fill=ctk.BOTH, expand=True)
        
    def search_anime(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Input error", "Please enter a search query")
            return
        
        try:
            response = requests.get(f"https://api.anilibria.tv/v2/searchTitles?search={query}")
            response.raise_for_status()
            data = response.json()
            self.display_results(data)
        except requests.RequestException as e:
            messagebox.showerror("API Error", f"An error occurred: {e}")
    
    def display_results(self, data):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        for anime in data:
            anime_id = anime.get("id", "N/A")
            anime_name = anime.get("names", {}).get("en", "N/A")
            anime_year = anime.get("season", {}).get("year", "N/A")
            anime_type = anime.get("type", {}).get("full_string", "N/A")
            
            anime_frame = ctk.CTkFrame(self.results_frame)
            anime_frame.pack(pady=10, padx=10, fill=ctk.X)
            
            result_label = ctk.CTkLabel(anime_frame, text=f"{anime_name} ({anime_year}) [{anime_type}]")
            result_label.pack(side=ctk.LEFT, padx=10)
            
            view_button = ctk.CTkButton(anime_frame, text="View Details", command=lambda id=anime_id: self.on_item_double_click(id))
            view_button.pack(side=ctk.RIGHT, padx=10)
    
    def on_item_double_click(self, anime_id):
        self.show_anime_details(anime_id)
    
    def show_anime_details(self, anime_id):
        try:
            response = requests.get(f"https://api.anilibria.tv/v2/getTitle?id={anime_id}")
            response.raise_for_status()
            data = response.json()
            self.display_anime_details(data)
        except requests.RequestException as e:
            messagebox.showerror("API Error", f"An error occurred: {e}")
    
    def display_anime_details(self, data):
        # Get the position of the main window
        main_window_x = self.winfo_x()
        main_window_y = self.winfo_y()
        main_window_width = self.winfo_width()
        
        # Calculate the position for the details window
        details_window_x = main_window_x + main_window_width + 10
        details_window_y = main_window_y

        details_window = ctk.CTkToplevel(self)
        details_window.title(data["names"]["en"])
        details_window.geometry(f"1000x800+{details_window_x}+{details_window_y}")
        
        details_frame = ctk.CTkFrame(details_window)
        details_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Main frame to hold banner and description side by side
        main_frame = ctk.CTkFrame(details_frame)
        main_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Poster
        poster_frame = ctk.CTkFrame(main_frame)
        poster_frame.pack(side=ctk.LEFT, padx=10, pady=10)
        
        if "posters" in data and "original" in data["posters"]:
            poster_url = "https://www.anilibria.tv" + data["posters"]["original"]["url"]
            poster_image = self.get_image_from_url(poster_url)
            if poster_image:
                poster_label = ctk.CTkLabel(poster_frame, image=poster_image)
                poster_label.pack(pady=5)
        
        # Title
        title_label = ctk.CTkLabel(poster_frame, text=f"Title: {data['names']['en']}", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=5)
        
        # Description
        description_frame = ctk.CTkFrame(main_frame)
        description_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        description_label = ctk.CTkLabel(description_frame, text="Description:", font=ctk.CTkFont(size=14, weight="bold"))
        description_label.pack(pady=5)
        
        description_text = ScrolledText(description_frame, wrap=ctk.WORD, height=10)
        description_text.insert(ctk.END, data['description'])
        description_text.config(state=ctk.DISABLED)
        description_text.pack(pady=5, fill=ctk.BOTH, expand=True)
        
        # Download links
        if "torrents" in data and "list" in data["torrents"]:
            torrents_label = ctk.CTkLabel(description_frame, text="Download Links:", font=ctk.CTkFont(size=14, weight="bold"))
            torrents_label.pack(pady=5)
            
            torrents_text = ScrolledText(description_frame, wrap=ctk.WORD, height=5)
            torrents_text.config(state=ctk.NORMAL)
            for torrent in data["torrents"]["list"]:
                torrents_text.insert(ctk.END, f"{torrent['quality']['string']} - {torrent['url']}\n")
            torrents_text.config(state=ctk.DISABLED)
            torrents_text.pack(pady=5, fill=ctk.BOTH, expand=True)
        
        # Player links
        if "player" in data:
            player_label = ctk.CTkLabel(details_frame, text="Player Links:", font=ctk.CTkFont(size=14, weight="bold"))
            player_label.pack(pady=5)
            
            player_text = ScrolledText(details_frame, wrap=ctk.WORD, height=5)
            player_text.config(state=ctk.NORMAL)
            for ep_num, ep_info in data["player"]["playlist"].items():
                ep_link = f"//{data['player']['host']}{ep_info['hls']['hd']}"
                player_text.insert(ctk.END, f"Episode {ep_num}: {ep_link}\n")
            player_text.config(state=ctk.DISABLED)
            player_text.pack(pady=5, fill=ctk.BOTH, expand=True)
    
    def get_image_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((300, 450), Image.LANCZOS)
            return ctk.CTkImage(light_image=image, dark_image=image, size=(300, 450))
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

if __name__ == "__main__":
    app = AniLibriaApp()
    app.mainloop()
