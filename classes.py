import random

class Player:
    def __init__(self, name, team, role, x, y):
        self.name = name
        self.team = team
        self.role = role
        self.x = x
        self.y = y
        self.speed = self.assignSpeed(role) 
        self.dribbling = False
        self.fixY = False
        self.passCooldown = 0
        self.hasMadeRun = False
        self.isMovingToTarget = False

    def assignSpeed(self, role):
        speedRanges = {
            'forward': (1.3, 1.8),
            'midfielder1': (1, 1.5),
            'midfielder2': (1, 1.5),
            'defender': (1, 1.25),
            'goalkeeper': (1, 1)
        }

        # Randomly assign speed within the range specified for the role.
        return random.uniform(*speedRanges[role])

    def __str__(self):
        return f"Player(Name: {self.name}, Team: {self.team}, Role: {self.role}, Position: ({self.x}, {self.y}))"

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []

    def addPlayer(self, player):
        self.players.append(player)

    def getPlayers(self):
        return self.players

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.isMoving = False
        self.passable = False
        self.power = 0
        self.lastPowerIncreaseTime = 0
        self.targetX = x 
        self.targetY = y  
        self.originalSpeed = 5
        self.movingSpeed = self.originalSpeed
        self.lastPlayer = None
        self.justPassed = False
        self.possession = None
        self.collisionCooldown = 0
    
    def changePossession(self, teamName):
        self.possession = teamName

    def move(self, dx, dy, baseSpeed = None):
        # Move the ball to a new position.
        self.targetX = self.x + dx
        self.targetY = self.y + dy
        self.isMoving = True
        if baseSpeed is not None:
            self.movingSpeed = baseSpeed

    def stop(self):
        self.isMoving = False
    
    def increasePower(self, currentTime):
        if currentTime - self.lastPowerIncreaseTime > 0.2:
            if self.power < 10:
                self.power += 1
            self.lastPowerIncreaseTime = currentTime

    def resetPower(self):
        self.power = 0

    def startCollisionCooldown(self, cooldownTime=1):
        self.collisionCooldown = cooldownTime

    def updateCollisionCooldown(self, elapsedTime):
        if self.collisionCooldown > 0:
            self.collisionCooldown -= elapsedTime

    def __str__(self):
        return f"Ball(Position: ({self.x}, {self.y}), Target: ({self.targetX}, {self.targetY}), Speed: {self.movingSpeed}, Moving: {'Yes' if self.isMoving else 'No'})"