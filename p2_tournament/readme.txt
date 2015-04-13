Project 2 for Udacity's Full Stack Developer Nanodegree Program

Tournament Planner


This project has a Python module that uses the PostgreSQL database to keep track of players and matches in game tournaments. 

The game tournament uses the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible. 



Instruction:


1. Clone this repo and navigate to project folder:

$ cd p2_tournament/


2. Start up vagrant and wait for it to install any dependencies:

$ vagrant up


3. SSH into virtual machine:

$ vagrant ssh


4. Setup PostgreSQL:

$ cd /vagrant/p2_tournament
$ psql tournament

tournament=> \i tournament.sql
tournament=> \q


5. Run the program:

/vagrant/p2_tournament$python tournament_test.py
