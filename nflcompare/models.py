

from flask_sqlalchemy import SQLAlchemy


DB = SQLAlchemy()

"""
We start from the bottom up and fill add non-redundant columns. Every table should be able to merge/join with each other at this point 
    - Once the play-by-play data is in Players we can write helper functions that merge/join/wrangles them all into any possible format we'd want. 
"""


class League(DB.Model):
    """
    A League has Teams, Players, Games, Coaches, Stadiums, Refs.

    Each one of these is related to each other but will ultimately converge through this table.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(20))
    year = DB.Column(DB.Integer())
    last_updated = DB.Column(DB.BigInteger())   # when was this league year last updated. Always helpful to know what data is lacking.

    def __repr__(self):
        return '<League {}>'.format(self.name)

class Organization(DB.Model):
    """
    We consider each season to be filled with 32 brand new teams.
        - Only reason to keep this would be for fun fact type articles. 
        - Not sure if it'll cause more harm than good but until then will keep. 
    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    league_id = DB.Column(DB.BigInteger, DB.ForeignKey(League.id), nullable=False)
    league = DB.relationship('League', backref=DB.backref('organizations', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<The {} organization.>'.format(self.name)

class teamSeason(DB.Model):
    """
    We consider each season to be filled with 32 brand new teams.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    year = DB.Column(DB.Integer())
    league_id = DB.Column(DB.BigInteger, DB.ForeignKey(League.id), nullable=False)
    organization = DB.relationship('Organization', backref=DB.backref('teamsSeason', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<teamSeason stats for the {} from the {} season.>'.format(self.organization, self.year)

class teamGame(DB.Model):
    """
    Each teamSeason plays many teamGames. 

    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    teamSeason_id = DB.Column(DB.BigInteger, DB.ForeignKey(League.id), nullable=False)
    teamSeason = DB.relationship('teamSeason', backref=DB.backref('teamGames', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<Team {}>'.format(self.name)

class Player(DB.Model):
    """
    Player main table.
    """
    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    league_id = DB.Column(DB.BigInteger, DB.ForeignKey(League.id), nullable=False)
    league = DB.relationship('League', backref=DB.backref('players', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<Player {}>'.format(self.name)

class playerSeason(DB.Model):
    """
    We consider each player/team, player/season, and player/team/season changes to mean a new player.
        - thus the Player <-> Team Relationship is many to many for a season
        - while only many -> one for any given game. Many players play for a team for any given game, but never more than one.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    team = DB.Column(DB.String(50))
    year = DB.Column(DB.Integer())
    player_id = DB.Column(DB.BigInteger, DB.ForeignKey(Player.id), nullable=False)
    league = DB.relationship('Player', backref=DB.backref('playerSeasons', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<{} for the {} season>'.format(self.name, self.year)

class playerGame(DB.Model):
    """
    We consider each player/team, player/season, and player/team/season changes to mean a new player.
        - thus the Player <-> Team Relationship is many to many for a season
        - while only many -> one for any given game. Many players play for a team for any given game, but never more than one.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    team = DB.Column(DB.String(50))
    year = DB.Column(DB.Integer())
    player_id = DB.Column(DB.BigInteger, DB.ForeignKey(Player.id), nullable=False)
    league = DB.relationship('playerSeason', backref=DB.backref('playerGames', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<{} for the {} season>'.format(self.name, self.year)

class Coach(DB.Model):
    """
    Coach main table.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    team = DB.Column(DB.String(50))
    experience = DB.Column(DB.Integer())
    league = DB.relationship('League', backref=DB.backref('coaches', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<Coach {}>'.format(self.name)

class coachSeason(DB.Model):
    """
    Season data for a coach.
    """
    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    team = DB.Column(DB.String(50))
    year = DB.Column(DB.Integer())
    coach_id = DB.Column(DB.BigInteger, DB.ForeignKey(Coach.id), nullable=False)
    coachSeason = DB.relationship('Coach', backref=DB.backref('coachSeasons', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<{} for the {} season>'.format(self.name, self.year)

class coachGame(DB.Model):
    """
    Game Data for a coach.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    team = DB.Column(DB.String(50))
    year = DB.Column(DB.Integer())
    season_id = DB.Column(DB.String(20), nullable=False)
    coachGame = DB.relationship('coachSeason', backref=DB.backref('coachGames', lazy=True))

    def __repr__(self):
        return '<{} for the {} season>'.format(self.name, self.year)

class Stadium(DB.Model):
    """
    An NFL stadium
    """
    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    yearBuilt = DB.Column(DB.BigInteger)
    yearClosed = DB.Column(DB.BigInteger)
    year = DB.Column(DB.Integer())
    stadium_id = DB.Column(DB.BigInteger, DB.ForeignKey(Coach.id), nullable=False)
    league = DB.relationship('League', backref=DB.backref('stadiums', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<{} for the {} season>'.format(self.name, self.year)

class stadiumSeason(DB.Model):
    """
    Season data at a stadium.
    """
    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    home_team = DB.Column(DB.String(50))
    year = DB.Column(DB.Integer())
    stadium_id = DB.Column(DB.BigInteger, DB.ForeignKey(Coach.id), nullable=False)
    stadiumSeason = DB.relationship('Stadium', backref=DB.backref('stadiumSeasons', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<{} for the {} season>'.format(self.name, self.year)

class stadiumGame(DB.Model):
    """
    Season data at a stadium.
    """
    id = DB.Column(DB.String(20), primary_key=True)
    name = DB.Column(DB.String(50))
    home_team = DB.Column(DB.String(50))
    year = DB.Column(DB.Integer())
    stadium_id = DB.Column(DB.BigInteger, DB.ForeignKey(Coach.id), nullable=False)
    stadiumGame = DB.relationship('stadiumSeason', backref=DB.backref('stadiumGames', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return '<{} >'.format(self.name, self.year)

class Game(DB.Model):
    """
    Game data between two teams.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    home_team_id = DB.Column(DB.String(50))
    kickoff_date = DB.Column(DB.BigInteger)
    league_id = DB.Column(DB.BigInteger, DB.ForeignKey(League.id), nullable=False)
    game = DB.relationship('League', backref=DB.backref('games', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return "<Game played @ {} with a {} o'clock kickoff>".format(self.stadium, self.kickoff)

class Play(DB.Model):
    """
    Play Data for a Game.
        - Play by Play data is the furthest down the stream. 
        - The most time should be spent here when trying to perfect things.
    """

    id = DB.Column(DB.String(20), primary_key=True)
    home_team_id = DB.Column(DB.String(50))
    kickoff_date = DB.Column(DB.BigInteger)
    league_id = DB.Column(DB.BigInteger, DB.ForeignKey(League.id), nullable=False)
    text = DB.Column(DB.Unicode(500))
    play = DB.relationship('Game', backref=DB.backref('plays', lazy=True))
    last_updated = DB.Column(DB.BigInteger())

    def __repr__(self):
        return "<Game played @ {} with a {} o'clock kickoff>".format(self.stadium, self.kickoff)