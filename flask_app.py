from flask import Flask, render_template
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


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    # For local development
    app.run(host='127.0.0.1', port=5000, debug=True)

# This is what PythonAnywhere will use
# No need to call app.run() for production
