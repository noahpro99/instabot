-- create instagram database

CREATE DATABASE instagram;


CREATE DATABASE test_instagram;


CREATE TABLE users (username VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
                                                               name VARCHAR(255),
                                                                    bio VARCHAR(255),
                                                                        posts INT, followers INT, following INT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE messages (id SERIAL PRIMARY KEY NOT NULL UNIQUE,
                                                      sender VARCHAR(255) NOT NULL,
                                                                          receiver VARCHAR(255) NOT NULL,
                                                                                                message VARCHAR(255) NOT NULL,
                                                                                                                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);