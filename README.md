# p2_tournament
Tournament - Project 2 for Udacity's Full Stack Developer Nanodegree Program

A / -Project Description: Tournament Planner

This project has a Python module that uses the PostgreSQL database to keep track of players and matches
    in game tournaments.

The game tournament uses the Swiss system for pairing up players in each round:
    players are not eliminated, and each player should be paired with another player with the same number of wins,
    or as close as possible.

The project implements all of the requirements of the Udacity's Full Stack Developer Nanodegree Program 
  for the project number 2, plus all of its suggestions for the extra credit, plus one more one.

The Extra credit:

1. Allow the odd number of players.If there is an odd number of players,
       one player is assigned a“ bye”(skipped round).
                                   
   A bye counts as a free win
   A player should not receive more than one bye in a tournament.

2. Support games where a draw(tied game) is possible.
    

3. When two players have the same number of wins, they are ranked according to OMW
    (Opponent Match Wins), the total number of wins by players they have played against.

4. Support more than one tournament in the database, so matches do not have to be deleted between tournaments.
        

5. One more extra credit: The project allows to see the result of any previous round in any tournament.


B / -Options of the project:

1. Add a new tournament.

2. Choose to see and update the match result of an existent tournament
    

3. Register for the new tournament:

    - Add a new player, or 
    - Choose an existent player.

4. See the result of any round of any existent tournament.

5. Record the match results of a new round of some tournament.

6. Delete the match results of the last round of any tournament 
   (in case the user want to repair some recently recorded data.)
