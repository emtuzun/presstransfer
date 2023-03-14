use presstransfer;
select * from deneme;
select * from deneme where robot=1 and position=1;
update deneme set x_axis = 1.0, y_axis = 1.0, z_axis = 1.0, a_axis = 1.0, b_axis = 1.0, c_axis = 1.0, p_axis = 1.0, q_axis = 1.0 where robot = 1 and position = 1;
SET SQL_SAFE_UPDATES = 0;