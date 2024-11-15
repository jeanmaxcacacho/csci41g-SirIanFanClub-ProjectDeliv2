from flask import Flask, render_template, request, redirect, session
from flask_session import Session

from database.db import get_db_connection

"""
APPLICATION SETUP
"""

app = Flask(__name__)

# session management config
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

"""
DESTINATION ROUTE
"""

# destination page after login return one template and two different redirects
# - `/admin` admin landing page (will lead to admin_dashboard.html)
# - `/passenger` passenger landing page (will lead to passenger_dashboard.html)
@app.route('/')
def index():
    is_logged_in = session.get('is_logged_in', False)

    # redirect to either `admin` or `/passenger` route
    if is_logged_in:
        if session.get('user_role') == 'P':
            return redirect('/passenger')
        else:
            return redirect('/admin')
    return render_template('index.html')


"""
LOGIN/LOGOUT AND REGISTRATION ROUTES
"""

# if login info matches to an account in the db, user logs in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passkey = request.form.get('passkey')

        conn = get_db_connection()
        cursor = conn.cursor()
        match_query = """
            select u.user_id u_id, u.user_role u_role
            from user u
            where u.email = %s and u.passkey = %s
        """
        cursor.execute(match_query, (email, passkey))
        match_result = cursor.fetchone()

        # successful login
        if match_result:
            session['user_id'] = match_result[0]
            session['user_role'] = match_result[1]
            session['is_logged_in'] = True

            cursor.close()
            conn.close()

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
        user_role = request.form.get('user_role')

        conn = get_db_connection()
        cursor = conn.cursor()
        registration_query = """
            insert into user(email, passkey, lname, fname, middle_initial, birth_date, sex, user_role)
            values (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(registration_query, (email, passkey, lname,
                                            fname, middle_initial, birth_date,
                                            sex, user_role))

        # conditional insertion into table based on user_role
        conditional_insert = None
        if user_role == 'P':
            conditional_insert = """
                insert into passenger(user_id)
                values (last_insert_id())
            """
        else:
            conditional_insert = """
                insert into admin(user_id)
                values (last_insert_id())
            """
        cursor.execute(conditional_insert)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/login')
    return render_template('sessionmgt/register.html')

"""
ADMIN ROUTES
"""

@app.route('/admin')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    trains_query = """
        select train_id t_id, train_series t_series, max_speed
        from train
    """
    cursor.execute(trains_query)
    trains = cursor.fetchall()
    return render_template("adminpages/admin.html",
                           trains = trains)

@app.route('/addtrain' ,methods=['GET', 'POST'])
def addtrain():
    if request.method == 'POST':
        train_series = request.form.get('train_series')
        max_speed = request.form.get('max_speed')
        seating_capacity = request.form.get('seating_capacity')
        lavatories = request.form.get('lavatories')
        reclining_seats = request.form.get('reclining_seats')
        folding_tables = request.form.get('folding_tables')
        vending_machines = request.form.get('vending_machines')
        disability_access = request.form.get('disability_access')
        food_service = request.form.get('food_service')
        luggage_storage = request.form.get('luggage_storage')

        conn = get_db_connection()
        cursor = conn.cursor()

        train_insertion_query = """
            insert into train(train_series, max_speed, seating_capacity, lavatories, reclining_seats,
                              folding_tables, vending_machines, disability_access, food_service, luggage_storage)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(train_insertion_query, (train_series, max_speed, seating_capacity,
                                               lavatories, reclining_seats, folding_tables,
                                               vending_machines, disability_access, food_service, 
                                               luggage_storage))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect('/admin')
    return render_template('adminpages/add_train.html')

"""
MISC. SETUP
"""

# set app to debug mode makes it so that you can serve the application by running `python app.py` via terminal
if __name__ == '__main__':
    app.run(debug=True)