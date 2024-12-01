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
        select lr.route_id, os.station_name, ds.station_name,  lr.local_duration, lr.local_price
        from local_route lr
        join route r on lr.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    intertown_route_query = """
        select ir.route_id, os.station_name, ds.station_name, ir.intertown_duration, ir.intertown_price
        from intertown_route ir
        join route r on ir.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    local_trip_query = """
        select t.train_id, os.station_name, ds.station_name, t.departure_time, t.arrival_time, lr.local_duration, lr.local_price
        from local_trip lt
        join trip t on lt.trip_id=t.trip_id
        join local_route lr on lt.route_id=lr.route_id
        join route r on lr.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    intertown_trip_query = """
        select t.train_id, os.station_name, ds.station_name, t.departure_time, t.arrival_time, ir.intertown_duration, ir.intertown_price
        from intertown_trip it
        join trip t on it.trip_id=t.trip_id
        join intertown_route ir on it.route_id=ir.route_id
        join route r on ir.route_id=r.route_id
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

"""
PASSENGER PAGES
"""

# present all possible trips then create tickets and ticketitems as dictated by what's purchased
# also display relevant passenger info i.e. amt of Lion Coins they have
@app.route('/passenger')
def passenger():
    conn = get_db_connection()
    cursor = conn.cursor()

    customer_query = """
        select concat(u.fname, ' ', u.middle_initial, ' ', u.lname),
               p.lion_coins,
               u.created_at
        from passenger p
        join user u on p.user_id = u.user_id
        where p.user_id = %s
    """
    cursor.execute(customer_query, (session.get('user_id'), ))
    user = cursor.fetchone()

    local_route_query = """
        select lr.route_id, os.station_name, ds.station_name,  lr.local_duration, lr.local_price
        from local_route lr
        join route r on lr.route_id=r.route_id
        join station os on r.origin_id=os.station_id
        join station ds on r.destination_id=ds.station_id
    """
    cursor.execute(local_route_query)
    local_routes = cursor.fetchall()

    # display all `ticket`s purchased by the user, these will have their own
    # detail pages displaying all the `ticketitem`s associated per `ticket`
    ticket_query = """
        select t.ticket_id, t.travel_date, t.total_cost, t.purchase_date
        from ticket t
        where t.user_id = %s
    """
    cursor.execute(ticket_query, (session.get('user_id'), ))
    tickets = cursor.fetchall()

    return render_template('passengerpages/passenger.html',
                           user=user,
                           local_routes=local_routes,
                           tickets = tickets)

# form sequence to instantiate the base ticketitem of a ticket
@app.route('/passenger/buyticket1', methods=['GET'])
def buyticket1():
    session['travel_date'] = request.args.get('travel_date')
    session['departure_time'] = request.args.get('departure_time')

    if session['travel_date'] and session['departure_time']:
        print(session['travel_date'])
        print(session['departure_time'])
        return redirect(url_for('buyticket2'))
    return render_template('passengerpages/buy_ticket1.html')

@app.route('/passenger/buyticket2/', methods=['GET', 'POST'])
def buyticket2():
    travel_date = session.get('travel_date')
    departure_time = session.get('departure_time')

    print(departure_time)

    conn = get_db_connection()
    cursor = conn.cursor()

    trip_query = """
        select t.trip_id, r.route_id, os.station_name, ds.station_name, lr.local_price
        from local_trip lt
        join trip t on lt.trip_id = t.trip_id
        join route r on lt.route_id = r.route_id
        join station os on r.origin_id = os.station_id
        join station ds on r.destination_id = ds.station_id
        join local_route lr on r.route_id = lr.route_id
        where t.departure_time >= %s
        order by t.departure_time
        limit 4
    """
    cursor.execute(trip_query, (departure_time, ))
    trips = cursor.fetchall()

    if request.method == 'POST':
        trip_id = request.form.get('trip_id')

        ticket_insertion_query = """
            insert into ticket(user_id, travel_date, total_cost)
            values(%s, %s, %s)
        """
        # total cost can be 2 atm because it is the base ticketitem
        cursor.execute(ticket_insertion_query, (session.get('user_id'), travel_date, 2))

        ticket_id = cursor.lastrowid
        ticketitem_insertion_query = """
            insert into ticketitem(ticket_id, trip_id)
            values(%s, %s)
        """
        cursor.execute(ticketitem_insertion_query, (ticket_id, trip_id))

        update_userbal_query = """
            update passenger
            set lion_coins = lion_coins - 2
            where user_id = %s
        """
        cursor.execute(update_userbal_query, (session.get('user_id'), ))

        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('passenger'))

    return render_template('passengerpages/buy_ticket2.html', trips=trips)

@app.route('/passenger/ticket/<int:ticket_id>', methods=['GET', 'POST'])
def ticket_detail(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    base_ticket_query = """
        select tick.ticket_id, u.user_id, u.lname, u.fname, u.middle_initial, u.sex, tick.travel_date, tick.total_cost
        from user u
        join ticket tick on u.user_id = tick.user_id
        where tick.ticket_id = %s
    """
    cursor.execute(base_ticket_query, (ticket_id, ))
    ticket = cursor.fetchone()

    ticketitem_query = """
        select concat(tr.train_series, '-', lpad(tr.train_id, 3, '0')),
               os.station_name, ds.station_name,
               t.departure_time, t.arrival_time,
               lr.local_duration, lr.local_price
        from ticketitem ti
        join trip t on ti.trip_id = t.trip_id
        join local_trip lt on t.trip_id = lt.trip_id
        join route r on lt.route_id = r.route_id
        join local_route lr on r.route_id = lr.route_id
        join train tr on t.train_id = tr.train_id
        join station os on r.origin_id = os.station_id
        join station ds on r.destination_id = ds.station_id
        where ticket_id = %s
        order by t.departure_time
    """
    cursor.execute(ticketitem_query, (ticket_id, ))
    ticketitems = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('passengerpages/ticket_detail.html', ticket=ticket, ticketitems=ticketitems)

# generating new ticketitems for tickets that already exist
@app.route('/passenger/ticket/addtrip1/<int:ticket_id>', methods=['GET', 'POST'])
def addtrip1(ticket_id):
    departure_time = request.args.get('departure_time')
    session['departure_time'] = departure_time
    if session['departure_time']:
        return redirect(url_for('addtrip2', ticket_id=ticket_id))
    return render_template('passengerpages/add_trip1.html', ticket_id=ticket_id)

@app.route('/passenger/ticket/addtrip2/<int:ticket_id>', methods=['GET', 'POST'])
def addtrip2(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    departure_time = session.get('departure_time')

    trip_query = """
        select t.trip_id, r.route_id, os.station_name, ds.station_name, lr.local_price
        from local_trip lt
        join trip t on lt.trip_id = t.trip_id
        join route r on lt.route_id = r.route_id
        join station os on r.origin_id = os.station_id
        join station ds on r.destination_id = ds.station_id
        join local_route lr on r.route_id = lr.route_id
        where t.departure_time >= %s
        order by t.departure_time
        limit 4
    """
    cursor.execute(trip_query, (departure_time, ))
    trips = cursor.fetchall()
    cursor.close()
    conn.close()
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        trip_id = request.form.get('trip_id')
        ticketitem_insertion_query = """
            insert into ticketitem(ticket_id, trip_id)
            values (%s, %s)
        """
        cursor.execute(ticketitem_insertion_query, (ticket_id, trip_id))

        # update total cost attribute of base ticket
        total_cost_update_query = """
            update ticket
            set total_cost = (
                select count(*)
                from ticketitem
                where ticketitem.ticket_id = ticket.ticket_id
            ) * 2
            where ticket_id = %s
        """
        cursor.execute(total_cost_update_query, (ticket_id, ))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    return render_template('passengerpages/add_trip2.html', trips=trips, ticket_id=ticket_id)

"""
MISC. SETUP
"""

# set app to debug mode makes it so that you can serve the application by running `python app.py` via terminal
if __name__ == '__main__':
    app.run(debug=True)