#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#
from random import randint
from math import log, ceil
import psycopg2

MAX_ROUND = 10

def connect():
	"""Connect to the PostgreSQL database.  Returns a database connection."""
	return psycopg2.connect("dbname=tournament")

def dropTable():
	conn = connect()
	c = conn.cursor()
	c.execute("drop table if exists Matches;")
	c.execute("drop table if exists OneRoundMatches;")
	c.execute("drop table if exists Players_Tournaments;")
	c.execute("drop table if exists Players;")
	c.execute("drop table if exists Tournaments;")
	conn.commit()
	conn.close()


def deleteMatches():
	"""Remove all the match records from the database."""
	conn = connect()
	c = conn.cursor()
	c.execute("delete from OneRoundMatches;")
	c.execute("delete from Matches;")
	conn.commit()
	conn.close()

def deletePlayers():
	"""Remove all the player records from the database."""
	conn = connect()
	c = conn.cursor()
	c.execute("delete from OneRoundMatches;")
	c.execute("delete from Matches;")
	c.execute("delete from Players;")
	conn.commit()
	conn.close()

def countPlayers(tourNum):
	"""Returns the number of players currently registered for the tournament "tourNum"."""
	conn = connect()
	c = conn.cursor()
	c.execute("select count(*) from Players_Tournaments where tourNumber = %s;", (tourNum,))
	count = c.fetchone()[0]
	conn.commit()
	conn.close()
	return count

def registerPlayer(name):
	"""Adds a player to the tournament database.
	The database assigns a unique serial id number for the player.  (This
	should be handled by your SQL database schema, not in your Python code.)
	Args:
		name: the player's full name (need not be unique).
	"""
	conn = connect()
	c = conn.cursor()

	c.execute("insert into Players (id, name) values (DEFAULT, %s) returning id", (name,))
	player_id = c.fetchone()[0]
	
	conn.commit()
	conn.close()
	return player_id

def playerStandings(tourNum, roundNum = MAX_ROUND):
	"""Returns a list of the players and their win records at the end of the round "roundNum"
	of the tournament "tourNum", sorted by wins and the total wins of the player's opponents.

	The first entry in the list should be the player in first place, or a player
	tied for first place if there is currently a tie.

	Returns:
	  A list of tuples, each of which contains (id, name, wins, opp_wins, matches):
		id: the player's unique id (assigned by the database)
		name: the player's full name (as registered)
		wins: the number of matches the player has won
		opp_wins: the number of matches the player's opponents has won
		matches: the number of matches the player has played
	"""
	conn = connect()
	c = conn.cursor()

	c.execute("select t1.id, name, wins, opp_wins, matches from \
		(select p.id as id, p.name as name, wins, matches \
		from matches_number_fn({0}, {1}) p left join wins_fn({0}, {1}) w\
		on p.id = w.id) t1 \
		left join total_opponent_wins_fn({0}, {1}) t2 \
		on t1.id = t2.id \
		order by wins desc, opp_wins desc;".format(tourNum, roundNum))
	standing = c.fetchall()
	standingList = [row for row in standing if row[0] != 0] # eliminate Dummy player if exists.
	conn.commit()
	conn.close()
	return standingList

def reportMatch(p1, p2, result):
	"""Records the outcome of a single match between two players.
	This function use OneRoundMatches table to ensure an eligible match between the two players.
	(p1 < p2, and (p1, p2) is the primary key of the table.)
	Args:
		p1, p2 :  the id number of the players
		result=-1 for the draw match, otherwise, result is the id number of the winner.
	"""

	conn = connect()
	c = conn.cursor()

	if p1 == p2:
		raise ValueError("The players must be the two different players.")
	elif p1 > p2:
		p = p1
		p1 = p2
		p2 = p

	c.execute("insert into OneRoundMatches values ({0}, {1}, {2})".format(p1, p2, result))
	conn.commit()
	conn.close()

