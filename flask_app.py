from flask import Flask, render_template
import os
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__, static_folder='assets', static_url_path='/static_web')

# Configuration for different environments
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True


@app.route('/')
def index():
    #return render_template('welcome.html')
    return render_template('index.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


def fetch_climber_routes(url, max_retries=3, delay=0.3):
    """
    Fetch climbing routes from lezec.cz with retry logic.
    
    Args:
        url: URL to fetch data from
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        List of route dictionaries or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all table cells
            all_cells = soup.find_all(['td', 'th'])
            
            # Find the header row by looking for "Datum" cell
            header_index = None
            for i, cell in enumerate(all_cells):
                if cell.get_text(strip=True) == 'Datum':
                    header_index = i
                    break
            
            if header_index is None:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                return None
            
            # Verify we have the right headers
            expected_headers = ['Datum', 'Cesta', 'Oblast', 'Klas', 'Body', 'Styl', 'P']
            actual_headers = [all_cells[header_index + i].get_text(strip=True) 
                            for i in range(len(expected_headers))]
            
            if actual_headers != expected_headers:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                return None
            
            # Parse routes - data starts after the header row (7 cells)
            routes = []
            data_start = header_index + 7
            
            # Each route has 7 cells: Datum, Cesta (name), Oblast (sector), Klas (difficulty), Body, Styl (style), P
            for i in range(10):  # Get only first 10 routes
                route_start = data_start + (i * 7)
                
                # Check if we have enough cells
                if route_start + 6 >= len(all_cells):
                    break
                
                # Extract route data
                date = all_cells[route_start].get_text(strip=True)
                name = all_cells[route_start + 1].get_text(strip=True)
                sector = all_cells[route_start + 2].get_text(strip=True)
                difficulty = all_cells[route_start + 3].get_text(strip=True)
                style = all_cells[route_start + 5].get_text(strip=True)
                
                # Stop if we hit the "Celkem:" row or empty data
                if date == 'Celkem:' or not name:
                    break
                
                route = {
                    'date': date,
                    'name': name,
                    'sector': sector,
                    'difficulty': difficulty,
                    'style': style
                }
                routes.append(route)
            
            return routes if routes else None
            
        except (requests.RequestException, Exception) as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            else:
                print(f"Error fetching data after {max_retries} attempts: {e}")
                return None
    
    return None


@app.route('/prelezy')
def prelezy():
    """Route to display climbing routes for multiple climbers."""
    climbers_data = [
        {
            'name': 'Honza Koudelka',
            'url': 'https://lezec.cz/denik.php?parn=2&uid=486f6e7a61204b6f7564656c6b61h&ckat=2&crok=9992'
        },
        {
            'name': 'choodi',
            'url': 'https://lezec.cz/denik.php?parn=2&uid=63686f6f6469h&ckat=2&crok=9992'
        },
        {
            'name': 'seqa',
            'url': 'https://lezec.cz/denik.php?parn=2&uid=53657161h&ckat=2&crok=9992'
        },
        {
            'name': '_brouk_',
            'url': 'https://lezec.cz/denik.php?parn=2&uid=5f62726f756b5fh&ckat=2&crok=9992'
        }
    ]
    
    climbers = []
    for climber in climbers_data:
        routes = fetch_climber_routes(climber['url'])
        
        climber_info = {
            'name': climber['name'],
            'routes': routes if routes else [],
            'error': None if routes else 'Nepodařilo se načíst data po 3 pokusech'
        }
        climbers.append(climber_info)
    
    return render_template('routes.html', climbers=climbers)


if __name__ == '__main__':
    # For local development
    app.run(host='127.0.0.1', port=5000, debug=True)

# This is what PythonAnywhere will use
# No need to call app.run() for production
