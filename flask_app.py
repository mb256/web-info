from flask import Flask, render_template, request, redirect, url_for
import os

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


@app.route('/route')
def route():
    return render_template('route.html')


@app.route('/search', methods=['POST'])
def search_route():
    route_name = request.form.get('route_name')
    if route_name:
        # TODO:
        # Here you can add your search logic
        # For now, we'll just pass the search term to a results template
        return render_template('route.html', search_query=route_name, show_results=True)
    else:
        return redirect(url_for('route'))



if __name__ == '__main__':
    # For local development
    app.run(host='127.0.0.1', port=5000, debug=True)

# This is what PythonAnywhere will use
# No need to call app.run() for production
