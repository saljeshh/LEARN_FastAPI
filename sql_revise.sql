select id,name 
from products
limit 5 offset 1;
-- offset skip first 1 row

select * from products


insert into products (id,name, price,inventory) values(8,'Book',15,7),(9,'Watch',45,8);


-- if we want to return the data as soon as the data is done, we use returning
insert into products (id,name, price,inventory) values(10,'Calculator',15,7) returning *;


DELETE FROM products 
WHERE id = 10;
SELECT * FROM products;

UPDATE products 
SET name = 'Chicken Rice', price = 40
WHERE id = 9 returning *;
