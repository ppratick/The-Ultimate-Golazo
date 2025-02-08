from gameMechanics import *
from drawingFunctions import *
import random
import time

# Initializes the application with default settings
def onAppStart(app):
    # Read team data from file and initialize team settings
    teamsData = readTeamFile('teams.txt')
    app.teams = list(teamsData.values())

    # Set application window dimensions
    app.width = 680
    app.height = 1050

    # Initialize game state and scoring
    app.game = "titleScreen"
    app.currentTeamIndex = 0
    app.opponentTeam = None
    app.myTeam = None
    app.ball = Ball(340, 525)
    app.mouseX = 0
    app.mouseY = 0
    app.myTeamScore = 0
    app.opponentTeamScore = 0
    app.lastScorer = "None"
    app.gamePlayStarted = False

    # Initialize game timing
    app.gameStartTime = time.time()
    app.elapsedTime = 0
    app.gameEndTime = None
    app.gameEnded = False
    app.winner = None

    # Define boundaries and initial ball movement state
    app.goalkeeperArea = (156, 367)
    app.fieldLeftEdge, app.fieldRightEdge = 43, 635
    app.fieldTopEdge, app.fieldBottomEdge = 55, 995
    app.firstBallMovement = True

    # Load and resize images for the game
    app.leoImage = openImage("leo.jpg")
    app.leoImage = app.leoImage.resize((500, 850))
    app.leoImage = CMUImage(app.leoImage)

    app.soccerImage = openImage("soccerfield.jpg")
    app.soccerImage = app.soccerImage.resize((640, 1010))
    app.soccerImage = CMUImage(app.soccerImage)

    app.soccerBallImage = openImage("soccerball.jpg")
    app.soccerBallImage = app.soccerBallImage.resize((25, 25)) 
    app.soccerBallImage = CMUImage(app.soccerBallImage)

    app.myplayerImage = openImage("myPlayer.png")
    app.myplayerImage = app.myplayerImage.resize((30, 75))
    app.myplayerImage = CMUImage(app.myplayerImage)

    app.opponentPlayerImage = openImage("oppPlayer.png")
    app.opponentPlayerImage = app.opponentPlayerImage.resize((30, 75))
    app.opponentPlayerImage = CMUImage(app.opponentPlayerImage)

    # Additional 
    app.lastGoalTime = None
    app.currentPlayer = None


# Main game loop function that updates each frame
def onStep(app):
    if app.ball.isMoving:
        moveBall(app)
        handleGoalScoring(app)
    
    if app.opponentTeam and app.ball.possession != app.opponentTeam.name:
        resetOpponentForwardMovement(app)

    if app.myTeam and app.opponentTeam:  
        if app.lastGoalTime is not None and time.time() - app.lastGoalTime < 5:
            return
        app.ball.updateCollisionCooldown(0.016)
        forward = findPlayerByRole(app.opponentTeam, 'forward')
        if app.ball.possession == app.myTeam.name:
            forward.hasMadeRun = False
        if forward and forward.hasMadeRun:
            updateForwardPosition(app, forward)
            if forward.isMovingToTarget:
                passBallToTargetPosition(app.ball, (forward.targetX, forward.targetY))
            if not forward.isMovingToTarget and app.ball.lastPlayer == forward:
                if distance(app.ball.x, app.ball.y, forward.x, forward.y) < 50:  
                    takeShotAtGoal(app.ball)

        currentTime = time.time()
        app.elapsedTime = currentTime - app.gameStartTime
        enforcePlayerBoundaries(app)
        findNearestPlayer(app)
        updateBallPositionWithPlayer(app)
        checkBallPlayerCollisions(app)
        defenderReactionToBall(app)
        midfielderReactionToBall(app)
        forwardReactionToBall(app)
        goalkeeperActions(app)
        goalkeeperActionsMyTeam(app)


        for player in app.opponentTeam.players:
                if player.role == 'goalkeeper':
                    yPosition = 42
                    moveGoalkeeper(player, app, 4, yPosition)

        for player in app.myTeam.players:
            if player.role == 'goalkeeper':
                yPosition = 960
                moveGoalkeeper(player, app, 2, yPosition)

        for player in app.myTeam.players + app.opponentTeam.players:
            if player.passCooldown > 0:
                player.passCooldown -= 0.016  

    if not app.gameEnded:
        if (app.myTeamScore >= 3 or app.opponentTeamScore >= 3) or (time.time() - app.gameStartTime >= 300):
            app.gameEnded = True
            app.gameEndTime = time.time()
            app.winner = app.myTeam.name if app.myTeamScore > app.opponentTeamScore else app.opponentTeam.name
            if app.myTeamScore == app.opponentTeamScore:
                app.winner = "Draw"

    # New logic for passing from defender to midfielder
    if app.opponentTeam and app.ball.possession == app.opponentTeam.name:
        lastPlayer = app.ball.lastPlayer
        if lastPlayer and lastPlayer.role == 'defender':
            furthestMidfielder = findFurthestMidfielderFromOpponents(app)
            if furthestMidfielder:
                passBallToPlayer(app.ball, furthestMidfielder)
                app.ball.lastPlayer = furthestMidfielder

        # New logic for midfielder passing to forward
        elif lastPlayer and lastPlayer.role in ['midfielder1', 'midfielder2']:
            makeForwardRunAndPassBall(app)