def swissPairings(tourNum):
	""" Call function playerStandings"""
	
	"""Returns a list of pairs of players for the next round of a match.

	The playersList is taken from the Players_Tournaments table for that tournament "tourNum".
	If there were some rounds of that tournament, the playersList will be updated from the standingList.

	Each player appears exactly once in the pairings.  Each player is paired with another
	player with an equal or nearly-equal win record, that is, a player adjacent
	to him or her in the standings.
	
	If the player number is odd:
		- a player is set to a "bye player" by random.
		- Once someone is set to a bye player, the info is written to the Players_Tournaments table, 
			to ensure that he or she is a bye player no more than one time in a tournament.
		- The pairingList will be added a pair of that bye player with the dummy player.
		- The playersList will be eliminated that player.

		(A dummy player is a player with the id = 0, it is inserted to the Players table at the begining 
		to be used in some algorithms in the program) 
	
	Returns the pairingList:
		A list of tuples, each of which contains (id1, name1, id2, name2)
		id1: the first player's unique id
		name1: the first player's name
		id2: the second player's unique id
		name2: the second player's name
	"""
	conn = connect()
	c = conn.cursor()

	pairingList = []

	c.execute("select p.id, name, bye from players p join Players_Tournaments pt on p.id = pt.Player_id \
				where tourNumber = %s and p.id <> 0;", (tourNum,))
	playersList = c.fetchall()
	byePlayer = 0       # byePlayer will be set to the id of the choosen bye player.
						# Actually, we always found the new byePlayer because 
						# the number of round is equal ceil(log2(playerNum)). 
						# So the loop will never be infinite loop.

	playerNum = len(playersList)
	if playerNum % 2 != 0:
		r = randint(0, playerNum - 1)
		count = 0
		while byePlayer == 0: 
			if playersList[r][2] == 0: # The bye attribute is still equal 0 in this tournament.
				byePlayer = playersList[r][0] # The id of the chosen bye player.

				pair = (playersList[r][0], playersList[r][1], 0, "") 
				pairingList.append(pair) # for the bye player with the dummy player.

				c.execute("update Players_Tournaments set bye = 1 \
						where player_id = %s and tourNumber = %s;", (playersList[r][0], tourNum,))

				playersList = playersList[0:r] + playersList[r+1:] # eliminate the bye player.

			else:
				r +=1               # try to find another player with bye attribute is still equal 0.
				if r == playerNum:
					r = 0
			count += 1

			if count > playerNum:
				raise ValueError("The round number is over the actual available round of the tournament.")

	# Check if it is the first round of the tournament:
	c.execute("select * from Matches where tourNumber = %s;", (tourNum,))
	rows = c.fetchall()
	if len(rows) > 0: # There are some rounds of this tournament, take the standingList:
		standingList = playerStandings(tourNum)
		if byePlayer != 0: # There is a byePlayer that must not be in the playersList.
			playersList = []
			for row in standingList:
				if row[0] != byePlayer:
					playersList.append((row[0], row[1], 0))
		else:
			playersList = standingList

	for i,row in enumerate(playersList):
		if i%2 == 0:
			[c1, c2] = [row[0], row[1]]
		else:
			[c3, c4] = [row[0], row[1]]
			pair = (c1,c2,c3,c4)
			pairingList.append(pair)
	conn.commit()
	conn.close()
	return pairingList

def selectTour():
	""" Call function selectRound"""

	conn = connect()
	c = conn.cursor()
	c.execute("select * from Tournaments;")
	tours = c.fetchall()

	print '\n   Tournament List:'
	for tour in tours:
		print '\n  ', tour[0], ' - ', tour[1]
	print '\n\n\n   0  -  Make a new tournament'
	print '\n  -1  -  Delete all information of one tournament.'

	tourNum = raw_input("\nChoose your option (the id of the tournament or '0' or '-1'): ")
	print "\n------------------------------------------------------------------------------\n"
	tourNum = int(tourNum)

	if tourNum == 0:
		name = raw_input("\nEnter the name of the new tournament: ")
		print "\n------------------------------------------------------------------------------\n"

		c.execute("insert into Tournaments (id, name) values (DEFAULT, %s) returning id;", (name,))
		tourNum = c.fetchone()[0]
		conn.commit()
		addPlayers(tourNum)
	
	elif tourNum == -1:
		delete_id = raw_input("\nEnter the id of an existent tournament: ")
		print "\n------------------------------------------------------------------------------\n"

		c.execute("delete from Matches where tourNumber = %s", (delete_id,))
		c.execute("delete from Players_Tournaments where tourNumber = %s", (delete_id,))
		c.execute("delete from Tournaments where id = %s", (delete_id,))

	elif (tourNum < 0) or (tourNum not in [row[0] for row in tours]):
		raise ValueError("You enter a wrong number. ") 

	else:
		selectRound(tourNum)
	conn.commit()
	conn.close()
	return

