-- Table definitions for the tournament project.
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

drop function if exists players_fn(integer);
drop function if exists views_fn(integer, integer);
drop function if exists matches_fn(integer, integer);
drop function if exists matches_number_fn(integer, integer);
drop function if exists opponent_wins_fn(integer, integer);
drop function if exists total_opponent_wins_fn(integer, integer);

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
--                                     in 1 round the two players must have only 1 match.
--player_win CONSTRAINT:  win = match winner id or (-1) to represent a draw.

CREATE TABLE OneRoundMatches(p1 INTEGER REFERENCES Players(id),
		p2 INTEGER REFERENCES Players(id),
		win INTEGER,
		PRIMARY KEY (p1,p2),
		CONSTRAINT player_order CHECK (p1 < p2),
		CONSTRAINT player_win CHECK (win = p1 OR win = p2 OR win = -1)
);
--This table is used temporarily when user record the match result, it helps to check the constraint.
--player_order CONSTRAINT and PRIMARY KEY(p1,p2): to ensure that 
--              the two players must have only 1 match in 1 round. 
--player_win CONSTRAINT: win = match winner id or (-1) to represent a draw.
-----------------------------------------------------------------------------------
-- players_fn and matches_fn will have data for tournament "tourNum" and 
-- all the rounds not after "roundNum.

create or replace function players_fn(tourNum integer)
  returns table (id integer, name text)
as
$body$
  select * from Players p where p.id in
				(select pt.player_id from Players_Tournaments pt where tourNumber = $1)
$body$
language sql;
-----------------------------------------------------------------------------------
create or replace function matches_fn(tourNum integer, roundNum integer)
  returns table (roundNumber integer, p1 integer, p2 integer, win integer)
as
$body$
	select roundNumber, p1, p2, win from Matches where tourNumber = $1 and roundNumber <= $2
$body$
language sql;
-----------------------------------------------------------------------------------
-- Calculate the number of matches for each player, eliminate the dummy player (id = 0).

create or replace function matches_number_fn(tourNum integer, roundNum integer)
  returns table (id integer, name text, matches integer)
as
$body$
	select p.id, name, count(win)::integer
		from players_fn($1) p left join (select * from matches_fn($1, $2) where p1 != 0 and p2 != 0) m
		on (p.id = m.p1) or (p.id = m.p2)
		group by p.id, name;
$body$
language sql;
-----------------------------------------------------------------------------------
-- Calculate the number of wins for each player.
create or replace function wins_fn(tourNum integer, roundNum integer)
  returns table (id integer, name text, wins integer)
as
$body$
	select p.id, name, count(m.win)::integer
		from players_fn($1) p left join matches_fn($1, $2) m 
		on (p.id = m.win) 
		group by p.id, name;
$body$
language sql;
-----------------------------------------------------------------------------------
-- Calculate the number of win for each player's opponents:
create or replace function opponent_wins_fn(tourNum integer, roundNum integer)
  returns table (id integer, opp_win integer)
as
$body$
	select p.id, w.wins from players_fn($1) p, wins_fn($1, $2) w 
		where w.id in ((select p1 from matches_fn($1, $2) where p2 = p.id) 
						union 
						(select p2 from matches_fn($1, $2) where p1 = p.id));
$body$
language sql;
-----------------------------------------------------------------------------------
create or replace function total_opponent_wins_fn(tourNum integer, roundNum integer)
  returns table (id integer, opp_wins integer)
as
$body$
	select id, sum(opp_win)::integer from opponent_wins_fn($1, $2) group by id;
$body$
language sql;
-----------------------------------------------------------------------------------

INSERT INTO Players VALUES (0, 'Dummy');
