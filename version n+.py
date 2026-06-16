#version n+

from pygame import *
from math import *
import random

init()
w, h = 1200, 900
screen = display.set_mode((w, h))

# --- Loading Screen (5 seconds) ---
loadingStart = time.get_ticks()
while time.get_ticks() - loadingStart < 1000:
    for e in event.get():
        if e.type == QUIT:
            quit()
    screen.fill((255, 255, 255))
    display.flip()

grey = (127, 127, 127)
blue = (0, 0, 255)
white = (255, 255, 255)
dirt = (109, 36, 0)
red = (255, 0, 0)
orange = (255, 127, 0)
yellow = (255, 255, 0)
lightBlue = (0, 191, 255)

X = 0
Y = 1
W = 2
H = 3
ROW = 4
COL = 5

SPRITE_W = 110
SPRITE_H = 100

bgImg     = transform.scale(image.load("pics/Sonic BG final.png"), (36720, 4590))
menuBgImg = transform.scale(image.load("pics/sonicMenuBG.png"), (w, h))

def addPics(folder, name, start, end):
    pics = []
    for i in range(start, end):
        pics.append(image.load(f"pics/{folder}/{name}{i}.png"))
    return pics

sonicRight = addPics("sonic sprites", "sonic", 1, 10)
sonicLeft  = [transform.flip(img, True, False) for img in sonicRight]
sonicIdle  = [sonicRight[0]]
sonicJump  = [image.load("pics/sonic sprites/sonicjump.png")]

sonicPics = [sonicRight, sonicLeft, sonicIdle, sonicJump]

coinPics = addPics("coins", "coin", 1, 4)

def updateCoins(coins):
    for coin in coins:
        coin[4] += 0.15
        if coin[4] >= len(coinPics):
            coin[4] = 0

def drawHud(cam, coinCount, lives, coins, elapsedTime, powerTimer):
    for coin in coins:
        if coin[5] == False:
            frame = transform.scale(coinPics[int(coin[4])], (coin[2], coin[3]))
            screen.blit(frame, (coin[0] - cam[0], coin[1] - cam[1]))

    f = font.SysFont(None, 36)
    coinIcon = transform.scale(coinPics[0], (28, 28))
    screen.blit(coinIcon, (10, 10))
    screen.blit(f.render(f"x {coinCount}", True, white), (44, 14))
    screen.blit(f.render(f"LIVES: {lives}", True, white), (10, 50))

    seconds = int(elapsedTime % 60)
    minutes = int(elapsedTime // 60)
    secStr = f"0{seconds}" if seconds < 10 else f"{seconds}"
    screen.blit(f.render(f"TIME: {minutes}:{secStr}", True, white), (10, 90))

    if powerTimer > 0:
        pSecs = int((powerTimer / 60) + 1)
        screen.blit(f.render(f"INVINCIBLE: {pSecs}s", True, yellow), (10, 130))

def checkCoinCollect(p, coinCount, coins):
    playerRect = Rect(p[X], p[Y], p[W], p[H])
    for coin in coins:
        if coin[5] == False:
            if playerRect.colliderect(Rect(coin[0], coin[1], coin[2], coin[3])):
                coin[5] = True
                coinCount += 1
    return coinCount

def updateDroppedCoins(cam, droppedCoins):
    for dc in droppedCoins:
        dc[6] += 0.15
        if dc[6] >= len(coinPics):
            dc[6] = 0

        dc[0] += dc[4]
        dc[1] += dc[5]
        dc[5] += 0.5

        dummyP = [dc[0], dc[1], dc[2], dc[3]]
        gY = getGround(dummyP, cam)

        if gY != None:
            if dc[1] + dc[3] >= gY - 50:
                dc[1] = gY - 50 - dc[3]
                dc[5] = -dc[5] * 0.75
                dc[4] *= 0.9

        dc[7] -= 1

    return [dc for dc in droppedCoins if dc[7] > 0]

def drawDroppedCoins(cam, droppedCoins):
    for dc in droppedCoins:
        frame = transform.scale(coinPics[int(dc[6])], (dc[2], dc[3]))
        screen.blit(frame, (dc[0] - cam[0], dc[1] - cam[1]))

def collectDroppedCoins(p, coinCount, droppedCoins):
    playerRect = Rect(p[X], p[Y], p[W], p[H])
    newCoinCount = coinCount
    for dc in droppedCoins:
        if dc[7] < 160:
            if playerRect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])):
                newCoinCount += 1

    updatedList = []
    for dc in droppedCoins:
        if dc[7] < 160:
            if playerRect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])):
                pass
            else:
                updatedList.append(dc)
        else:
            updatedList.append(dc)

    return newCoinCount, updatedList