def selectRound(tourNum):
	""" Call function addPlayer, oldRound, newRound"""
	
	conn = connect()
	c = conn.cursor()

	c.execute("select max(roundNumber) from Matches where tourNumber = %s;", (tourNum,))
	roundNumber = c.fetchone()

	if roundNumber[0] == None:
		roundNumber = 0
	else:
		roundNumber = int(roundNumber[0])
		
	c.execute("select * from Tournaments where id = %s;", (tourNum,))
	print "\n Welcome to the tournament ", c.fetchone()[1]
	
	print "\n There have already been ", roundNumber," rounds."

	print "\n\n 1- See an existent round."
	print "\n 2- Make a new round."
	print "\n 3- Delete all the match results of the last round."

	option = raw_input("\nChoose your option: ")
	print "\n------------------------------------------------------------------------------\n"

	if option == '1':
		oldRound(roundNumber, tourNum)
	elif option == '2':
		max_round = log(countPlayers(tourNum),2)
		if roundNumber >= ceil(max_round):
			raise ValueError("There has already been the final round.")
		newRound(roundNumber+1, tourNum)
	elif option == '3':
		deleteLastRound(tourNum)
	else:
		raise ValueError("You must enter 1 or 2 or 3.")
	conn.commit()
	conn.close()

def deleteLastRound(tourNum):
	""" Delete all the match record of the last round of the tournament tourNum"""

	conn = connect()
	c = conn.cursor()

	c.execute("select max(roundNumber) from Matches where tourNumber = %s;", (tourNum,))
	roundNumber = c.fetchone()
	if roundNumber[0] == None:
		print "\n There was not any round of that tournament."
	else:
		c.execute("delete from Matches where tourNumber = %s and roundNumber = %s;", \
					(tourNum, int(roundNumber[0])))
	conn.commit()
	conn.close()

def oldRound(roundNum, tourNum):
	""" Call function seeMatches, playerStandings, seeRows"""
	
	conn = connect()
	c = conn.cursor()
	roundNumber = raw_input("\nEnter the number of the round you want to see (>0 and <={0}): "\
							.format(roundNum))
	print "\n------------------------------------------------------------------------------\n"

	roundNumber = int(roundNumber)
	if roundNumber > roundNum or roundNumber < 1:
		raise ValueError("\nThe round number must be > 0 and <= {0}.".format(roundNum))
	else:
		seeMatches(roundNumber, tourNum)
		standingList = playerStandings(tourNum, roundNumber)
		seeRows("standing list: id, name, wins, opp_wins, matches", standingList)

	conn.commit()
	conn.close()

def newRound(roundNumber, tourNum):
	""" Call function swissPairings, recordMatchesResult, seeMatches, playerStandings, seeRows"""

	conn = connect()
	c = conn.cursor()

	pairingList = swissPairings(tourNum)
	
	recordMatchesResult(pairingList, roundNumber, tourNum)

	seeMatches(roundNumber, tourNum)
	standingList = playerStandings(tourNum)
	seeRows("standing list: id, name, wins, opp_wins, matches", standingList)
	conn.commit()
	conn.close()

