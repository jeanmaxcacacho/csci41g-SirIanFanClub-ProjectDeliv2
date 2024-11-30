-- local trains
insert into train(train_series, max_speed, seating_capacity, lavatories,
reclining_seats, folding_tables, vending_machines, disability_access,
food_service, luggage_storage)
values
('S', 120, 70, 7, 'Y', 'Y', 'Y', 'Y', 'N', 'N'),
('S', 120, 70, 7, 'Y', 'Y', 'Y', 'Y', 'N', 'N'),
('S', 120, 70, 7, 'Y', 'Y', 'Y', 'Y', 'N', 'N'),
('S', 120, 70, 7, 'Y', 'Y', 'Y', 'Y', 'N', 'N');

-- inter-town trains
insert into train(train_series, max_speed, seating_capacity, lavatories,
reclining_seats, folding_tables, vending_machines, disability_access,
food_service, luggage_storage)
values
('A', 320, 400, 8, 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'),
('A', 310, 380, 7, 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'),
('A', 300, 360, 6, 'Y', 'Y', 'N', 'Y', 'Y', 'Y'),
('A', 300, 350, 6, 'Y', 'Y', 'N', 'Y', 'Y', 'Y'),
('A', 290, 340, 6, 'Y', 'Y', 'N', 'Y', 'Y', 'Y'),
('A', 250, 320, 5, 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'),
('A', 240, 300, 4, 'Y', 'Y', 'N', 'Y', 'N', 'Y'),
('A', 240, 280, 4, 'Y', 'Y', 'N', 'Y', 'N', 'N'),
('A', 230, 270, 4, 'Y', 'Y', 'N', 'Y', 'N', 'N'),
('A', 230, 260, 3, 'Y', 'Y', 'N', 'Y', 'N', 'N'),
('A', 200, 220, 2, 'N', 'N', 'N', 'Y', 'N', 'N'),
('A', 190, 210, 2, 'N', 'N', 'N', 'Y', 'N', 'N'),
('A', 180, 200, 2, 'N', 'N', 'N', 'Y', 'N', 'N'),
('A', 170, 190, 2, 'N', 'N', 'N', 'Y', 'N', 'N'),
('A', 160, 180, 2, 'N', 'N', 'N', 'Y', 'N', 'N'),
('A', 280, 240, 5, 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'),
('A', 270, 230, 4, 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'),
('A', 260, 220, 4, 'Y', 'Y', 'N', 'Y', 'Y', 'Y'),
('A', 250, 210, 4, 'Y', 'Y', 'N', 'Y', 'Y', 'Y'),
('A', 150, 150, 1, 'N', 'N', 'N', 'N', 'N', 'N'),
('A', 140, 140, 1, 'N', 'N', 'N', 'N', 'N', 'N'),
('A', 130, 130, 1, 'N', 'N', 'N', 'N', 'N', 'N');

-- crews
insert into crew(lname, fname, middle_initial)
values
('Garcia', 'John', 'D.'),
('Santos', 'Maria', 'E.'),
('Reyes', 'Michael', 'L.'),
('Cruz', 'Anna', 'M.'),
('Dela Cruz', 'James', 'P.'),
('Ramos', 'Sofia', 'R.'),
('Torres', 'Paul', 'S.'),
('Lopez', 'Catherine', 'T.'),
('Gonzales', 'David', 'V.'),
('Hernandez', 'Emily', 'J.');