def updateEnemies(cam, enemies, p):
    for enemy in enemies:
        dist = sqrt((enemy[0] - p[X])**2 + (enemy[1] - p[Y])**2)

        if dist < 350:
            if enemy[4] <= p[X]:
                if p[X] <= enemy[5]:
                    if enemy[0] < p[X]:
                        enemy[6] = abs(enemy[6])
                    else:
                        enemy[6] = -abs(enemy[6])
                    enemy[0] += enemy[6] * 2.5
                else:
                    enemy[0] += enemy[6]
                    if enemy[0] <= enemy[4]:
                        enemy[0] = enemy[4]
                        enemy[6] = abs(enemy[6])
                    elif enemy[0] >= enemy[5]:
                        enemy[0] = enemy[5]
                        enemy[6] = -abs(enemy[6])
            else:
                enemy[0] += enemy[6]
                if enemy[0] <= enemy[4]:
                    enemy[0] = enemy[4]
                    enemy[6] = abs(enemy[6])
                elif enemy[0] >= enemy[5]:
                    enemy[0] = enemy[5]
                    enemy[6] = -abs(enemy[6])
        else:
            enemy[0] += enemy[6]
            if enemy[0] <= enemy[4]:
                enemy[0] = enemy[4]
                enemy[6] = abs(enemy[6])
            elif enemy[0] >= enemy[5]:
                enemy[0] = enemy[5]
                enemy[6] = -abs(enemy[6])

        dummyEnemy = [enemy[0], enemy[1], enemy[2], enemy[3]]
        gY = getGround(dummyEnemy, cam)
        if gY != None:
            enemy[1] = gY - enemy[3]

def updateFishEnemies(fishes):
    for fish in fishes:
        if fish[4] == False:
            fish[7] -= 1
            if fish[7] <= 0:
                fish[4] = True
                fish[5] = -20
        else:
            fish[1] += fish[5]
            fish[5] += 0.6

            if fish[1] >= fish[6]:
                fish[1] = fish[6]
                fish[4] = False
                fish[5] = 0
                fish[7] = 90

def updateBuzzBombers(bombers, p, projectiles):
    for b in bombers:
        if b[7] > 0:
            b[7] -= 1
        else:
            if b[8] == True:
                b[8] = False
                b[7] = 60
            else:
                b[0] += b[6]
                if b[0] <= b[4]:
                    b[0] = b[4]
                    b[6] = abs(b[6])
                elif b[0] >= b[5]:
                    b[0] = b[5]
                    b[6] = -abs(b[6])

                if abs(p[X] - b[0]) < 250:
                    if p[Y] > b[1]:
                        b[8] = True
                        b[7] = 30
                        if p[X] < b[0]:
                            projVx = -5
                        else:
                            projVx = 5
                        projectiles.append([b[0] + 20, b[1] + 30, 20, 10, projVx, 5])

def updateProjectiles(projectiles):
    updated = []
    for pr in projectiles:
        pr[0] += pr[4]
        pr[1] += pr[5]
        if -500 < pr[0]:
            if pr[0] < 40000:
                if pr[1] < h + 500:
                    updated.append(pr)
    return updated

