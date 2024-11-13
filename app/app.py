from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
# current task is to just display user information associated to current session
def index():
    return render_template('index.html')

# if login info matches to an account in the db, user logs in
@app.route('/login')
def login():
    pass

# clear session cookie
@app.route('/logout')
def logout():
    pass

# create a user object and redirect to login
@app.route('/register')
def register():
    pass

# set app to debug mode makes it so that you can serve the application by running `python app.py` via terminal
if __name__ == '__main__':
    app.run(debug=True)