def addPlayers(tourNum):
	""" Call function registerPlayer.
	
		All of the players of one tournament must be added at one time to commit, 
		otherwise, they must be aborted."""
	
	print '\n\n Register for players: '

	conn = connect()
	c = conn.cursor()
	playerNumber = raw_input("\nEnter the number of players: (>0 and <=16)  ")
	print "\n------------------------------------------------------------------------------\n"

	playerNumber = int(playerNumber)
	if playerNumber <= 0 or playerNumber > 16:
		raise ValueError("\nYou enter a wrong number.")
	if playerNumber % 2 != 0: # Add a dummy player to this tournament.
		c.execute("insert into Players_Tournaments values (%s, 0, 0);", (tourNum,))

	for i in range(playerNumber):
		print "\n 1 - Add a new player."
		print "\n 2 - Choose an existent player."
		option = raw_input("\nChoose your option: ")
		print "\n------------------------------------------------------------------------------\n"

		if option == '1':
			name = raw_input("Enter the name of the player {0}:".format(i+1))
			print "\n------------------------------------------------------------------------------\n"
			player_id = registerPlayer(name)
		else:
			player_id = raw_input("Enter the id of the exist player: ")
			print "\n------------------------------------------------------------------------------\n"

			player_id = int(player_id)
			c.execute("select id, name from Players where id = %s", (player_id,))
			player = c.fetchone()
			if player == None:
				raise ValueError("The required id is not exist.")
		c.execute("insert into Players_Tournaments values (%s, %s, 0)", (tourNum,player_id,))
		conn.commit()
	conn.close()

def seeMatches(roundNum, tourNum):
	""" Show match info of the round "roundNum" of the tournament "tourNum" """

	conn = connect()
	c = conn.cursor()
	c.execute("select * from Matches where roundNumber <= %s and tourNumber = %s;", (roundNum, tourNum,))
	rows = c.fetchall()
	seeRows("Matches table (tourNumber, round number, player1, player2, the winner (-1 means draw)):", rows)
	conn.commit()
	conn.close()

def recordMatchesResult(pairingList, roundNumber, tourNum):
	""" Call function: reportMatch.
		All match results of one round must be reported at one time to commit,
		otherwise, they would be aborted."""

	conn = connect()
	c = conn.cursor()

	print '\n\n Report match results: '

	c.execute("delete from OneRoundMatches")
	
	for row in pairingList:
		if row[2] == 0: # a byePlayer is paired with the Dummy player with id = 0. 
			reportMatch(0, row[0], row[0])
			continue
		print '\n                           ', row
		result = raw_input("Enter '{0}' (if player '{1}' won), \n  or  '{2}' (if player '{3}' won), \n  or  -1 (if draw)  \n \
		".format(row[0], row[0], row[2], row[2]))
		print "\n------------------------------------------------------------------------------\n"

		result = int(result)
		if result in [-1,row[0], row[2]]:
			reportMatch(row[0], row[2], result)
		else:
			raise ValueError("You entered a wrong number.")
	
	# Copy data of the new round to Matches table.
	c.execute("select * from oneRoundMatches;")
	rows = c.fetchall()
	for row in rows:
		c.execute("insert into Matches values (%s, %s, %s, %s, %s)", \
					(tourNum, roundNumber, row[0], row[1], row[2],))

	c.execute("delete from OneRoundMatches") # complete record all the match results for one round.

	conn.commit()
	conn.close()

def seeRows(rowsName, rows):
	print '\n', rowsName
	for row in rows:
		print row

def	showData():
	conn = connect()
	c = conn.cursor()
	print "\n------------------------------------------------------------------------------\n"
	print '\n Existent data:'
	c.execute("SELECT * FROM Players;")
	seeRows("Players: id, name", c.fetchall())
	c.execute("SELECT * FROM tournaments;")
	seeRows("Tournaments: tourNumber, name", c.fetchall())
	c.execute("SELECT * FROM players_tournaments;")
	seeRows("Players_Tournaments: tourNumber, player_id", c.fetchall())
	raw_input("Press Enter to continue.")
	print "\n------------------------------------------------------------------------------\n"

	conn.commit()
	conn.close()