def drawEnemies(cam, enemies, fishes, bombers, projectiles, winBox, jumpPad, monitor, star):
    draw.rect(screen, yellow, (winBox[0] - cam[0], winBox[1] - cam[1], winBox[2], winBox[3]))
    draw.rect(screen, lightBlue, (jumpPad[0] - cam[0], jumpPad[1] - cam[1], jumpPad[2], jumpPad[3]))

    mColor = blue if monitor[4] == False else grey
    draw.rect(screen, mColor, (monitor[0] - cam[0], monitor[1] - cam[1], monitor[2], monitor[3]))
    if monitor[4] == False:
        draw.rect(screen, yellow, (monitor[0] + 15 - cam[0], monitor[1] + 15 - cam[1], 30, 30))

    if star[2] == True:
        draw.circle(screen, white, (int(star[0] - cam[0]), int(star[1] - cam[1])), 15)
        draw.circle(screen, yellow, (int(star[0] - cam[0]), int(star[1] - cam[1])), 8)

    for enemy in enemies:
        draw.rect(screen, red, (enemy[0] - cam[0], enemy[1] - cam[1], enemy[2], enemy[3]))
    for fish in fishes:
        draw.rect(screen, orange, (fish[0] - cam[0], fish[1] - cam[1], fish[2], fish[3]))
    for b in bombers:
        draw.rect(screen, blue, (b[0] - cam[0], b[1] - cam[1], b[2], b[3]))
    for pr in projectiles:
        draw.rect(screen, yellow, (pr[0] - cam[0], pr[1] - cam[1], pr[2], pr[3]))

def checkEnemyCollision(p, vel, invincibility, coinCount, lives, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, godMode):
    playerRect = Rect(p[X], p[Y], p[W], p[H])

    destroyedEnemies    = []
    destroyedFishes     = []
    destroyedBombers    = []
    destroyedProjectiles = []

    hitByHarmful = False
    enemyX = 0

    for enemy in enemies:
        enemyRect = Rect(enemy[0], enemy[1], enemy[2], enemy[3])
        if playerRect.colliderect(enemyRect):
            if isRolling == True or godMode:
                destroyedEnemies.append(enemy)
                vel[1] = -10
            elif vel[1] > 0:
                destroyedEnemies.append(enemy)
                vel[1] = -10
            else:
                hitByHarmful = True
                enemyX = enemy[0]

    for fish in fishes:
        fishRect = Rect(fish[0], fish[1], fish[2], fish[3])
        if playerRect.colliderect(fishRect):
            if isRolling == True or godMode:
                destroyedFishes.append(fish)
                vel[1] = -10
            elif vel[1] > 0:
                destroyedFishes.append(fish)
                vel[1] = -10
            else:
                hitByHarmful = True
                enemyX = fish[0]

    for b in bombers:
        bomberRect = Rect(b[0], b[1], b[2], b[3])
        if playerRect.colliderect(bomberRect):
            if isRolling == True or godMode:
                destroyedBombers.append(b)
                vel[1] = -10
            elif vel[1] > 0:
                destroyedBombers.append(b)
                vel[1] = -10
            else:
                hitByHarmful = True
                enemyX = b[0]

    for pr in projectiles:
        projRect = Rect(pr[0], pr[1], pr[2], pr[3])
        if playerRect.colliderect(projRect):
            if isRolling == True or godMode:
                destroyedProjectiles.append(pr)
            else:
                hitByHarmful = True
                enemyX = pr[0]

    enemies[:]     = [e  for e  in enemies     if e  not in destroyedEnemies]
    fishes[:]      = [f  for f  in fishes      if f  not in destroyedFishes]
    bombers[:]     = [b  for b  in bombers     if b  not in destroyedBombers]
    projectiles[:] = [pr for pr in projectiles if pr not in destroyedProjectiles]

    if hitByHarmful == True and not godMode:
        if invincibility <= 0:
            vel[1] = -12
            if p[X] < enemyX:
                vel[0] = -10
            else:
                vel[0] = 10

            invincibility = 120

            if coinCount > 0:
                coinsToDrop = min(coinCount, 20)
                for i in range(coinsToDrop):
                    angle = random.uniform(0, 2 * pi)
                    speed = random.uniform(4, 9)
                    vx = cos(angle) * speed
                    vy = sin(angle) * speed - 3
                    droppedCoins.append([p[X], p[Y], 32, 32, vx, vy, 0.0, 180])
                coinCount = 0
            else:
                lives -= 1
                p[X], p[Y] = 200, 100
                vel[0], vel[1] = 0, 0
                invincibility = 0

    return invincibility, coinCount, lives

