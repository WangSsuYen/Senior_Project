CREATE TABLE client (
    uniform_numbers INT PRIMARY KEY,
    client_password VARCHAR(10) NOT NULL ,
    creattime datetime NOT NULL

);

CREAT TABLE client_detail(
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    website VARCHAR(255),
    rating DECIMAL(2,1),
    cuisine VARCHAR(255),
    price_range VARCHAR(20),
    opening_hours VARCHAR(255),
    description TEXT,
    image_url VARCHAR(255)
)