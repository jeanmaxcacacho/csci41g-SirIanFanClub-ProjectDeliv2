from flask import Flask, render_template, request, redirect, session
from flask_session import Session

from database.db import get_db_connection

app = Flask(__name__)

# session management config
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/')
# current task is to just display user information associated to current session
def index():
    is_logged_in = session.get('is_logged_in', False)
    passenger_name = None

    if is_logged_in:
        conn = get_db_connection()
        cursor = conn.cursor()
        userinfo_query = """
            select concat(fname, " ", middle_initial, " ", lname)
            from passenger p
            where p.passenger_id = %s
        """
        cursor.execute(userinfo_query, (session.get('user_id'), ))
        passenger_name = cursor.fetchone()
    return render_template('index.html', 
                           is_logged_in=is_logged_in,
                           passenger_name=passenger_name)

# if login info matches to an account in the db, user logs in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passkey = request.form.get('passkey')

        conn = get_db_connection()
        cursor = conn.cursor()
        match_query = """
        select p.passenger_id p_id
        from passenger p
        where p.email = %s and p.passkey = %s
        """
        cursor.execute(match_query, (email, passkey))
        match_result = cursor.fetchone()

        # successful login
        if match_result:
            session['user_id'] = match_result[0]
            session['is_logged_in'] = True
            return redirect('/')
        # failed login
        else:
            return render_template("errorpages/login_failed.html")
    return render_template("sessionmgt/login.html")

# clear session cookie
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# create a user object and redirect to login
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        passkey = request.form.get('passkey')
        lname = request.form.get('lname')
        fname = request.form.get('fname')
        middle_initial = request.form.get('middle_initial')
        birth_date = request.form.get('birth_date')
        sex = request.form.get('sex')

        conn = get_db_connection()
        cursor = conn.cursor()
        registration_query = """
            INSERT INTO passenger(email, passkey, lname, fname, middle_initial, birth_date, sex)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(registration_query, (email, passkey, lname,
                                            fname, middle_initial, birth_date, sex))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/login')
    return render_template('sessionmgt/register.html')

# set app to debug mode makes it so that you can serve the application by running `python app.py` via terminal
if __name__ == '__main__':
    app.run(debug=True)