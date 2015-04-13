#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
	"""Connect to the PostgreSQL database.  Returns a database connection."""
	return psycopg2.connect("dbname=tournament")

def deleteMatches():
	"""Remove all the match records from the database."""

	conn = connect()
	c = conn.cursor()
	c.execute("delete from Matches;")
	conn.commit()
	conn.close()

def deletePlayers():
	"""Remove all the player records from the database."""

	conn = connect()
	c = conn.cursor()
	c.execute("delete from Players cascade;")
	conn.commit()
	conn.close()

def countPlayers():
	"""Returns the number of players currently registered."""

	conn = connect()
	c = conn.cursor()
	c.execute("select count(*) from Players;")
	row = c.fetchone()
	conn.commit()
	conn.close()
	return row[0]

def registerPlayer(name):
	"""Adds a player to the tournament database.

	The database assigns a unique serial id number for the player.  (This
	should be handled by your SQL database schema, not in your Python code.)

	Args:
		name: the player's full name (need not be unique).
	"""
	conn = connect()
	c = conn.cursor()
	c.execute("insert into Players (id, name) values (DEFAULT, %s)", (name,))
	conn.commit()
	conn.close()

def playerStandings():
	"""Returns a list of the players and their win records, sorted by wins.

	The first entry in the list should be the player in first place, or a player
	tied for first place if there is currently a tie.

	Returns:
	  A list of tuples, each of which contains (id, name, wins, matches):
		id: the player's unique id (assigned by the database)
		name: the player's full name (as registered)
		wins: the number of matches the player has won
		matches: the number of matches the player has played
	"""
	conn = connect()
	c = conn.cursor()
	c.execute("create view play_view (id, name, match_number) as select p.id, name, count(win) \
        from Players p left join Matches m \
		on (p.id = m.p1) or (p.id = m.p2) \
		group by p.id, name;")

	c.execute("create view win_view (id, name, win_number) as select p.id, name, count(m.win) \
        from Players p left join Matches m \
		on (p.id = m.win) \
		group by p.id, name;")

	c.execute("select play_view.id, play_view.name, win_number, match_number \
        from play_view join win_view \
		on play_view.id = win_view.id \
		order by win_number desc;")
	standing = c.fetchall()

	c.execute("drop view play_view;")
	c.execute("drop view win_view;")
	conn.commit()
	conn.close()

	return standing

def reportMatch(winner, loser):
	"""Records the outcome of a single match between two players.

	Args:
		winner:  the id number of the player who won
		loser:  the id number of the player who lost
	"""
	conn = connect()
	c = conn.cursor()
	if winner == loser:
		raise ValueError("The players must be the two different players.")
    
	c.execute("insert into Matches values (DEFAULT, {0}, {1}, {2})".format(winner, loser, winner))
	conn.commit()
	conn.close()
 
def swissPairings():
	"""Returns a list of pairs of players for the next round of a match.

	Assuming that there are an even number of players registered, each player
	appears exactly once in the pairings.  Each player is paired with another
	player with an equal or nearly-equal win record, that is, a player adjacent
	to him or her in the standings.

	Returns:
		A list of tuples, each of which contains (id1, name1, id2, name2)
		id1: the first player's unique id
		name1: the first player's name
		id2: the second player's unique id
		name2: the second player's name
	"""
	conn = connect()
	c = conn.cursor()

	standings = playerStandings()
	pairingList = []
	for i,row in enumerate(standings):
		if i%2 == 0:
			[c1, c2] = [row[0], row[1]]
		else:
			[c3, c4] = [row[0], row[1]]
			c = (c1,c2,c3,c4)
			pairingList.append(c)
	conn.commit()
	conn.close()
	return pairingList
