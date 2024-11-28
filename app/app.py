from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session

from datetime import datetime, timedelta

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

# this route will return a list anchor tags that will link to crew and train detail pages
@app.route('/admin')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    trains_query = """
        select train_id t_id, train_series t_series, max_speed
        from train
    """
    crew_query = """
        select crew_id,
               concat(fname, ' ', middle_initial, ' ', lname)
        from crew
    """
    station_query = """
        select *
        from station
        order by station_type
    """
    local_route_query = """
        select lr.route_id, os.station_name, ds.station_name, lr.local_price, lr.local_duration
        from local_route lr
        join routes r on lr.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    intertown_route_query = """
        select ir.route_id, os.station_name, ds.station_name, ir.intertown_price, ir.intertown_duration
        from intertown_route ir
        join routes r on ir.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    local_trip_query = """
        select t.train_id, os.station_name, ds.station_name, t.departure_time, t.arrival_time, lr.local_duration, lr.local_price
        from local_trip lt
        join trip t on lt.trip_id=t.trip_id
        join local_route lr on lt.route_id=lr.route_id
        join routes r on lr.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    intertown_trip_query = """
        select t.train_id, os.station_name, ds.station_name, t.departure_time, t.arrival_time, ir.intertown_duration, ir.intertown_price
        from intertown_trip it
        join trip t on it.trip_id=t.trip_id
        join intertown_route ir on it.route_id=ir.route_id
        join routes r on ir.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    cursor.execute(trains_query)
    trains = cursor.fetchall()
    cursor.execute(crew_query)
    crews = cursor.fetchall()
    cursor.execute(station_query)
    stations = cursor.fetchall()
    cursor.execute(local_route_query)
    local_routes = cursor.fetchall()
    cursor.execute(intertown_route_query)
    intertown_routes = cursor.fetchall()
    cursor.execute(local_trip_query)
    local_trips = cursor.fetchall()
    cursor.execute(intertown_trip_query)
    intertown_trips=cursor.fetchall()

    return render_template("adminpages/admin.html",
                           trains=trains,
                           crews=crews,
                           stations=stations,
                           local_routes=local_routes,
                           intertown_routes=intertown_routes,
                           local_trips=local_trips,
                           intertown_trips=intertown_trips)