# Handles key press events
def onKeyPress(app, key):
    if app.game == "teamScreen":
        handleTeamSelection(app, key)
    if app.gameEnded:
        return
    elif app.game == "gameStarted" and app.gamePlayStarted:
        switchPlayerControl(app, key)
        handleGameActions(app, key)

# Handles continous key holds
def onKeyHold(app, keys):
    if app.lastGoalTime is not None and time.time() - app.lastGoalTime < 5:
        return
    if "space" in keys:
        app.gamePlayStarted = True
        
    if app.gamePlayStarted:
        if app.gameEnded:
            return
        currentTime = time.time()  
        ballMovementDistance = 5
        radiusThreshold = 25
        moveSpeed = 1.5
        goalkeeperMoveSpeed = 2

        increaseBallPower(app, keys, currentTime)

        if app.game == "gameStarted":
            # Handle movement for the selected player
            if app.currentPlayer:
                handlePlayerMovement(app.currentPlayer, keys, moveSpeed)

            # Handle movement for the nearest player
            if app.nearestPlayer and app.nearestPlayer != app.currentPlayer:
                handlePlayerMovement(app.nearestPlayer, keys, moveSpeed)

            for player in app.myTeam.players + app.opponentTeam.players:
                if player.passCooldown > 0:
                    player.passCooldown -= 0.016


# Handles key release events
def onKeyRelease(app, key):
    if key == "space" and app.ball.passable:
        dx, dy, distanceToMouse = calculateBallDirectionAndDistance(app)

        if distanceToMouse > 0:
            moveBallWithPower(app, dx, dy)
            if app.nearestPlayer:
                app.nearestPlayer.passCooldown = 0.5

        app.ball.resetPower() 
        resetDribblingStatus(app) 

# Handles mouse movement events
def onMouseMove(app, mouseX, mouseY):
    app.mouseX = mouseX
    app.mouseY = mouseY

# Handles mouse press events
def onMousePress(app, mouseX, mouseY):
    if app.game == "titleScreen":
        handleTitleScreenPress(app, mouseX, mouseY)
    elif app.game == "teamScreen":
        handleTeamScreenPress(app, mouseX, mouseY) 
    elif app.game == "instructionScreen":
        handleInstructionScreenPress(app, mouseX, mouseY)
    elif app.gameEnded:
        if (mouseX >= 248 and mouseX <= 432) and (mouseY >= 525 and mouseY <= 560):
            resetGameForNewMatch(app)


def main():
    runApp()

main()