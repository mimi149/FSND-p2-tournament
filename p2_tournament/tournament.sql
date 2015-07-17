-- Table definitions for the tournament project.

-- Create database "tournament" and connect to that database before creating tables
\c vagrant
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players CASCADE;

CREATE TABLE Players (
                        id SERIAL PRIMARY KEY,
                        name TEXT
);
CREATE TABLE Matches (  
                        id SERIAL PRIMARY KEY,
                        p1 INTEGER REFERENCES Players(id), 
                        p2 INTEGER REFERENCES Players(id), 
                        win INTEGER REFERENCES Players(id)
                        CONSTRAINT win CHECK (win = p1 OR win = p2)
);