# this route will bring the user to the train_detail page; will have a link to `/addmaintenance`
@app.route('/admin/train/<int:train_id>', methods=['GET', 'POST'])
def train_detail(train_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    train_query = """
        select train_id, train_series, max_speed, seating_capacity,
               lavatories, reclining_seats, folding_tables, vending_machines,
               disability_access, food_service, luggage_storage
        from train
        where train_id = %s
    """
    cursor.execute(train_query, (train_id, ))
    train = cursor.fetchone()

    # prepare an actual error page for this case
    if not train:
        return "Train not found"
    
    filter_by = request.args.get('filter', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    maintenance_query = """
        select maintenance_date,
               concat(u.fname, ' ', u.middle_initial, ' ', u.lname),
               concat(c.fname, ' ', c.middle_initial, ' ', c.lname),
               train_id, task, train_condition
        from maintenance m
        join crew c on m.crew_id = c.crew_id
        join user u on m.user_id = u.user_id
        where train_id = %s
    """
    query_params = [train_id]

    # custom date range query takes precedence since it is more specific
    if start_date and end_date:
        maintenance_query += " and maintenance_date between %s and %s"
        query_params.extend([start_date, end_date])
        filter_by = None
    elif filter_by == 'year':
        maintenance_query += " and maintenance_date >= %s"
        query_params.append(datetime.now().replace(month=1, day=1).date())
    elif filter_by == 'month':
        maintenance_query += " and maintenance_date >= %s"
        query_params.append(datetime.now().replace(day=1).date())
    elif filter_by == 'week':
        maintenance_query += " and maintenance_date between %s and %s"

        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        query_params.extend([start_of_week.date(), end_of_week.date()])

    maintenance_query += " order by maintenance_date desc"

    cursor.execute(maintenance_query, query_params)
    maintenance_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('/adminpages/train_detail.html',
                           train=train,
                           maintenance_history=maintenance_history,
                           start_date=start_date,
                           end_date=end_date,
                           filter_by=filter_by)

# insert maintenance record inside train_detail page
@app.route('/admin/addmaintenance/<int:train_id>', methods=['GET', 'POST'])
def add_maintenance(train_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    crew_query = """
        select crew_id,
               concat(fname, ' ', middle_initial, ' ', lname)
        from crew
        order by fname
    """
    cursor.execute(crew_query)
    crews = cursor.fetchall()

    if not crews:
        cursor.close()
        conn.close()
        return "Cannot add maintenance record with no valid crew instances."

    if request.method == 'POST':
        crew_id = request.form.get('crew_id')
        user_id = session.get('user_id')
        task = request.form.get('task')
        train_condition = request.form.get('train_condition')
        maintenance_date = request.form.get('maintenance_date')

        maintenance_insertion_query = """
            insert into maintenance(crew_id, train_id, user_id, task, train_condition, maintenance_date)
            values (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(maintenance_insertion_query,
                       (crew_id, train_id, user_id, task, train_condition, maintenance_date))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('train_detail', train_id=train_id))

    return render_template('/adminpages/add_maintenance.html',
                           crews=crews,
                           train_id=train_id)

# form to add a train
@app.route('/addtrain' ,methods=['GET', 'POST'])
def add_train():
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

# form to add a crew
@app.route('/addcrew', methods=['GET', 'POST'])
def add_crew():
    if request.method == 'POST':
        lname = request.form.get('lname')
        fname = request.form.get('fname')
        middle_initial = request.form.get('middle_initial')

        crew_insertion_query = """
            insert into crew(lname, fname, middle_initial)
            values (%s, %s, %s)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(crew_insertion_query, (lname, fname, middle_initial))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/admin')
    return render_template('adminpages/add_crew.html')

# form to register a station
@app.route('/add_station', methods=['GET', 'POST'])
def add_station():
    if request.method == 'POST':

        station_name = request.form.get('station_name')
        station_type = request.form.get('station_type')

        conn = get_db_connection()
        cursor = conn.cursor()

        station_insertion_query = """
            insert into station(station_name, station_type)
            values (%s, %s)
        """
        cursor.execute(station_insertion_query, (station_name, station_type))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/admin')
    
    return render_template('adminpages/add_station.html')

# form to register route
@app.route('/add_route/<string:route_type>', methods=['GET', 'POST'])
def add_route(route_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    station_query = """
        select station_id, station_name
        from station
        where station_type = %s
    """
    cursor.execute(station_query, (route_type,))
    stations = cursor.fetchall()

    if not stations:
        cursor.close()
        conn.close()
        return 'Cannot add route with no valid station instances'
    
    if request.method == 'POST':
        origin_id = int(request.form.get('origin_id'))
        destination_id = int(request.form.get('destination_id'))
        price = int(request.form.get('price'))
        hours = int(request.form.get('hours'))
        minutes = int(request.form.get('minutes'))

        duration = f"{hours:02}:{minutes:02}:00"

        # default price and duration to specified in project case
        if route_type == 'local':
            price = 2
            duration = '00:05:00'

        route_insertion_query = """
            insert into routes(origin_id, destination_id)
            values (%s, %s)
        """
        cursor.execute(route_insertion_query, (origin_id, destination_id))

        if route_type == 'local':
            route_subtype_insert = """
                insert into local_route(route_id, local_price, local_duration)
                values (last_insert_id(), %s, %s)
            """
        else:
            route_subtype_insert = """
                insert into intertown_route(route_id, intertown_price, intertown_duration)
                values (last_insert_id(), %s, %s)
            """
        cursor.execute(route_subtype_insert, (price, duration))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/admin')

    conn.commit()
    cursor.close()
    conn.close()
    return render_template('adminpages/add_route.html', stations=stations, route_type=route_type)

@app.route('/add_trip/<string:trip_type>', methods=['GET', 'POST'])
def add_trip(trip_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    train_query = """
        select train_id
        from train
        where train_series = %s
    """

    if trip_type == 'local':
        train_series = 'S'
        route_query = """
            select lr.route_id, concat(os.station_name, ' - ', ds.station_name)
            from local_route lr
            join routes r on lr.route_id=r.route_id
            join station os on r.origin_id=os.station_id
            join station ds on r.destination_id=ds.station_id
        """
    else:
        train_series = 'A'
        route_query = """
            select ir.route_id, concat(os.station_name, ' to ', ds.station_name)
            from intertown_route ir
            join routes r on ir.route_id=r.route_id
            join station os on r.origin_id=os.station_id
            join station ds on r.destination_id=ds.station_id
        """

    cursor.execute(train_query, (train_series, ))
    trains = cursor.fetchall()
    cursor.execute(route_query)
    routes = cursor.fetchall()

    if not trains or not routes:
        cursor.close()
        conn.close()
        return 'Cannot add trip without any valid train or route intances.'

    if request.method == 'POST':
        train_id = int(request.form.get("train_id"))
        departure_hour = int(request.form.get("departure_hour"))
        departure_minute = int(request.form.get("departure_minute"))
        route_id = int(request.form.get("route_id",))

        if trip_type == 'local':
            duration_query = """
                select local_duration
                from local_route
                where route_id = %s
            """
        else:
            duration_query = """
                select intertown_duration
                from intertown_route
                where route_id = %s
            """
        cursor.execute(duration_query, (route_id,))
        duration = cursor.fetchone()

        departure_time = f"{departure_hour:02}:{departure_minute:02}:00"

        duration_str = duration[0]  # Get the duration string
        duration_hours, duration_minutes, duration_seconds = map(int, duration_str.split(':'))
        
        duration_in_minutes = (duration_hours*60) + duration_minutes
        total_minutes = departure_minute + duration_in_minutes
        arrival_minute = total_minutes % 60
        arrival_hour = (departure_hour + (total_minutes // 60)) % 24

        # Format the final arrival time
        arrival_time = f"{arrival_hour:02}:{arrival_minute:02}:00"

        trip_insertion_query = """
            insert into trip(train_id, departure_time, arrival_time)
            values(%s, %s, %s)
        """
        cursor.execute(trip_insertion_query, (train_id, departure_time, arrival_time))
        
        if trip_type == 'local':
            trip_subtype_insert = """
                insert into local_trip(trip_id, route_id)
                values (last_insert_id(), %s)
            """
        else:
            trip_subtype_insert = """
                insert into intertown_trip(trip_id, route_id)
                values (last_insert_id(), %s)
            """
        cursor.execute(trip_subtype_insert, (route_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/admin')

    
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('adminpages/add_trip.html', trip_type=trip_type, trains=trains, routes=routes)
"""
MISC. SETUP
"""

# set app to debug mode makes it so that you can serve the application by running `python app.py` via terminal
if __name__ == '__main__':
    app.run(debug=True)