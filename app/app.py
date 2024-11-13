from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# set app to debug mode makes it so that you can serve the application by running `python app.py` via terminal
if __name__ == '__main__':
    app.run(debug=True)