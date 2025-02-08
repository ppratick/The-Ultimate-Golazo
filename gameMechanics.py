from generalFunctions import *
import time
import random

# ---------------------------
# Ball Movement and Mechanics
# ---------------------------

# Code for moving the ball
def moveBall(app):
    distanceToTarget = distance(app.ball.x, app.ball.y, app.ball.targetX, app.ball.targetY)

    # Gradually reduce the moving speed of the ball
    if app.ball.possession != app.opponentTeam.name:
        app.ball.movingSpeed = app.ball.movingSpeed * 0.98

    if app.ball.movingSpeed < 0.1:
        app.ball.isMoving = False
        app.ball.movingSpeed = 0
    
    if distanceToTarget > app.ball.movingSpeed:
        directionX = (app.ball.targetX - app.ball.x) / distanceToTarget
        directionY = (app.ball.targetY - app.ball.y) / distanceToTarget
        newX = app.ball.x + directionX * app.ball.movingSpeed
        newY = app.ball.y + directionY * app.ball.movingSpeed

        # Check if the ball is within goal width but not in the goal height
        withinGoalWidth = 263 <= newX <= 416
        withinGoalHeight = newY <= 55 or newY >= 995 

        # Handle collision with side boundaries
        if newX < app.fieldLeftEdge or newX > app.fieldRightEdge:
            if not withinGoalHeight: 
                directionX = -directionX
                newX = app.ball.x + directionX * app.ball.movingSpeed
                app.ball.targetX = app.ball.x + directionX * (distanceToTarget - app.ball.movingSpeed)

        # Handle collision with top and bottom boundaries
        if newY < app.fieldTopEdge or newY > app.fieldBottomEdge:
            if not withinGoalWidth:
                directionY = -directionY
                newY = app.ball.y + directionY * app.ball.movingSpeed
                app.ball.targetY = app.ball.y + directionY * (distanceToTarget - app.ball.movingSpeed)

        app.ball.x, app.ball.y = newX, newY
    else:
        app.ball.x, app.ball.y = app.ball.targetX, app.ball.targetY
        app.ball.isMoving = False

    # Reset the ball's moving speed if it stops
    if not app.ball.isMoving and app.ball.possession != app.opponentTeam.name:
        app.ball.movingSpeed = 5  

# Checks and handles goal scoring situations
def handleGoalScoring(app):
    if 263 <= app.ball.x <= 416: 
        if app.ball.y <= 31: 
            app.myTeamScore += 1
            app.lastScorer = "Me"
            app.ball.possession = app.opponentTeam.name
            resetGame(app)
            app.lastGoalTime = time.time()
        elif app.ball.y >= 1008: 
            app.opponentTeamScore += 1
            app.lastScorer = "Opp"
            app.ball.possession = None
            resetGame(app)

# Taking a shot at the goal
def takeShotAtGoal(ball):
    goalXRange = (263, 416)
    goalY = 1008
    targetX = random.uniform(goalXRange[0], goalXRange[1])
    ball.targetX = targetX
    ball.targetY = goalY
    shotSpeed = 20  
    ball.move(targetX - ball.x, goalY - ball.y, shotSpeed)
    ball.isMoving = True
    

# Resets the game to its initial state
def resetGame(app):
    app.ball.x, app.ball.y = app.width / 2, app.height / 2
    app.ball.isMoving = False
    if app.lastScorer == "Me":
        resetPlayerPositions(app, app.myTeam, myStartingPositionsWhenIScore)
        resetPlayerPositions(app, app.opponentTeam, opponentStartingPositionsWhenIScore)
    elif app.lastScorer == "Opp":
        resetPlayerPositions(app, app.myTeam, myStartingPositions)
        resetPlayerPositions(app, app.opponentTeam, opponentStartingPositions)

# Resets the game for new match
def resetGameForNewMatch(app):
    app.myTeamScore = 0
    app.opponentTeamScore = 0
    app.lastScorer = "None"
    app.gameStartTime = time.time()
    app.gameEnded = False
    app.winner = None
    app.game = "titleScreen"
    app.gamePlayStarted = False
    app.ball.possesion = None

    resetPlayerPositions(app, app.myTeam, myStartingPositions)
    resetPlayerPositions(app, app.opponentTeam, opponentStartingPositions)
    app.ball.x, app.ball.y = app.width / 2, app.height / 2
    app.ball.isMoving = False

# -------------------------
# Player Movement and Logic
# -------------------------

# Ensures players remain within the field boundaries
def enforcePlayerBoundaries(app):
    for team in [app.myTeam, app.opponentTeam]:
        for player in team.players:

            player.x = max(min(player.x, app.fieldRightEdge), app.fieldLeftEdge)
            player.y = max(min(player.y, app.fieldBottomEdge), app.fieldTopEdge)

