#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

def showMenu():
    print "\n +--------------------------------------------------------------------------------+"
    print "\n |              WELCOME TO THE TOURNAMENT APP                                     |"
    print "\n +--------------------------------------------------------------------------------+"
    print "\n | 'h': Show this menu.                                                           |"
    print "\n | '1': Show all tournaments.                                                     |"
    print "\n | '2': Show all players.                                                         |"
    print "\n | '3': Add a new tournament.                                                     |"
    print "\n | '4': Remove all information of one tournament.                                 |"
    print "\n | '5': Add players to a tournament.                                              |"
    print "\n | '6': Play with an existent tournament.                                         |"
    print "\n |     '6.1': Show the ID of the players in a tournament.                         |"
    print "\n |     '6.2': Show the match results of the last round.                           |"
    print "\n |     '6.3': Show the current standing list.                                     |"
    print "\n |     '6.4': Add a new round (get a list of pairs of players for the next round.)|"
    print "\n |     '6.5': Add the match results for a new round.                              |"
    print "\n |     '6.6': Remove all the match results of the last round.                     |"
    print "\n |     '6.7': Show the result after a selected round.                             |"
    print "\n | '7': Manage database.                                                          |"
    print "\n |     '7.1': Delete Tournaments table.                                           |"
    print "\n |     '7.2': Delete Players_Tournaments table.                                   |"
    print "\n |     '7.3': Delete Matches table.                                               |"
    print "\n |     '7.4': Delete Players table.                                               |"
    print "\n | 'q': quit.                                                                     |"
    print "\n +--------------------------------------------------------------------------------+"

def mainloop():
    showMenu()
    option = 'h'
    while option != 'q':

        option = raw_input("\n PLEASE SELECT AN OPTION (Enter 'h' for help): ")

        if option == 'h':
            showMenu()
        elif option == '1':
            print "\n ....'1': Show all tournaments................................................."
            showTournaments()
        elif option == '2':
            print "\n ....'2': Show all players....................................................."
            showPlayers()
        elif option == '3':
            print "\n ....'3': Add a new tournament................................................."
            addNewTournament()
        elif option == '4':
            print "\n ....'4': Remove all information of one tournament............................."
            deleteTournament()
        elif option == '5':
            print "\n ....'5': Add players to a tournament.........................................."
            addPlayers()
        elif option == '6.1':
            print "\n ........'6.1': Show the ID of the players in a tournament....................."
            showPlayersInTournament()
        elif option == '6.2':
            print "\n ........'6.2': Show the match results of the last round......................."
            showLastRound()
        elif option == '6.3':
            print "\n ........'6.3': Show the current standing list................................."
            showCurrentStandingList()
        elif option == '6.4':
            print "\n ........'6.4': Add a new round (get a list of pairs of players)..............."
            addNewRound()
        elif option == '6.5':
            print "\n ........'6.5': Add the match results for a new round.........................."
            reportMatchResults()
        elif option == '6.6':
            print "\n ........'6.6': Remove all the match results of the last round................."
            deleteLastRound()
        elif option == '6.7':
            print "\n.........'6.7': Show the result after a selected round........................."
            showSelectedRound()
        elif option == '7.1':
            print "\n.........'7.1': Delete Tournaments table......................................."
            deleteTournamentsTable()
        elif option == '7.2':
            print "\n.........'7.2': Delete Players_Tournaments table.  ............................"
            deletePlayers_TournamentsTable()
        elif option == '7.3':
            print "\n.........'7.3': Delete Matches table..........................................."
            deleteMatchesTable()
        elif option == '7.4':
            print "\n.........'7.4': Delete Players table.........................................."
            deletePlayersTable()
        elif option != 'q':
            print "\n You entered a wrong option."
        print "\n******************************************************************************\n"

if __name__ == '__main__':
    mainloop()
