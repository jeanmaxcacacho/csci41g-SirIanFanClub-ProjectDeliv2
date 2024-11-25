create database if not exists tiriantrains_db;
use tiriantrains_db;

/*
    main reference for normalized tables: https://docs.google.com/document/d/1R-muPMy_0neNLb0SloKkpuf4Jn6KFx_u7pxed_T6X70/edit?tab=t.0

    --USER AND SUPERUSER MANAGEMENT--
    creation of a new parent entity called `User`, it has mandatory disjoint subtypes: `Passenger` (customer) and `Admin` (company-side)
    `Admin` users are not allowed to access transactional aspects of the app, they only get to view service-side and management parts.
    Likewise `Passenger` users are not allowed to access managerial aspects of the app, they only get to buy tickets and go places;
    I guess we can implement this by setting a custom 'user_type' key in the session object provided by Flask.

    --TRAINS AND TRAIN MAINTENANCE--
    to make this super legit we have to integrate CRUD operations with regards to the trains entities in our app; but tbh that's it
    this is like super omega easy to implement ngl since it's enumerating a `select *` query in a HTML table
    if anything I guess what's tricky is the actual train.html page listing but we'll cross that bridge once we get there
*/

-- USERS

create table if not exists user(
    user_id int not null auto_increment unique primary key,
    email varchar(255) not null unique,
    passkey varchar(255) not null, -- since we're implementing session management this needs to exist
    lname varchar(255) not null,
    fname varchar(255) not null,
    middle_initial varchar(5) not null,
    birth_date date not null,
    sex ENUM('M', 'F') default null,
    user_role ENUM('P', 'A') default 'P', -- for demonstrative purposes, we can just ask for this in the registration form
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp
);

create table if not exists passenger(
    user_id int primary key,
    foreign key (user_id) references user(user_id) on delete cascade
);

create table if not exists admin(
    user_id int primary key,
    foreign key (user_id) references user(user_id) on delete cascade
);

-- TRAINS AND MAINTENANCE

create table if not exists train(
    train_id int not null auto_increment unique primary key,
    train_series ENUM('S', 'A') not null,
    max_speed int not null,
    seating_capacity int not null,
    lavatories int not null,
    reclining_seats ENUM('Y', 'N') not null,
    folding_tables ENUM('Y', 'N') not null,
    vending_machines ENUM('Y', 'N') not null,
    disability_access ENUM('Y', 'N') not null,
    food_service ENUM('Y', 'N') not null,
    luggage_storage ENUM('Y', 'N') not null
);

create table if not exists crew(
    crew_id int not null auto_increment unique primary key,
    lname varchar(255) not null,
    fname varchar(255) not null,
    middle_initial varchar(5) not null
);

create table if not exists maintenance(
    crew_id int not null,
    train_id int not null,
    user_id int not null,
    task varchar(255) not null,
    train_condition ENUM('Excellent', 'Very Good', 'Good', 'Satisfactory', 'Poor') default null,
    maintenance_date date not null,
    primary key (crew_id, train_id, maintenance_date),
    foreign key (crew_id) references crew(crew_id) on delete cascade,
    foreign key (train_id) references train(train_id) on delete cascade,
    foreign key (user_id) references user(user_id) on delete cascade
);

-- ROUTES
create table if not exists station(
    station_id int not null auto_increment unique primary key,
    station_name varchar(255),
    station_type ENUM('L', 'I')
);

create table if not exists routes(
    route_id int not null auto_increment unique primary key,
    train_id int not null,
    origin_id int not null,
    destination_id int not null,
    price int not null,
    duration time not null,
    foreign key (train_id) references train(train_id) on delete cascade,
    foreign key (origin_id) references station(station_id) on delete cascade,
    foreign key (destination_id) references station(station_id) on delete cascade
);

create table if not exists local_routes(
    route_id int primary key,
    foreign key (route_id) references routes(route_id) on delete cascade
);

create table if not exists intertown_routes(
    route_id int primary key,
    foreign key (route_id) references routes(route_id) on delete cascade
);

-- SCHEDULING AND SALES
create table if not exists trip(
     trip_id int not null auto_increment unique primary key,
     train_id int not null,
     departure_date date not null,
     departure_time time not null,
     foreign key (train_id) references train(train_id) on delete cascade
);

create table if not exists local_trip(
    trip_id int not null,
    route_id int not null,
    arrival_time time not null,
    primary key (trip_id, route_id),
    foreign key (trip_id) references trip(trip_id) on delete cascade,
    foreign key (route_id) references routes(route_id) on delete cascade
);

create table if not exists intertown_trip(
    trip_id int not null,
    route_id int not null,
    arrival_time time not null,
    primary key (trip_id, route_id),
    foreign key (trip_id) references trip(trip_id) on delete cascade,
    foreign key (route_id) references routes(route_id) on delete cascade
);

create table if not exists ticket(
    ticket_id int not null auto_increment unique primary key,
    travel_date date not null,
    total_cost int not null,
    purchase_date timestamp default current_timestamp,
    bought_on date default current_date
);

create table if not exists passenger(
    customer_id int not null auto_increment unique primary key,
    lname varchar(255) not null,
    fname varchar(255) not null,
    middle_initial varchar(5) not null,
    birth_date date not null,
    gender ENUM('M', 'F') default null
);