# Finds the nearest player to the ball
def findNearestPlayer(app):
    nearestPlayer = None
    minDistance = 10000
    playerImageWidth = 30
    playerImageHeight = 75

    for player in app.myTeam.players:
        if player.role != 'goalkeeper':
            playerBottomEdgeY = player.y + playerImageHeight / 2
            dist = distance(player.x, playerBottomEdgeY, app.ball.x, app.ball.y)
            if dist < minDistance:
                minDistance = dist
                nearestPlayer = player

    app.nearestPlayer = nearestPlayer
    app.ball.passable = minDistance <= 50

# Updates the ball's position when a player is dribbling
def updateBallPositionWithPlayer(app):
    if app.myTeam and app.nearestPlayer.dribbling:
        app.ball.x = app.nearestPlayer.x + 15
        app.ball.y = app.nearestPlayer.y + 75 / 2
        app.ball.lastPlayer = app.nearestPlayer
        app.ball.changePossession(app.myTeam.name)
        app.nearestPlayer.passCooldown = 0.5  

# Defines defender's reaction to the ball's position
def defenderReactionToBall(app):
    opponentDefender = None
    
    for player in app.opponentTeam.players:
        if player.role == 'defender':
            opponentDefender = player
            break

    if opponentDefender:
        if 156 <= app.ball.x <= 523 and 42 <= app.ball.y <= 192:
            moveDefenderTowardsBall(opponentDefender, app)

            if distance(opponentDefender.x, opponentDefender.y, app.ball.x, app.ball.y) < 50:
                if app.nearestPlayer.dribbling:
                    app.nearestPlayer.dribbling = False

                furthestMidfielder = findFurthestMidfielderFromOpponents(app)
                if furthestMidfielder:
                    passBallToPlayer(app.ball, furthestMidfielder)
                    app.ball.lastPlayer = furthestMidfielder
                    return            

# Moves a defender towards the ball
def moveDefenderTowardsBall(defender, app):
    if defender is None:
        return

    dx, dy = app.ball.x - defender.x, app.ball.y - defender.y
    distanceToBall = math.sqrt(dx**2 + dy**2)

    if distanceToBall > 0:
        dx, dy = dx / distanceToBall, dy / distanceToBall
    else:
        return

    defender.x += dx * defender.speed
    defender.y += dy * defender.speed

# Defines midfielder's reaction to the ball's position
def midfielderReactionToBall(app):
    if app.ball.possession != app.opponentTeam.name:
        if app.gamePlayStarted:
            closestMidfielder = None
            minDistanceToBall = 10000

            for player in app.opponentTeam.players:
                if player.role in ['midfielder1', 'midfielder2']:
                    distanceToBall = distance(player.x, player.y, app.ball.x, app.ball.y)
                    if distanceToBall < minDistanceToBall:
                        minDistanceToBall = distanceToBall
                        closestMidfielder = player

            if closestMidfielder:
                if app.ball.possession != app.opponentTeam.name and minDistanceToBall < 400 and not (156 <= app.ball.x <= 523 and 42 <= app.ball.y <= 192):
                    movePlayerTowardsBall(closestMidfielder, app)

                    if minDistanceToBall < 50:
                        if app.nearestPlayer.dribbling:
                            app.nearestPlayer.dribbling = False
                
                if minDistanceToBall < 30:
                    app.ball.changePossession(app.opponentTeam.name)
                    closestMidfielder.dribbling = True
    if app.ball.possession == app.opponentTeam.name:
        app.ball.movingSpeed = 5
        closestMidfielder, minDistanceToBall = findClosestMidfielderToBall(app)
        if minDistanceToBall <= 50:
            makeForwardRunAndPassBall(app)

# Finding the furthest midfielder from opponents
def findFurthestMidfielderFromOpponents(app):
    furthestMidfielder = None
    maxDistance = -1

    for midfielder in app.opponentTeam.players:
        if midfielder.role in ['midfielder1', 'midfielder2']:
            distanceToClosestOpponent = min([distance(midfielder.x, midfielder.y, p.x, p.y) for p in app.myTeam.players])
            if distanceToClosestOpponent > maxDistance:
                maxDistance = distanceToClosestOpponent
                furthestMidfielder = midfielder

    return furthestMidfielder

