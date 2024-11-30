# this script will only be run after train and routes have been populated
# it's important to know that the default creation scripts make it so that
# there is a 1:1 ratio between trains and routes

from db import get_db_connection
from datetime import datetime, timedelta

if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()

    local_train_query = """
        select tr.train_id
        from train tr
        where tr.train_series = 'S'
    """
    cursor.execute(local_train_query)
    local_trains = cursor.fetchall()

    local_route_query = """
        select lr.route_id, r.origin_id, r.destination_id, lr.local_duration
        from local_route lr
        join route r on lr.route_id = r.route_id
    """
    cursor.execute(local_route_query)
    local_routes = cursor.fetchall()

    # I adjusted the order of how things are in inserted s.t.
    # train_id and route_ids have 1 to 1 correspondence
    train_ids = [x[0] for x in local_trains]
    route_ids = [x[0] for x in local_routes]

    """ READ IN WALFRIDO DAVID DIY'S VOICE
        per each iteration of insertion we want to DECREMENT the the train assigned to each route
        each iteration will have four insertions

        1st iteration || r0: t0, r1: t1, r2: t2, r3:t3
        2nd iteration || r0: t3, r1: t0, r2: t1, r3:t2

        once the iterator hits 0 BAAAM, reset back to 3; there will never be overlaps because of 1:1 ratio
        between local trains and routes, at any given point in time a single train must only be assigned to
        a single route and vice-versa

        one important thing to note also is that the actual mathematical index and the `id` attribute
        are off by one, so just do keep that in mind

        for demonstrative purposes let's only produce rows from 10:00 AM - 15:00 PM
    """

    base_departure_time = datetime.strptime("10:00:00", "%H:%M:%S")
    end_time = datetime.strptime("15:00:00",  "%H:%M:%S")
    local_departure_interval = 10 # 10 minute intervals per trip
    current_departure_time = base_departure_time

    train_index = len(train_ids) - 1

    while current_departure_time <= end_time:
        for route_index, route in enumerate(local_routes):
            train_id = train_ids[(train_index + route_index) % len(train_ids)]

            route_id, origin_id, destination_id, local_duration = route
            arrival_time = (current_departure_time + local_duration).time()

            cursor.execute("""
                insert into trip (train_id, departure_time, arrival_time)
                values (%s, %s, %s)
            """, (train_id, current_departure_time.time(), arrival_time))

            trip_id = cursor.lastrowid

            cursor.execute("""
                insert into local_trip (trip_id, route_id)
                values (%s, %s)
            """, (trip_id, route_id))

            print(f"Assigned Train {train_id} to Route {route_id} from {origin_id} to {destination_id} "
                  f"departing at {current_departure_time.time()} and arriving at {arrival_time}")
        train_index = (train_index - 1) % len(train_ids)
        current_departure_time += timedelta(minutes=local_departure_interval)
    conn.commit()
    cursor.close()
    conn.close()