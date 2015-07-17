"""!/usr/bin/env python

 tournament.py -- implementation of a Swiss-system tournament
"""
from random import randint
from math import log, ceil
import psycopg2
MAX_NUMBER_OF_PLAYERS = 16

def connect():
    """ Connect to the PostgreSQL database. Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def db_CRUD(sqlList):
    """ execute every sql in sqlList and return the result of the last one."""
    conn = connect()
    c = conn.cursor()
    for sql in sqlList:
        c.execute(sql["sql"].format(*sql["args"]))
    try:
        result = c.fetchall()
    except:
        result =  []
    conn.commit()
    conn.close()
    return result

def countPlayers(tourNum):
    """ Returns the number of players currently registered for the tournament "tourNum"."""
    result = db_CRUD([{"sql" : "select count(*) from Players_Tournaments where tourNumber = {0};",
                       "args" : [tourNum]}]
             )
    return int(result[0][0])

def registerPlayer(name):
    """ Adds a player to the tournament database.
    The database assigns a unique serial id number for the player. (This will be handled by
    SQL database schema, not in Python code.)
    Args:
        name: the player's full name (need not be unique).
    """
    result = db_CRUD([{"sql" : "insert into Players (id, name) values (DEFAULT, '{0}') returning id;",
                       "args" : [name]}]
             )
    return result[0][0] # return the id of the new player.

def playerStandings(tourNum, roundNum):
    """ Using functions: matches_number_fn(), wins_fn(), and total_opponent_wins_fn().

    Returns a list of the players and their win records at the end of the round "roundNum"
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
    result = db_CRUD([{"sql" :"select t1.id, name, wins, opp_wins, matches \
                               from (select p.id as id, p.name as name, wins, matches \
                                     from matches_number_fn({0}, {1}) p \
                                          left join wins_fn({0}, {1}) w \
                                          on p.id = w.id) t1 \
                                    left join total_opponent_wins_fn({0}, {1}) t2 \
                                    on t1.id = t2.id \
                               order by wins desc, opp_wins desc;",

                       "args" : [tourNum, roundNum]}]
             )

    standingList = [row for row in result if row[0] != 0] # eliminate dummy player if exists.
    return standingList

def swissPairings(tourNum, roundNum):
    """ Call functions setByePlayer, playerStandings.

    Returns a list of pairs of players for the next round of a tournament.

    The playersList is taken from the Players_Tournaments table for that tournament "tourNum".
    If there were some rounds of that tournament, the playersList will be updated from the standingList.

    Each player appears exactly once in the pairings. Each player is paired with another
    player with an equal or nearly-equal win record, it means, a player adjacent
    to him or her in the standings.

    Returns the pairingList:
        A list of tuples, each of which contains (id1, name1, id2, name2)
            id1: the first player's unique id
            name1: the first player's name
            id2: the second player's unique id
            name2: the second player's name
    """

    pairingList, playersList, byePlayer = setByePlayer(tourNum)

    # If there are some rounds of the tournament, take a playersList from a standingList.
    result = db_CRUD([{"sql" :"select * from Matches where tourNumber = {0};",
                       "args" : [tourNum]}]
             )

    if result != []:
        standingList = playerStandings(tourNum, roundNum)
        playersList = [(row[0], row[1])  for row in standingList if row[0] != byePlayer]

    for i,row in enumerate(playersList):
        if i%2 == 0:
            [c1, c2] = [row[0], row[1]]
        else:
            [c3, c4] = [row[0], row[1]]
            pairingList.append((c1, c2, c3, c4))

    return pairingList

