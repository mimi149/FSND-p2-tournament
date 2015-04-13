-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

CREATE TABLE Players (
                        id SERIAL PRIMARY KEY,
                        name TEXT
);
CREATE TABLE Matches (  
                        id SERIAL PRIMARY KEY,
                        p1 INTEGER REFERENCES Players(id), 
                        p2 INTEGER REFERENCES Players(id), 
                        win INTEGER REFERENCES Players(id)
                        CONSTRAINT win CHECK (win = p1 OR win = p2) \
);