def getGround(p, cam):
    sx = int(p[X] - cam[0] + (p[W] / 2))
    sy = int(p[Y] - cam[1] + p[H])

    if sx < 0 or sx >= w:
        return None

    for y in range(sy, sy + 300):
        if 0 <= y < h:
            c = screen.get_at((sx, y))[:3]
            if c[0] == 69 and c[1] == 23 and c[2] == 0:  # exact match only
                return y + cam[1]
        else:
            break
    return None

def updatePhysics(p, vel, cam, isJumping, invincibility, isRolling):
    p[Y] += vel[1]
    groundY = getGround(p, cam)
    fallDeath = False

    if groundY != None:
        if p[Y] + p[H] >= groundY - 50:
            p[Y] = groundY - 50 - p[H]
            vel[1] = 0
            isJumping = False

    if p[Y] > h + 200:
        p[X] = 200
        p[Y] = 100
        vel[0] = 0
        vel[1] = 0
        isJumping = False
        isRolling = False
        fallDeath = True

    if invincibility > 0:
        invincibility -= 1

    return isJumping, invincibility, fallDeath, isRolling

def handleInput(p, vel, isJumping, invincibility, isRolling, xPressedLast):
    keys = key.get_pressed()

    if invincibility < 100 or True:
        if keys[K_SPACE] or keys[K_UP]:
            if isJumping == False:
                vel[1] = -25
                isJumping = True
                isRolling = False

        if keys[K_x]:
            if xPressedLast == False:
                xPressedLast = True
                if isRolling == True:
                    isRolling = False
                elif isJumping == False:
                    isRolling = True
        else:
            xPressedLast = False

        if keys[K_LEFT]:
            if isRolling == True:
                vel[0] -= 0.35
            else:
                vel[0] -= 0.25 + max(0.05, abs(vel[0]) * 0.02)
        elif keys[K_RIGHT]:
            if isRolling == True:
                vel[0] += 0.35
            else:
                vel[0] += 0.25 + max(0.05, abs(vel[0]) * 0.02)

    if isJumping:
        p[ROW] = 3
        p[COL] = 0
    elif isRolling == False:
        moving = False
        if keys[K_LEFT] or keys[K_RIGHT]:
            moving = True

        if keys[K_LEFT]:
            p[ROW] = 1
        elif keys[K_RIGHT]:
            p[ROW] = 0

        if moving == False:
            p[ROW] = 2
            p[COL] = 0
        else:
            speed = abs(vel[0])
            p[COL] += 0.1 + speed * 0.03
            numFrames = len(sonicPics[p[ROW]])
            if p[COL] >= numFrames:
                p[COL] = 0

    if keys[K_LEFT] == False and keys[K_RIGHT] == False:
        fric = 0.025 if isRolling else 0.12
        if vel[0] > 0:
            vel[0] -= fric * (1 + abs(vel[0]) * 0.03)
            if vel[0] < 0: vel[0] = 0
        elif vel[0] < 0:
            vel[0] += fric * (1 + abs(vel[0]) * 0.03)
            if vel[0] > 0: vel[0] = 0

    maxSpeed = 22 if isRolling else 16

    vel[0] = max(-maxSpeed, min(maxSpeed, vel[0]))
    p[X] += vel[0]
    vel[1] += 1

# Keep player inside the map horizontally
    MAP_LEFT  = 0
    MAP_RIGHT = 36720
    p[X] = max(MAP_LEFT, min(p[X], MAP_RIGHT - p[W]))

    return isJumping, isRolling, xPressedLast