# Finding the furthest midfielder from the player's team
def findFurthestMidfielderFromOpponentsMyTeam(app):
    furthestMidfielder = None
    maxDistance = -1

    for midfielder in app.myTeam.players:
        if midfielder.role in ['midfielder1', 'midfielder2']:
            distanceToClosestOpponent = min([distance(midfielder.x, midfielder.y, p.x, p.y) for p in app.opponentTeam.players])
            if distanceToClosestOpponent > maxDistance:
                maxDistance = distanceToClosestOpponent
                furthestMidfielder = midfielder

    return furthestMidfielder

# Finding the closest midfielder to the ball
def findClosestMidfielderToBall(app):
    closestMidfielder = None
    minDistanceToBall = float('inf')

    for player in app.opponentTeam.players:
        if player.role in ['midfielder1', 'midfielder2']:
            distanceToBall = distance(player.x, player.y, app.ball.x, app.ball.y)
            if distanceToBall < minDistanceToBall:
                minDistanceToBall = distanceToBall
                closestMidfielder = player

    return closestMidfielder, minDistanceToBall

# Passing the ball to a player
def passBallToPlayer(ball, player, baseSpeed = 10):
    ball.targetX, ball.targetY = player.x, player.y
    ball.isMoving = True
    ball.movingSpeed = baseSpeed
    ball.startCollisionCooldown(1)

# The forward makes a run and passes the ball
def makeForwardRunAndPassBall(app):
    forward = findPlayerByRole(app.opponentTeam, 'forward')
    targetPositions = [(200, 850), (478, 850)]
    if forward and not forward.hasMadeRun:
        targetPosition = random.choice(targetPositions)
        forward.targetX, forward.targetY = targetPosition
        forward.hasMadeRun = True  
        forward.isMovingToTarget = True 

        passBallToTargetPosition(app.ball, targetPosition)
        app.ball.lastPlayer = forward  

# Passes the ball to the target position
def passBallToTargetPosition(ball, targetPosition, baseSpeed=5):
    ball.targetX, ball.targetY = targetPosition
    ball.isMoving = True
    ball.movingSpeed = baseSpeed
    ball.startCollisionCooldown(1)

# Updates the forwards positions
def updateForwardPosition(app, forward, movementSpeed=2.5):
    if forward.isMovingToTarget:
        dx = forward.targetX - forward.x
        dy = forward.targetY - forward.y
        distanceToTarget = math.sqrt(dx**2 + dy**2)

        if distanceToTarget > movementSpeed:
            dx, dy = dx / distanceToTarget, dy / distanceToTarget
            forward.x += dx * movementSpeed
            forward.y += dy * movementSpeed
        else:
            forward.x, forward.y = forward.targetX, forward.targetY
            forward.isMovingToTarget = False  # The forward has reached the target

# Finds a player by their role in a team
def findPlayerByRole(team, role):
    for player in team.players:
        if player.role == role:
            return player
    return None

# Moves a player towards the ball
def movePlayerTowardsBall(player, app):
    if player is None:
        return

    dx, dy = app.ball.x - player.x, app.ball.y - player.y
    distanceToBall = math.sqrt(dx**2 + dy**2)

    if distanceToBall > 0:
        dx, dy = dx / distanceToBall, dy / distanceToBall
    else:
        return

    newX, newY = player.x + dx * player.speed, player.y + dy * player.speed

    for teammate in app.opponentTeam.players:
        if teammate != player and distance(newX, newY, teammate.x, teammate.y) < 75: # This makes it so there's an invisible bubble around the opponent so when the AI opponent moves, it doesn't go 50 pixels near another player. 
            return
        
    player.x += dx * player.speed
    player.y += dy * player.speed

# Clears the ball from the current position
def clearBall(app):
    kickPower = random.randint(5, 10)
    dy = kickPower * 50
    app.ball.move(0, dy)
    app.ball.changePossession(None)

# Resets the forward movement of the opponent team
def resetOpponentForwardMovement(app):
    for player in app.opponentTeam.players:
        player.dribbling = False

# Checks if the ball is near a player
def isBallNearPlayer(ball, player, saveDistance=50):
    return distance(ball.x, ball.y, player.x, player.y) <= saveDistance

# Opponents goalkeeper saves the ball
def goalkeeperActions(app):
    opponentGoalkeeper = findPlayerByRole(app.opponentTeam, 'goalkeeper')
    if opponentGoalkeeper and isBallNearPlayer(app.ball, opponentGoalkeeper, 50):
        app.ball.stop()
        app.ball.changePossession(app.opponentTeam.name)
        furthestMidfielder = findFurthestMidfielderFromOpponents(app)
        if furthestMidfielder:
            passBallToPlayer(app.ball, furthestMidfielder)

