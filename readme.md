## p2_tournament

Project 2 for Udacity's Full Stack Developer Nanodegree Program

### Project Description: Tournament Planner

This project has a Python module that uses the PostgreSQL database to keep track of players and matches in game tournaments.

The game tournament uses the Swiss system for pairing up players in each round.
Players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

##### The first version of this program (in the unit_test branch) can pass these tests:
1. deleteMatches: Remove all the matches records from the database.
2. deletePlayers: Remove all the player records from the database.
3. countPlayers: Returns the number of players currently registered.
4. registerPlayer: Adds a player to the tournament database.
5. playerStandings: Returns a list of the players and their win records, sorted by wins.
6. reportMatch: This is to simply populate the matches table and record the winner and loser as (winner,loser) in the insert statement.
7. swissPairings: Returns a list of pairs of players for the next round of a match.

##### The second version of this program (in the master branch) has the following functions:

1. Show all tournaments.
2. Show all players.
3. Add a new tournament.
4. Remove all information of a tournament.
5. Add players to a tournament.
6. Play with an existent tournament.
  - Show the players in a tournament.
  - Show the match results of the last round.
  - Show the current standing list.
  - Add a new round.
  - Add the match results for a new round.
  - Remove all the match results of the last round.
  - Show the result after a selected round.
7. Manage database.
  - Delete Tournaments table.
  - Delete Players_Tournaments table.
  - Delete Matches table.
  - Delete Players table.

##### This second version of the program has all the following extra credit :

1. Allow the odd number of players. If there is an odd number of players, one player is assigned a 'bye' (skipped round). A bye counts as a free win. A player should not receive more than one bye in a tournament.
2. Support games where a draw (tied game) is possible.
3. When two players have the same number of wins, they are ranked according to OMW
 (Opponent Match Wins), the total number of wins by players they have played against.
4. Support more than one tournament in the database, so matches do not have to be deleted between tournaments.
5. One more extra credit: allow to see the standing list after any round in any tournament.

### Project Package

**README.md**: this file.

**tournament.sql**: contains all the commands to create tournament database. You can see the explanation of database design here.

**tournament.py**: contains all the necessary functions.

**tournament_test.py**: contains the main menu function.

**pg_config.sh**: helps to create the virtual machine and install PostgreSQL when running vagrant up.

### Project Usage

1. First, you need to install VirtualBox (https://www.virtualbox.org/wiki/Downloads) and Vagrant (href="https://www.vagrantup.com/downloads) to your machine.
2. Next, clone this repo and navigate to the project folder:
```
	$ cd p2_tournament/
```
3. Type vagrant up to launch your virtual machine. This will take some time in your first run, because it needs to install some dependencies.
```
	p2_tournament$vagrant up
```
4. Once it is up and running, type vagrant ssh to log into it. This will log your terminal in to the virtual machine, and you'll get a Linux shell prompt.
```
	p2_tournament$vagrant ssh
```
5. On your virtual machine, go to /vagrant/p2_tournament folder and create the database by running psql.
```
	~$cd /vagrant/p2_tournament
	/vagrant/p2_tournament$ psql
	vagrant=> \i tournament.sql
	tournament=> \q
```

6. Run the program and you will see the menu.

```
	/vagrant/p2_tournament$python tournament_test.py
```
