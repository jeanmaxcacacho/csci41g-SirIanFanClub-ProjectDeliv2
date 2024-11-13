create database if not exists tiriantrains_db;
use tiriantrains_db;

-- from https://docs.google.com/document/d/1R-muPMy_0neNLb0SloKkpuf4Jn6KFx_u7pxed_T6X70/edit?tab=t.0
create table if not exists passenger(
    passenger_id int not null auto_increment unique primary key,
    lname varchar(255) not null,
    fname varchar(255) not null,
    middle_initial varchar(5) not null,
    birth_date date not null,
    sex varchar(1)
);