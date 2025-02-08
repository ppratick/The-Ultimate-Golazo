from cmu_graphics import *
from classes import *
from PIL import Image
import os, pathlib
import math
import time

# Player's starting positions 
myStartingPositions = {
    'goalkeeper': (339, 960), 
    'defender': (339, 850),
    'midfielder1': (150, 750),
    'midfielder2': (528, 750),
    'forward': (320, 500)
}

opponentStartingPositions = {
    'goalkeeper': (339, 90),
    'defender': (339, 175),
    'midfielder1': (150, 300),
    'midfielder2': (528, 300),
    'forward': (339, 400)
}
myStartingPositionsWhenIScore = {
    'goalkeeper': (339, 960), 
    'defender': (339, 850),
    'midfielder1': (150, 750),
    'midfielder2': (528, 750),
    'forward': (339, 550)
}
opponentStartingPositionsWhenIScore = {
    'goalkeeper': (339, 90),
    'defender': (339, 175),
    'midfielder1': (150, 300),
    'midfielder2': (358, 490),
    'forward': (390, 490)
}

# Reads team data from a file
def readTeamFile(filename, isOpponent = False):
    teams = {}
    playerRoles = ['goalkeeper', 'defender', 'midfielder1', 'midfielder2', 'forward']
    startingPositionsToUse = opponentStartingPositions if isOpponent else myStartingPositions

    with open(filename, encoding='utf-8') as f:
        for line in f:
            teamName, players = line.split(":")
            team = Team(teamName.strip())
            playerNames = players.split(",")
            for i in range(5):
                role = playerRoles[i]
                x, y = startingPositionsToUse[role]
                player = Player(playerNames[i].strip(), teamName.strip(), role, x, y)
                team.addPlayer(player)
            teams[team.name] = team
    return teams

# Opens and returns an image from a specified path
def openImage(fileName, isTeamLogo = False):
    subfolder = 'teamLogos' if isTeamLogo else 'otherImages'
    imagePath = os.path.join('images', subfolder, fileName)
    return Image.open(os.path.join(pathlib.Path(__file__).parent, imagePath))

# Loads images for the selected teams
def loadTeamImages(app):
    myTeamImageFileName = app.myTeam.name.lower().replace(" ", "") + ".jpg"
    app.myTeamImage = CMUImage(openImage(myTeamImageFileName, isTeamLogo=True).resize((125, 125)))
    
    while True:
        potentialOpponentIndex = random.choice(range(len(app.teams)))
        if potentialOpponentIndex != app.currentTeamIndex:
            opponentTeamName = app.teams[potentialOpponentIndex].name
            app.opponentTeam = readTeamFile('teams.txt', isOpponent=True)[opponentTeamName]
            break

    opponentTeamImageFileName = app.opponentTeam.name.lower().replace(" ", "") + ".jpg"
    app.oppImage = CMUImage(openImage(opponentTeamImageFileName, isTeamLogo=True).resize((125, 125)))

# Calculates the distance between two points
def distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

# Resets the position of players in a team
def resetPlayerPositions(app, team, startingPositions):
    for player in team.players:
        player.x, player.y = startingPositions[player.role]

