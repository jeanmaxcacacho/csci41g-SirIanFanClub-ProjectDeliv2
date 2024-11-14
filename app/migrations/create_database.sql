create database if not exists tiriantrains_db;
use tiriantrains_db;

/*
    main reference for normalized tables: https://docs.google.com/document/d/1R-muPMy_0neNLb0SloKkpuf4Jn6KFx_u7pxed_T6X70/edit?tab=t.0

    --USER AND SUPERUSER MANAGEMENT--
    creation of a new parent entity called `User`, it has mandatory disjoint subtypes: `Passenger` (customer) and `Admin` (company-side)
    `Admin` users are not allowed to access transactional aspects of the app, they only get to view service-side and management parts.
    Likewise `Passenger` users are not allowed to access managerial aspects of the app, they only get to buy tickets and go places;
    I guess we can implement this by setting a custom 'user_type' key in the session object provided by Flask.
*/

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