# My goalkeeper saves the ball
def goalkeeperActionsMyTeam(app):
    goalkeeper = findPlayerByRole(app.myTeam, 'goalkeeper')
    if goalkeeper and isBallNearPlayer(app.ball, goalkeeper, 50):
        app.ball.stop()
        app.ball.changePossession(app.myTeam.name)
        furthestMidfielder = findFurthestMidfielderFromOpponentsMyTeam(app)
        if furthestMidfielder:
            passBallToPlayer(app.ball, furthestMidfielder)
            app.ball.lastPlayer = furthestMidfielder

# Checks if a player is marked by opponents
def isPlayerMarked(player, opponents, markingDistance=100):
    for opponent in opponents:
        if distance(player.x, player.y, opponent.x, opponent.y) < markingDistance:
            return True
    return False

# How the oopponents forward reacts to the ball
def forwardReactionToBall(app):
    opponentForward = findPlayerByRole(app.opponentTeam, 'forward')
    if opponentForward:
        # Define the target positions
        targetY = app.height / 2 + 200
        targetX = app.ball.x

        # Gradual movement speed
        movementSpeed = 2

        if app.ball.possession == app.myTeam.name:
            # Gradually move the forward towards the target X position
            if opponentForward.x < targetX:
                opponentForward.x += min(movementSpeed, targetX - opponentForward.x)
            elif opponentForward.x > targetX:
                opponentForward.x -= min(movementSpeed, opponentForward.x - targetX)

            # Gradually move the forward towards the target Y position
            if opponentForward.y < targetY:
                opponentForward.y += min(movementSpeed, targetY - opponentForward.y)
            elif opponentForward.y > targetY:
                opponentForward.y -= min(movementSpeed, opponentForward.y - targetY)

# -----------------------
# Input and Interaction
# -----------------------

# Handles team selection input
def handleTeamSelection(app, key):
    if key in ["right", "left", "up", "down"]:
        if key in ["right", "up"]:
            app.currentTeamIndex = (app.currentTeamIndex + 1) % len(app.teams)
        elif key in ["left", "down"]:
            app.currentTeamIndex = (app.currentTeamIndex - 1) % len(app.teams)

        app.myTeam = app.teams[app.currentTeamIndex]
        imageFileName = app.myTeam.name.lower().replace(" ", "") + ".jpg"
        app.myTeamImage = CMUImage(openImage(imageFileName, isTeamLogo=True).resize((125, 125)))

# Handles the instruction screen press
def handleInstructionScreenPress(app, mouseX, mouseY):
    if (mouseX >= 230 and mouseX <= 450) and (mouseY >= 930 and mouseY <= 970):
        app.game = "titleScreen"

# Handles game actions based on key inputs
def handleGameActions(app, key):
    if key == "c" and app.ball.passable:
        app.nearestPlayer.dribbling = not app.nearestPlayer.dribbling

# Handles collisions between players
def handlePlayerCollisions(currentPlayer, allPlayers, app):
    for player in allPlayers:
        if player != currentPlayer:
            distanceBetweenPlayers = distance(currentPlayer.x, currentPlayer.y, player.x, player.y)
            if distanceBetweenPlayers < 30: 
                dx = currentPlayer.x - player.x
                dy = currentPlayer.y - player.y
                distanceToMove = 30 - distanceBetweenPlayers  

                if dx != 0 or dy != 0:
                    normalizationFactor = distanceToMove / math.sqrt(dx**2 + dy**2)
                    dx *= normalizationFactor
                    dy *= normalizationFactor

                currentPlayer.x += dx / 2
                currentPlayer.y += dy / 2

                currentPlayer.x = max(min(currentPlayer.x, app.fieldRightEdge), app.fieldLeftEdge)
                currentPlayer.y = max(min(currentPlayer.y, app.fieldBottomEdge), app.fieldTopEdge)

                if currentPlayer.role == 'goalkeeper' and currentPlayer.fixY:
                    currentPlayer.y = 960

# Handles collisions between opponent players
def handleOpponentCollisions(currentPlayer, opponentPlayers, app):
    for opponentPlayer in opponentPlayers:
        if currentPlayer != opponentPlayer:
            distanceBetweenPlayers = distance(currentPlayer.x, currentPlayer.y, opponentPlayer.x, opponentPlayer.y)
            if distanceBetweenPlayers < 30: 
                dx = currentPlayer.x - opponentPlayer.x
                dy = currentPlayer.y - opponentPlayer.y
                distanceToMove = 30 - distanceBetweenPlayers 

                if dx != 0 or dy != 0:
                    normalizationFactor = distanceToMove / math.sqrt(dx**2 + dy**2)
                    dx *= normalizationFactor
                    dy *= normalizationFactor

                currentPlayer.x += dx / 2
                currentPlayer.y += dy / 2

                currentPlayer.x = max(min(currentPlayer.x, app.fieldRightEdge), app.fieldLeftEdge)
                currentPlayer.y = max(min(currentPlayer.y, app.fieldBottomEdge), app.fieldTopEdge)

                if currentPlayer.role == 'goalkeeper' and currentPlayer.fixY:
                    currentPlayer.y = 90

