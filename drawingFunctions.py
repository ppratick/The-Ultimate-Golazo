from cmu_graphics import *

# Draws a button with specified text and position
def drawButton(text, x, y, color, width = 185, height = 35, textSize = 20):
    drawRect(x, y, width, height, fill=color)
    textX = x + width/2
    textY = y + height/2
    drawLabel(text, textX, textY, size = textSize, fill="white", align = "center")

# Draws the title screen of the game 
def drawTitleScreen(app):
    drawRect(0, 0, app.width, app.height, fill = "gray")
    drawLabel("The Ultimate", app.width/2, 100, bold = True, size = 80, fill = "orange")
    drawLabel("Golazo", app.width/2, 175, bold = True, size = 80, fill = "orange")
    drawButton("Select Team", 400, 275, "darkblue", 200, 35, 30)
    drawButton("Instructions", 400, 325, "purple", 200, 35, 30)
    drawImage(app.leoImage, 0, 200)

# Draws the instructions screen
def drawInstructionsScreen(app):
    drawRect(0, 0, app.width, app.height, fill="gray")
    drawLabel("Instructions", app.width / 2, 100, size=60, fill="orange", bold=True)

    instructionsText = [
        "Welcome to The Ultimate Golazo!",
        "Controls:",
        "- 'WASD' keys: Move players",
        "- '1' to '5' keys: Select specific players",
        "- 'Space': Pass/Shoot",
        "- 'C': Tackle / Close Dribble",
        "Game Rules:",
        "- Outscore the AI opponent",
        "- First to 3 goals wins, or most goals after 5 minutes",
        "Enjoy the Game!",
        "Master your skills, strategize your plays, and score the ultimate golazo!"
    ]

    startY = 200
    for line in instructionsText:
        if line.endswith(":"):
            drawLabel(line, app.width / 2, startY, size=25, fill="lightblue", bold=True)
        else:
            drawLabel(line, app.width / 2, startY, size=20, fill="white")
        startY += 35

    # Back to Menu button
    buttonWidth = 220
    buttonHeight = 40
    buttonX = app.width / 2 - buttonWidth / 2
    buttonY = app.height - 120
    drawButton("Back to Menu", buttonX, buttonY, "darkblue", buttonWidth, buttonHeight, 25)

# Draw the team selection screen 
def drawTeamScreen(app):
    drawRect(0, 0, app.width, app.height, fill = "gray")
    drawLabel("Select Teams", 40, 100, bold = True, size = 80, fill = "orange", align = "left")
    drawLabel("You're the team on the top", 40, 160, size = 20, fill = "orange", align = "left")
    drawLabel("The team on the bottom is played by AI", 40, 190, size = 20, fill = "orange", align = "left")
    drawLabel("Press the arrow keys to change your team", 40, 220, size = 20, fill = "orange", align = "left")
    drawLabel(app.myTeam.name, 40, 300, size=35, fill="darkblue", bold = True, align = "left")
    drawImage(app.myTeamImage, 600, 330, align = "center")
    drawLabel("VS", 40, 500, size=35, fill="orange", bold = True, align = "left")
    drawLabel(app.opponentTeam.name, 40, 700, size=35, fill="purple", bold = True, align = "left")
    drawImage(app.oppImage, 600, 730, align = "center")
    drawButton("Start Game", 40, 850, "darkblue", 200, 35, 30)
    drawButton("Back", 40, 910, "purple", 200, 35, 30)

# Draws the background and field
def drawBackgroundAndField(app):
    drawRect(0, 0, 680, 1050, fill="green")
    drawImage(app.soccerImage, 20, 20)

# Draws players on the field
def drawPlayers(app):
    for player in app.myTeam.players:
        drawImage(app.myplayerImage, player.x, player.y, align="center")
        drawLabel(player.name, player.x, player.y - 50, fill="white", size=12, align="center")
        if app.nearestPlayer and app.nearestPlayer == player:
            drawLabel("*", player.x, player.y - 70, fill="gold", size=20, bold=True, align="center")

    for player in app.opponentTeam.players:
        drawImage(app.opponentPlayerImage, player.x, player.y, align="center")
        drawLabel(player.name, player.x, player.y - 50, fill="white", size=12, align="center")

# Draws the ball and additional game info
def drawBallAndInfo(app):
    drawImage(app.soccerBallImage, app.ball.x, app.ball.y, align="center")
    drawLabel(f'Power: {app.ball.power}', 66, 1030, size=20, bold=True)
    drawLabel(f"{app.myTeam.name} {app.myTeamScore} - {app.opponentTeamScore} {app.opponentTeam.name}", 
              50, app.height/2, size = 20, fill = "white", bold = True, opacity = 50, rotateAngle = 270)

# Draw Timer
def drawTimer(app):
    minutes = str(int(app.elapsedTime) // 60)
    seconds = str(int(app.elapsedTime) % 60)
    timeString = f"{minutes}:{seconds}"
    drawLabel(timeString, 70, app.height/2, size=20, fill="white", bold = True, opacity = 50, rotateAngle = 270)
   
# Draws the main game screen
def drawGameScreen(app):
    drawBackgroundAndField(app)
    drawPlayers(app)
    drawBallAndInfo(app)
    drawTimer(app)
    drawLabel(f"Possession: {app.ball.possession}", 655, 1030, size=20, bold = True, align="right")
    if app.gameEnded:
        drawRect(0, 0, app.width, app.height, fill="black", opacity=70)
        winText = f"{app.winner} Wins!" if app.winner != "Draw" else "It's a Draw!"
        drawLabel(winText, app.width/2, app.height/2 - 50, size=40, fill="white")
        drawButton("Play Again", app.width/2 - 92.5, app.height/2, "green", 185, 35, 20)

# Redraws all elements based on the game state
def redrawAll(app):
    if app.game == "titleScreen":
        drawTitleScreen(app)
    elif app.game == "teamScreen":
        drawTeamScreen(app)
    elif app.game == "instructionScreen":
        drawInstructionsScreen(app)
    elif app.game == "gameStarted":
        drawGameScreen(app)
        # drawRect(26, 40, 626, 971, opacity = 50) 
        # drawRect(156, 42, 367, 150)
        # drawRect(156, 858, 367, 150)