def setByePlayer(tourNum):
    """ If the player number is odd:
            - a player is set to a "bye player" by random.
            - Once someone is set to a bye player, the info is written to the Players_Tournaments table,
              to ensure that he or she is a bye player no more than one time in a tournament.
            - The pairingList will be added a pair of that bye player with the dummy player.
            - The playersList will be eliminated that player.

            (A dummy player is a player with the id = 0, it is inserted to the Players table
             at the begining to be used in some algorithms in the program)

            return a pairingList with the first pair of the byePlayer with the dummy player,
                   a playersList, and byePlayer is set to byePlayer ID.

        If the player number is even:
           return an empty pairingList, a playersList, and byePlayer is set to 0.
    """

    pairingList = []
    byePlayer = 0

    result = db_CRUD([{"sql" : "select p.id, name, bye \
                                from players p join Players_Tournaments pt \
                                               on p.id = pt.Player_id \
                                where tourNumber = {0} and p.id <> 0;",
                        "args" : [tourNum]}]
             )

    playersList = result

    playerNum = len(playersList)
    if playerNum % 2 != 0:

        r = randint(0, playerNum - 1)
        count = 0
        while byePlayer == 0:
            if playersList[r][2] == 0: # The bye attribute is still equal 0 in this tournament.
                byePlayer = playersList[r][0] # The id of the chosen bye player.

                pair = (playersList[r][0], playersList[r][1], 0, "")
                pairingList.append(pair) # a pair of the bye player and the dummy player.

                db_CRUD([{"sql" : "update Players_Tournaments set bye = 1 \
                                   where player_id = {0} and tourNumber = {1};",
                          "args" : [playersList[r][0], tourNum]}]
                )

                playersList = playersList[0:r] + playersList[r+1:] # eliminate the bye player.

            else:
                r = (r + 1) % playerNum  # try to find another player with bye attribute is still equal 0.
            count += 1

            if count > playerNum:
                raise ValueError("The round number is over the actual available round of the tournament.")
                # Actually, we always found the new byePlayer because the number of rounds is equal
                # ceil(log2(playerNum)). So the loop will never be infinite loop.

    return pairingList, playersList, byePlayer

def removeByePlayer(tourNum, lastRoundNum):
    """ When some round is aborted the byePlayer of that round if exists must be reset,
        so that he or she can be a byePlayer for some further round.
    """
    result = db_CRUD([{"sql" : "select * from Matches where tourNumber = {0} and roundNumber = {1};",
                       "args" : [tourNum, lastRoundNum]}])
    for match in result:
        if match[2] == 0 or match[3] == 0:
            byePlayer = match[2] if match[3] == 0 else match[3]

            db_CRUD([{"sql" : "update Players_Tournaments set bye = 0 \
                               where player_id = {0} and tourNumber = {1};",
                      "args" : [byePlayer, tourNum]}]
            )

def selectTournament():
    tourNum = raw_input("\n Enter the ID of the tournament: ")

    result = db_CRUD([{"sql" : "select * from Tournaments where id = {0};",
                       "args" : [tourNum]}]
             )

    if result != []:
        print "\n Welcome to the tournament ", result[0][1]
    else:
        raise ValueError("Invalid tournament ID.")

    result = db_CRUD([{"sql" : "select max(roundNumber) from Matches where tourNumber = {0};",
                       "args" : [tourNum]}]
             )
    result = result[0]
    lastRoundNum = 0 if result[0] == None else int(result[0])

    if lastRoundNum > 0:
        print "\n There have already been ", lastRoundNum," round(s)."
    else:
        print "\n There is not any round."

    return tourNum, lastRoundNum

def deleteRound(tourNum, lastRoundNum):
    """ Delete all the match records of the last round of the tournament 'tourNum'.
        The bye player in that round if exists will be reset so that he or she can be a
        bye player for some further round in this tournament.
    """
    removeByePlayer(tourNum, lastRoundNum)
    db_CRUD([{"sql" : "delete from Matches where tourNumber = {0} and roundNumber = {1};",
              "args" : [tourNum, lastRoundNum]}]
    )

def showRound(tourNum, roundNum):
    """ Show match results and the standingList of the rounds not later than 'roundNum' in the tournament 
        'tourNum'."""
    showMatches(tourNum, roundNum)
    standingList = playerStandings(tourNum, roundNum)
    showRows("Standing list:\n\n player_id, name, wins, opp_wins, matches", standingList)

def newRound(tourNum, roundNum):
    """ Get a list of pairs of players for the round 'roundNum' of the tournament 'tourNum' 
        and write to database (Matches table)."""
    pairingList = swissPairings(tourNum, roundNum)

    insertPairs(pairingList, tourNum, roundNum)
    showMatches(tourNum, roundNum)

