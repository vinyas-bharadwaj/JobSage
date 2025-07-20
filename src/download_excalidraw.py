# Create this file: src/download_excalidraw.py
import requests
import os

def download_excalidraw_assets():
    """Download Excalidraw assets for self-hosting"""
    
    base_url = "https://unpkg.com/@excalidraw/excalidraw@0.17.6/dist/"
    static_dir = "static/js/excalidraw/"
    
    files_to_download = [
        "excalidraw.production.min.js",
        "excalidraw.development.js",  # For development
    ]
    
    css_files = [
        "https://unpkg.com/@excalidraw/excalidraw@0.17.6/dist/excalidraw.css"
    ]
    
    # Create directories if they don't exist
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs("static/css/excalidraw/", exist_ok=True)
    
    # Download JS files
    for file in files_to_download:
        url = base_url + file
        print(f"Downloading {url}...")
        
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(static_dir, file), 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded {file}")
        else:
            print(f"✗ Failed to download {file}")
    
    # Download CSS files
    for css_url in css_files:
        filename = css_url.split('/')[-1]
        print(f"Downloading {css_url}...")
        
        response = requests.get(css_url)
        if response.status_code == 200:
            with open(f"static/css/excalidraw/{filename}", 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded {filename}")
        else:
            print(f"✗ Failed to download {filename}")
    
    # Download React dependencies
    react_files = [
        ("https://unpkg.com/react@18/umd/react.production.min.js", "react.min.js"),
        ("https://unpkg.com/react-dom@18/umd/react-dom.production.min.js", "react-dom.min.js")
    ]
    
    for url, filename in react_files:
        print(f"Downloading {url}...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(static_dir, filename), 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded {filename}")

if __name__ == "__main__":
    download_excalidraw_assets()