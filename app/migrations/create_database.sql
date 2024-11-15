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
    crew_id int,
    train_id int,
    task varchar(255),
    condition ENUM('Excellent', 'Good', 'Satisfactory', 'Below Satisfactory', 'Poor'),
    primary key (crew_id, train_id), -- MariaDB composite keys
    foreign key (crew_id) references crew(crew_id) on delete cascade,
    foreign key (train_id) references train(train_id) on delete cascade
);