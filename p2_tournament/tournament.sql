-- Table definitions for the tournament project.

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

drop table if exists Matches;
drop table if exists OneRoundMatches;
drop table if exists Players_Tournaments;
drop table if exists Players;
drop table if exists Tournaments;

CREATE TABLE Tournaments (
    id SERIAL PRIMARY KEY, 
    name TEXT
);

CREATE TABLE Players (
    id SERIAL PRIMARY KEY, 
    name TEXT
);

CREATE TABLE Players_Tournaments (
    tourNumber INTEGER REFERENCES Tournaments(id),
    player_id INTEGER REFERENCES Players(id),
    bye INTEGER,
    PRIMARY KEY (tourNumber, player_id));
-- bye = 0 by DEFAULT, it is set to 1 when the player is set to bye

CREATE TABLE Matches (
    tourNumber INTEGER, 
    roundNumber INTEGER,
    p1 INTEGER REFERENCES Players(id),
    p2 INTEGER REFERENCES Players(id),
    win INTEGER,
    PRIMARY KEY (tourNumber,roundNumber,p1,p2),
    CONSTRAINT player_order CHECK (p1 < p2),
    CONSTRAINT player_win CHECK (win = p1 OR win = p2 OR win = -1)
);

--player_order CONSTRAINT and PRIMARY KEY(tourNumber, roundNumber,p1,p2): to ensure that
--                      in 1 round of 1 tournament the two players must have only 1 match.
--player_win CONSTRAINT:  win = match winner id or (-1) to represent a draw.

CREATE TABLE OneRoundMatches(p1 INTEGER REFERENCES Players(id),
		p2 INTEGER REFERENCES Players(id),
		win INTEGER,
		PRIMARY KEY (p1,p2),
		CONSTRAINT player_order CHECK (p1 < p2),
		CONSTRAINT player_win CHECK (win = p1 OR win = p2 OR win = -1)
);
--This table is used temporarily when user record the match result for 1 round, 
--                                            it helps to check the constraints.
--player_order CONSTRAINT and PRIMARY KEY(p1,p2): to ensure that 
--              the two players must have only 1 match in 1 round. 
--player_win CONSTRAINT: win = match winner id or (-1) to represent a draw.


INSERT INTO Players VALUES (0, 'Dummy'); 
-- The dummy player is paired with the "bye player" for the odd number of players in a tournament.
