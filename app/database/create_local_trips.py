# this script will only be run after train and routes have been populated
# it's important to know that the default creation scripts make it so that
# there is a 1:1 ratio between trains and routes

from db import get_db_connection
from datetime import datetime, timedelta

if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()

    local_route_query = """
        select lr.route_id, r.origin_id, r.destination_id, lr.local_duration
        from local_route lr
        join route r on lr.route_id = r.route_id
    """
    cursor.execute(local_route_query)
    local_routes = cursor.fetchall()

    # intertown_route_query = """
    #     select route_id, intertown_duration from intertown_route
    # """
    # cursor.execute(intertown_route_query)
    # intertown_routes = cursor.fetchall()

    local_train_query = """
        select train_id
        from train
        where train_series = 'S'
    """
    cursor.execute(local_train_query)
    local_trains = [train[0] for train in cursor.fetchall()]

    # intertown_train_query = """
    #     select train_id
    #     from train
    #     where train_series = 'A'
    # """
    # cursor.execute(intertown_train_query)
    # intertown_trains = cursor.fetchall()

    # operational hours
    base_departure_time = datetime.strptime("06:00:00", "%H:%M:%S")
    end_time = datetime.strptime("22:00:00", "%H:%M:%S")
    local_departure_interval = 10
    # intertown_departure_interval = 30

    # initialize cyclic train assignments for local trips
    station_count = 4
    train_positions = {train_id:i for i, train_id in enumerate(local_trains)} # assign each train an index
    train_queue = local_trains[:]

    # # local_trip insertion
    # for route_index, (train, route) in enumerate(zip(local_trains, local_routes)):
    #     train_id = train[0]
    #     route_id, local_duration = route
    #     current_departure_time = base_departure_time

    #     while current_departure_time <= end_time:
    #         arrival_time = (current_departure_time + local_duration).time()

    #         cursor.execute("""
    #             insert into trip(train_id, departure_time, arrival_time)
    #                        values (%s, %s, %s)
    #                        """,
    #                        (train_id, current_departure_time.time(), arrival_time))
            
    #         trip_id = cursor.lastrowid

    #         cursor.execute("""
    #             insert into local_trip(trip_id, route_id)
    #             values (%s, %s)
    #                        """,
    #                        (trip_id, route_id))
            
    #         current_departure_time += timedelta(minutes=local_departure_interval)

    # current_departure_time = base_departure_time
    # while current_departure_time <= end_time:
    #     for route_id, origin_id, destination_id, local_duration in local_routes:
    #         assigned_train = None
    #         for _ in range(len(train_queue)):
    #             train_id = train_queue.pop(0)
    #             if train_positions[train_id] == origin_id:
    #                 assigned_train = train_id
    #                 break
    #             train_queue.append(train_id)
    #         if not assigned_train:
    #             print(f"Warning: No train available at station {origin_id}. Skipping this trip.")
    #             continue
    #         arrival_time = (current_departure_time + local_duration).time()

    #         print(f"Assigning Train {assigned_train} to Route {route_id} "
    #               f"from Station {origin_id} to Station {destination_id} "
    #               f"departing at {current_departure_time.time()} and arriving at {arrival_time}")
            
    #         cursor.execute("""
    #             insert into trip(train_id, departure_time, arrival_time)
    #             values (%s, %s, %s)
    #                        """,
    #                        (assigned_train, current_departure_time.time(), arrival_time))
    #         trip_id = cursor.lastrowid

    #         cursor.execute("""
    #             insert into local_trip(trip_id, route_id)
    #             values (%s, %s)
    #                        """,
    #                        (trip_id, route_id))
            
    #         train_positions[assigned_train] = destination_id
    #         train_queue.append(assigned_train)
    #     current_departure_time += timedelta(minutes=local_departure_interval)
    #     print(f"Train positions after {current_departure_time.time()}: {train_positions}")

    # Local trip insertion
    current_departure_time = base_departure_time
    while current_departure_time <= end_time:
        for route_id, origin_id, destination_id, local_duration in local_routes:
            assigned_train = None

            # Rotate through the train queue for assignment
            for _ in range(len(train_queue)):
                train_id = train_queue.pop(0)  # Get the first train from the queue
                if train_positions[train_id] == origin_id:  # Check if the train is at the origin station
                    assigned_train = train_id
                    break
                train_queue.append(train_id)  # Rotate the train back into the queue

            # Check if a train was assigned
            if not assigned_train:
                print(f"Warning: No train available at station {origin_id}. Skipping this trip.")
                continue

            # Calculate arrival time
            arrival_time = (current_departure_time + local_duration).time()

            # Log assignment (for debugging)
            print(f"Assigning Train {assigned_train} to Route {route_id} "
                  f"from Station {origin_id} to Station {destination_id} "
                  f"departing at {current_departure_time.time()} and arriving at {arrival_time}")

            # Insert trip into `trip` table
            cursor.execute("""
                INSERT INTO trip (train_id, departure_time, arrival_time)
                VALUES (%s, %s, %s)
            """, (assigned_train, current_departure_time.time(), arrival_time))
            trip_id = cursor.lastrowid

            # Insert trip into `local_trip` table
            cursor.execute("""
                INSERT INTO local_trip (trip_id, route_id)
                VALUES (%s, %s)
            """, (trip_id, route_id))

            # Update train position
            train_positions[assigned_train] = destination_id

            # Move the assigned train to the back of the queue
            train_queue.append(assigned_train)

        # Increment departure time
        current_departure_time += timedelta(minutes=local_departure_interval)

        # Log train positions after each departure cycle (for debugging)
        print(f"Train positions after {current_departure_time.time()}: {train_positions}")


    # for route_index, (train, route) in enumerate(zip(intertown_trains, intertown_routes)):
    #     train_id  = train[0]
    #     route_id, intertown_duration = route
    #     current_departure_time = base_departure_time

    #     while current_departure_time <= end_time:
    #         arrival_time = (current_departure_time + intertown_duration).time()
            
    #         cursor.execute("""
    #             insert into trip(train_id, departure_time, arrival_time)
    #             values (%s, %s, %s)
    #                        """,
    #                        (train_id, current_departure_time.time(), arrival_time))
            
    #         trip_id = cursor.lastrowid

    #         cursor.execute("""
    #             insert into intertown_trip(trip_id, route_id)
    #             values (%s, %s)
    #                        """,
    #                        (trip_id, route_id))
    #         current_departure_time += timedelta(minutes=intertown_departure_interval)

    conn.commit()
    cursor.close()
    conn.close()