def showMatches(tourNum, roundNum):
    """ Show match info of all the round not later than the round "roundNum" in the tournament "tourNum"."""

    result = db_CRUD([{"sql" : "select * from Matches where tourNumber = {0} and roundNumber <= {1};",
                       "args" : [tourNum, roundNum]}]
             )

    showRows("Matches table:\n\n tourNumber, roundNumber, player1, player2, winner (-1 means draw)", result)

def insertPairs(pairingList, tourNum, roundNum):
    """ Write the list of pairs of players for the round 'roundNum' in the tournament 'tourNum' 
        to database (Matches table)."""
    sqlList = []
    for row in pairingList:
        p1, p1name, p2, p2name = row

        if p1 > p2:
            p = p1
            p1 = p2
            p2 = p

        sqlList.append({"sql" : "insert into Matches values ({0}, {1}, {2}, {3});",
                        "args" : [tourNum, roundNum, p1, p2]}
        )
    db_CRUD(sqlList)
    
def matchResults(tourNum, roundNum):
    """ Allow to report the match results."""
    
    result = db_CRUD([{"sql" : "select p1, p2 from Matches \
                                where tourNumber = {0} and roundNumber = {1} and win is null;",
                       "args" : [tourNum, roundNum]}]
             )
    if result == []:
        print "\n You must select the option '6.4- Add a new round' first."
        return False
    else:
        print '\n\n Report match results: '
        print "\n    Please enter the id of the winner or -1 for a draw match:"

        sqlList = []
        for row in result:
            p1, p2 = row

            if p1 == 0 or p2 == 0: # a byePlayer is paired with the dummy player with id = 0.
                winner = p1 if p2 == 0 else p2
            else:
                print '\n   Match between ', p1, ' and ', p2, ':'
                winner = int(raw_input("                            winner: "))

            if winner in [-1, p1, p2]:
                sqlList.append({"sql" : "update Matches set win = {0} \
                                         where tourNumber = {1} and roundNumber = {2} \
                                               and p1 = {3} and p2 = {4};",
                                "args" : [winner, tourNum, roundNum, p1, p2]}
                )
            else:
                raise ValueError("You entered a wrong number.")

        db_CRUD(sqlList)
        return True

def showRows(rowsName, rows):
    print '\n', rowsName, '\n'
    for row in rows:
        print row

#-------------------------------------------------------------------------------------------#
# Functions called from main menu:

def showTournaments():
    result = db_CRUD([{"sql" : "SELECT * FROM tournaments;", "args" : []}])
    showRows("Tournaments:\n\n tourNumber, name", result)

def showPlayers():
    result = db_CRUD([{"sql" : "SELECT * FROM players;", "args" : []}])
    showRows("Players:\n\n id, name", result)

def addNewTournament():

    name = raw_input("\nEnter the name of the new tournament: ")
    db_CRUD([{"sql" : "insert into Tournaments (id, name) values (DEFAULT, '{0}');",
              "args" : [name]}]
    )

def deleteTournament():
    """ Delete the selected tournament. All the records in Players_Tournaments related to this tournament
        will be deleted on cascade.
        This in its turn calls to delete all the related matches in Matches on cascade.
    """
    delete_id = raw_input("\nEnter the id of an existent tournament: ")
    db_CRUD([{"sql" : "delete from Tournaments where id = {0};", "args" : [delete_id]}])

def addPlayers():
    """ Allows to add all players for a tournament."""

    playersList = []
    tourNum, lastRoundNum = selectTournament()
    playerNum = countPlayers(tourNum)

    if playerNum > 0:
        raise ValueError("\nThis tournament already has players.")

    print '\n\n Register for players: '

    playerNumber = raw_input("\nEnter the number of players: (>0 and <={0})  ".format(MAX_NUMBER_OF_PLAYERS))

    playerNumber = int(playerNumber)
    if playerNumber <= 0 or playerNumber > MAX_NUMBER_OF_PLAYERS:
        raise ValueError("\nYou enter a wrong number.")

    if playerNumber % 2 != 0: # Add a dummy player to this tournament.
        playersList.append({"sql" : "insert into Players_Tournaments values ({0}, 0, 0);",
                            "args" : [tourNum]}
        )

    for i in range(playerNumber):
        print "\n Player number {0}:".format(i+1)
        option = raw_input("\n    Select (1) to add a new player or (2) to choose an existent player. ")

        if option == '1':
            name = raw_input("Enter the name of the player {0}: ".format(i+1))
            player_id = registerPlayer(name)
        else:
            player_id = raw_input("\nEnter the id of the existent player: ")
            player_id = int(player_id)

            result = db_CRUD([{"sql" :"select id, name from Players where id = {0} and id <> 0;",
                               "args" : [player_id]}]
                     )

            if result == []:
                raise ValueError("The player id is not exist.")
            else:
                showRows("Players:\n\n id, name", result[0])

        playersList.append({"sql" :"insert into Players_Tournaments values ({0}, {1}, 0);",
                            "args" : [tourNum, player_id]}
        )
    db_CRUD(playersList)

