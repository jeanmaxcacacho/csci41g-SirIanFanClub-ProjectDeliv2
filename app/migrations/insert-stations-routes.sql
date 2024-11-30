-- according to case map allies' enclave is the entry point
-- to the inter-town station network so allies' enclave is
-- technically both a local and a

-- stations
insert into station(station_name, station_type)
values
("Allies' Enclave", 'interchange'),
("Beaver's Dam", 'local'),
("The Lamp Post", 'local'),
("The Wardrobe", 'local'),
("Mr.Tumms", 'inter-town'),
("Aslan's Camp", 'inter-town'),
("Cauldron Pool", 'inter-town'),
("Cherry Tree", 'inter-town'),
("Father Christmas", 'inter-town'),
("Dancing Lawn", 'inter-town'),
("Anvard", 'inter-town'),
("The Stone Tablet", 'inter-town'),
("Witch's Camp", 'inter-town');


-- local routes
insert into route (origin_id, destination_id)
values
(
    (select station_id from station where station_name = "Beaver's Dam"),
    (select station_id from station where station_name = "Allies' Enclave")
),
(
    (select station_id from station where station_name = "Allies' Enclave"),
    (select station_id from station where station_name = "The Wardrobe")
),
(
    (select station_id from station where station_name = "The Wardrobe"),
    (select station_id from station where station_name = "The Lamp Post")
),
(
    (select station_id from station where station_name = "The Lamp Post"),
    (select station_id from station where station_name = "Beaver's Dam")
);


-- intertown routes
insert into route(origin_id, destination_id)
values
(
    (select station_id from station where station_name = "Allies' Enclave"),
    (select station_id from station where station_name = "Mr.Tumms")
),
(
    (select station_id from station where station_name = "Mr.Tumms"),
    (select station_id from station where station_name = "Allies' Enclave")
),
(
    (select station_id from station where station_name = "Allies' Enclave"),
    (select station_id from station where station_name = "Aslan's Camp")
),
(
    (select station_id from station where station_name = "Aslan's Camp"),
    (select station_id from station where station_name = "Allies' Enclave")
),
(
    (select station_id from station where station_name = "Allies' Enclave"),
    (select station_id from station where station_name = "Cauldron Pool")
),
(
    (select station_id from station where station_name = "Cauldron Pool"),
    (select station_id from station where station_name = "Allies' Enclave")
),
(
    (select station_id from station where station_name = "Allies' Enclave"),
    (select station_id from station where station_name = "Dancing Lawn")
),
(
    (select station_id from station where station_name = "Dancing Lawn"),
    (select station_id from station where station_name = "Allies' Enclave")
),
(
    (select station_id from station where station_name = "Dancing Lawn"),
    (select station_id from station where station_name = "Anvard")
),
(
    (select station_id from station where station_name = "Anvard"),
    (select station_id from station where station_name = "Dancing Lawn")
),
(
    (select station_id from station where station_name = "Cauldron Pool"),
    (select station_id from station where station_name = "Cherry Tree")
),
(
    (select station_id from station where station_name = "Cherry Tree"),
    (select station_id from station where station_name = "Cauldron Pool")
),
(
    (select station_id from station where station_name = "Father Christmas"),
    (select station_id from station where station_name = "Cauldron Pool")
),
(
    (select station_id from station where station_name = "Cauldron Pool"),
    (select station_id from station where station_name = "Father Christmas")
),
(
    (select station_id from station where station_name = "Cherry Tree"),
    (select station_id from station where station_name = "Father Christmas")
),
(
    (select station_id from station where station_name = "Father Christmas"),
    (select station_id from station where station_name = "Cherry Tree")
),
(
    (select station_id from station where station_name = "Father Christmas"),
    (select station_id from station where station_name = "Witch's Camp")
),
(
    (select station_id from station where station_name = "Witch's Camp"),
    (select station_id from station where station_name = "Father Christmas")
),
(
    (select station_id from station where station_name = "Witch's Camp"),
    (select station_id from station where station_name = "The Stone Tablet")
),
(
    (select station_id from station where station_name = "The Stone Tablet"),
    (select station_id from station where station_name = "Witch's Camp")
),
(
    (select station_id from station where station_name = "The Stone Tablet"),
    (select station_id from station where station_name = "Dancing Lawn")
),
(
    (select station_id from station where station_name = "Dancing Lawn"),
    (select station_id from station where station_name = "The Stone Tablet")
);


insert into local_route(route_id)
select r.route_id from route r
join station os on r.origin_id = os.station_id
join station ds on r.destination_id = ds.station_id
where os.station_type in ('local', 'interchange')
and ds.station_type in ('local', 'interchange');


insert into intertown_route(route_id, intertown_price, intertown_duration)
select
    r.route_id,
    floor(rand()*31) + 20 as intertown_price,
    sec_to_time(floor(rand()*14400) + 3600) as intertown_duration
from route r
join station os on r.origin_id = os.station_id
join station ds on r.destination_id = ds.station_id
where os.station_type in ('interchange', 'inter-town')
or ds.station_type in ('interchange', 'inter-town');