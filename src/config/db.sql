CREATE DATABASE fyp_temp_db;

\c fyp_temp_db;

CREATE TABLE tblusers(
id SERIAL PRIMARY KEY,
public_id VARCHAR(255),
username VARCHAR(255),
password VARCHAR(255),
createdon VARCHAR(255)
);

CREATE TABLE tblimages(
id SERIAL PRIMARY KEY,
imagename VARCHAR(255),
image VARCHAR(255),
parentOf integer,
createdBy VARCHAR(255),
createdOn  VARCHAR(255)
);