def render(p, cam, coinCount, lives, invincibility, coins, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, elapsedTime, winBox, jumpPad, monitor, star, powerTimer):
    cam[0] += ((p[X] - w // 2) - cam[0]) * 0.08
    cam[1] += ((p[Y] - h // 2) - cam[1]) * 0.08

    # Clamp camera so it never shows outside the background
    BG_W, BG_H = 36720, 4590
    cam[0] = max(0, min(cam[0], BG_W - w))
    cam[1] = max(-2720, min(cam[1], BG_H - 2720 - h))

    screen.blit(bgImg, (-cam[0], -2720 - cam[1]))

    drawHud(cam, coinCount, lives, coins, elapsedTime, powerTimer)
    drawDroppedCoins(cam, droppedCoins)
    drawEnemies(cam, enemies, fishes, bombers, projectiles, winBox, jumpPad, monitor, star)

    godMode = powerTimer > 0

    shouldDraw = True
    if not godMode:
        if invincibility > 0:
            if invincibility % 4 >= 2:
                shouldDraw = False

    if shouldDraw:
        if isRolling == True:
            drawX  = int(p[X] - cam[0] + p[W] // 2)
            drawY  = int(p[Y] - cam[1] + p[H] // 2)
            radius = int(p[W] // 2)

            ballColor = blue
            if godMode:
                if powerTimer % 4 < 2:
                    ballColor = yellow

            draw.circle(screen, ballColor, (drawX, drawY), radius)
            draw.circle(screen, white,     (drawX, drawY), radius - 10, 3)
        else:
            frame       = sonicPics[p[ROW]][int(p[COL])]
            frameScaled = transform.scale(frame, (SPRITE_W, SPRITE_H))

            if godMode and (powerTimer % 4 < 2):
                tintSurf = Surface((SPRITE_W, SPRITE_H), SRCALPHA)
                tintSurf.fill((255, 255, 0, 140))
                frameScaled = frameScaled.copy()
                frameScaled.blit(tintSurf, (0, 0), special_flags=BLEND_RGBA_MULT)

            drawX = p[X] - cam[0] - (SPRITE_W - p[W]) // 2
            drawY = p[Y] - cam[1] - (SPRITE_H - p[H]) // 2
            screen.blit(frameScaled, (drawX, drawY))

            if godMode:
                draw.circle(screen, white, (int(p[X] - cam[0] + random.randint(0, p[W])), int(p[Y] - cam[1] - 10)), 5)

def drawVictoryScreen(elapsedTime):
    fLarge = font.SysFont(None, 72)
    fSmall = font.SysFont(None, 48)

    seconds = int(elapsedTime % 60)
    minutes = int(elapsedTime // 60)
    secStr  = f"0{seconds}" if seconds < 10 else f"{seconds}"

    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"

        overlay = Surface((w, h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(10)
        screen.blit(overlay, (0, 0))

        txtWin  = fLarge.render("YOU WON!", True, yellow)
        txtTime = fSmall.render(f"Final Time: {minutes}:{secStr}", True, white)
        txtExit = fSmall.render("Press ESC to return to Menu", True, grey)

        screen.blit(txtWin,  (w // 2 - txtWin.get_width()  // 2, h // 2 - 100))
        screen.blit(txtTime, (w // 2 - txtTime.get_width() // 2, h // 2))
        screen.blit(txtExit, (w // 2 - txtExit.get_width() // 2, h // 2 + 100))

        display.flip()

def storyScreen():
    c = time.Clock()
    while True:
        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return "menu"
        screen.blit(menuBgImg, (0, 0))
        display.flip()
        c.tick(60)

def instructionsScreen():
    c = time.Clock()
    while True:
        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return "menu"
        screen.blit(menuBgImg, (0, 0))
        display.flip()
        c.tick(60)

def mainMenu():
    c = time.Clock()
    btnStart        = Rect(100, 100, 200, 50)
    btnStory        = Rect(100, 200, 200, 50)
    btnInstructions = Rect(100, 300, 200, 50)
    f = font.SysFont(None, 28)

    while True:
        screen.fill(grey)
        mx, my = mouse.get_pos()

        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == MOUSEBUTTONDOWN:
                if btnStart.collidepoint(mx, my):
                    return "play"
                if btnStory.collidepoint(mx, my):
                    return "story"
                if btnInstructions.collidepoint(mx, my):
                    return "instructions"

        for btn in [btnStart, btnStory, btnInstructions]:
            draw.rect(screen, blue, btn)

        screen.blit(f.render("START",        True, white), (155, 110))
        screen.blit(f.render("STORY",        True, white), (155, 210))
        screen.blit(f.render("INSTRUCTIONS", True, white), (108, 310))

        display.flip()
        c.tick(60)

def playLevel():
    c = time.Clock()
    p   = [200, 100, 80, 80, 0, 0]
    vel = [0, 0]
    cam = [0, 0]

    isJumping     = False
    isRolling     = False
    xPressedLast  = False
    invincibility = 0
    powerTimer    = 0

    coinCount   = 0
    lives       = 3
    elapsedTime = 0.0

    coins = [
        [350,  400, 40, 40, 0.0, False],
        [1000, 400, 40, 40, 0.0, False],
        [1060, 400, 40, 40, 0.0, False],
    ]

    enemies = [
        [600, 400, 50, 50, 400, 900, 3]
    ]

    fishes = [
        [450, 650, 45, 45, False, 0.0, 650, 60]
    ]

    bombers = [
        [1400, 250, 60, 40, 1100, 1700, 2, 0, False]
    ]
    projectiles  = []
    droppedCoins = []

    winBox  = [2600, 350, 100, 100]
    jumpPad = [500, 430, 60, 20]

    monitor = [1800, 400, 60, 60, False]
    star    = [0.0, 0.0, False, 0.0]

    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"

        if lives <= 0:
            return "menu"

        elapsedTime += 1.0 / 60.0
        if powerTimer > 0:
            powerTimer -= 1

        godMode = powerTimer > 0

        isJumping, isRolling, xPressedLast = handleInput(p, vel, isJumping, invincibility, isRolling, xPressedLast)
        isJumping, invincibility, fallDeath, isRolling = updatePhysics(p, vel, cam, isJumping, invincibility, isRolling)

        if fallDeath == True:
            lives     -= 1
            powerTimer = 0

        updateCoins(coins)
        updateEnemies(cam, enemies, p)
        updateFishEnemies(fishes)
        updateBuzzBombers(bombers, p, projectiles)
        projectiles  = updateProjectiles(projectiles)
        droppedCoins = updateDroppedCoins(cam, droppedCoins)

        coinCount = checkCoinCollect(p, coinCount, coins)
        coinCount, droppedCoins = collectDroppedCoins(p, coinCount, droppedCoins)
        invincibility, coinCount, lives = checkEnemyCollision(
            p, vel, invincibility, coinCount, lives, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, godMode
        )

        playerRect = Rect(p[X], p[Y], p[W], p[H])

        if playerRect.colliderect(Rect(jumpPad[0], jumpPad[1], jumpPad[2], jumpPad[3])):
            vel[1]    = -32
            isJumping = True
            isRolling = False
            p[ROW]    = 3
            p[COL]    = 0

        if monitor[4] == False:
            if playerRect.colliderect(Rect(monitor[0], monitor[1], monitor[2], monitor[3])):
                monitor[4] = True
                star[0] = monitor[0] + 30
                star[1] = monitor[1] + 10
                star[2] = True
                star[3] = monitor[1] - 50

        if star[2] == True:
            if star[1] > star[3]:
                star[1] -= 2.0

        if star[2] == True:
            starDist = sqrt((p[X] + p[W]//2 - star[0])**2 + (p[Y] + p[H]//2 - star[1])**2)
            if starDist < 55:
                star[2]    = False
                powerTimer = 1200

        if playerRect.colliderect(Rect(winBox[0], winBox[1], winBox[2], winBox[3])):
            return drawVictoryScreen(elapsedTime)

        render(p, cam, coinCount, lives, invincibility, coins, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, elapsedTime, winBox, jumpPad, monitor, star, powerTimer)

        display.flip()
        c.tick(60)

current = "menu"
while current != "exit":
    if current == "menu":
        current = mainMenu()
    elif current == "play":
        current = playLevel()
    elif current == "story":
        current = storyScreen()
    elif current == "instructions":
        current = instructionsScreen()

quit()