# Handles mouse presses on the team screen
def handleTeamScreenPress(app, mouseX, mouseY):
    if (mouseX >= 40 and mouseX <= 240) and (mouseY >= 850 and mouseY <= 885):
        app.game = "gameStarted"  
        app.gameStartTime = time.time()
        app.elapsedTime = 0
    if (mouseX >= 40 and mouseX <= 240) and (mouseY >= 910 and mouseY <= 945):
        app.game = "titleScreen" 

# Increases the ball's power based on key holds
def increaseBallPower(app, keys, currentTime):
    if "space" in keys and app.ball.passable:
        app.ball.increasePower(currentTime)

# Handles player movement based on key inputs
def handlePlayerMovement(player, keys, moveSpeed):
    if 'w' in keys:
        player.y -= moveSpeed * player.speed
    if 's' in keys:
        player.y += moveSpeed * player.speed
    if 'a' in keys:
        player.x -= moveSpeed * player.speed
    if 'd' in keys:
        player.x += moveSpeed * player.speed

# Moves the goalkeeper based on the ball's position
def moveGoalkeeper(player, app, goalkeeperMoveSpeed, yPosition):
    goalkeeperLeftBound = app.goalkeeperArea[0]
    goalkeeperRightBound = app.goalkeeperArea[0] + app.goalkeeperArea[1] 
    desiredX = min(max(app.ball.x, goalkeeperLeftBound), goalkeeperRightBound)

    if player.x != desiredX:
        direction = 1 if player.x < desiredX else -1
        player.x += direction * min(goalkeeperMoveSpeed, abs(desiredX - player.x))

    player.y = yPosition

# Checks for collisions between the ball and players 
def checkBallPlayerCollisions(app):
    app.ball.updateCollisionCooldown(0.016)

    # Check collisions only if cooldown has elapsed
    if app.ball.collisionCooldown <= 0:
        for player in app.myTeam.players + app.opponentTeam.players:
            if player.passCooldown <= 0:
                if distance(app.ball.x, app.ball.y, player.x, player.y) < 30:
                    app.ball.isMoving = False
                    break

# Calculates the direction and distance of the ball from the mouse
def calculateBallDirectionAndDistance(app):
    dx = app.mouseX - app.ball.x
    dy = app.mouseY - app.ball.y
    distanceToMouse = math.sqrt(dx ** 2 + dy ** 2)

    if distanceToMouse > 0:
        dx /= distanceToMouse 
        dy /= distanceToMouse
    else:
        dx, dy = 0, 0

    return dx, dy, distanceToMouse

# Switching player control
def switchPlayerControl(app, key):
    if key == '1':
        app.currentPlayer = app.myTeam.players[0]
    elif key == '2':
        app.currentPlayer = app.myTeam.players[1]
    elif key == '3':
        app.currentPlayer = app.myTeam.players[2]
    elif key == '4':
        app.currentPlayer = app.myTeam.players[3]
    elif key == '5':
        app.currentPlayer = app.myTeam.players[4]

# Moves the ball with a specified power 
def moveBallWithPower(app, dx, dy):
    if app.ball.power >= 2 and not app.gamePlayStarted:
        app.gamePlayStarted = True
        
    baseSpeed = 10
    powerMultiplier = app.ball.power * 100
    app.ball.move(dx * powerMultiplier, dy * powerMultiplier, baseSpeed)

# Resets the dribbling status of players 
def resetDribblingStatus(app):
    if app.myTeam and app.nearestPlayer and app.nearestPlayer.dribbling:
        app.nearestPlayer.dribbling = False

# Handles mouse presses on the title screen
def handleTitleScreenPress(app, mouseX, mouseY):
    if (mouseX >= 400 and mouseX <= 400 + 200) and (mouseY >= 275 and mouseY <= 275 + 35):
        selectTeam(app)
    elif (mouseX >= 400 and mouseX <= 400 + 200) and (mouseY >= 325 and mouseY <= 325 + 35):
        app.game = "instructionScreen"

# Selects a team for the game 
def selectTeam(app):
    app.game = "teamScreen"
    app.myTeam = app.teams[app.currentTeamIndex]
    loadTeamImages(app)

