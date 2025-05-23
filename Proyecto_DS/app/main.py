from flask import Flask, render_template
import webbrowser
import threading

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/areas')
def areas():
    return render_template('areas.html')

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/catalogos')
def catalogos():
    return render_template('catalogos.html')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run()