def showPlayersInTournament():
    tourNum, lastRoundNum = selectTournament()
    result = db_CRUD([{"sql" : "SELECT * FROM players_tournaments where tourNumber = {0};",
                       "args" : [tourNum]}]
             )
    showRows("Players_Tournaments table: (bye=1 means the player is a byePlayer in some round)\
              \n\n tourNumber, player_id, bye", result)

def showLastRound():
    tourNum, lastRoundNum = selectTournament()
    if lastRoundNum > 0:
        showRound(tourNum, lastRoundNum)

def showCurrentStandingList():
    tourNum, lastRoundNum = selectTournament()
    if lastRoundNum > 0:
        standingList = playerStandings(tourNum, lastRoundNum)
        showRows("Standing list:\n\n player_id, name, wins, opp_wins, matches", standingList)

def addNewRound():
    """ Add a new round (get a list of pairs of players for the next round."""
    
    tourNum, lastRoundNum = selectTournament()
    playersNum = countPlayers(tourNum)
    if playersNum > 0:
        max_round = log(playersNum,2)
        if lastRoundNum >= ceil(max_round):
            raise ValueError("There has already been the final round.")
        newRound(tourNum, lastRoundNum+1)
    else:
         print "\n You must choose the option '5- Add players to a tournament' first."

def reportMatchResults():
    tourNum, roundNum = selectTournament()
    if matchResults(tourNum, roundNum):
        showMatches(tourNum, roundNum)
        standingList = playerStandings(tourNum, roundNum)
        showRows("Standing list:\n\n player_id, name, wins, opp_wins, matches", standingList)

def deleteLastRound():
    tourNum, lastRoundNum = selectTournament()
    if lastRoundNum > 0:
        deleteRound(tourNum, lastRoundNum)
        print "\n All the match results of the round {0} have been removed".format(lastRoundNum)

def showSelectedRound():
    """ Show all the match results not after the selected round."""
    
    tourNum, lastRoundNum = selectTournament()

    if lastRoundNum > 0:
        roundNum = raw_input("\nEnter the number of the round (>0 and <={0}): "\
                                .format(lastRoundNum))
        roundNum = int(roundNum)
        if roundNum > lastRoundNum or roundNum < 1:
            raise ValueError("\nThe round number must be > 0 and <= {0}.".format(lastRoundNum))
        else:
            showRound(tourNum, roundNum)

def deleteTournamentsTable():
    """ Remove all the tournament from the database.
        All the records in Players_Tournaments will be deleted on cascade.
        This in its turn calls to delete all the matches in Matches on cascade.
    """
    db_CRUD([ {"sql" : "delete from Tournaments;", "args" : [] } ])

def deletePlayers_TournamentsTable():
    """ Remove all the records from the Players_Tournaments table.
        All the matches in Matches will be deleted on cascade.
    """
    db_CRUD([{"sql" : "delete from Players_Tournaments;", "args" : []}])

def deleteMatchesTable():
    """ Remove all the matches from the database.
        Need to remove all the bye setting for all the players in all tournaments.
    """
    sqlList = [{"sql" : "update Players_Tournaments set bye = 0;", "args" : []},
               {"sql" : "delete from Matches;", "args" : []}]
    db_CRUD(sqlList)

def deletePlayersTable():
    """ Remove all the players from the database except the dummy player.
        All the matches in Matches will be deleted on cascade.
        All the records in Players_Tournaments will be deleted on cascade also.
    """
    db_CRUD([ {"sql" : "delete from Players where id <> 0;", "args" : [] } ])

#-------------------------------------------------------------------------------------------#

