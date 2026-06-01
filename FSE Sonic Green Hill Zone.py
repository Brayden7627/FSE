#FSE By Brayden Wang and Joel Langton
#Sonic The Hedgehog: Green Hill Zone

from pygame import *
from math import *


width,height=1200,900
screen=display.set_mode((width,height))

#Colours
red=(255,0,0)
grey=(127,127,127)
black=(0,0,0)
blue=(0,0,255)
green=(0,255,0)
yellow=(255,255,0)
white=(255,255,255)

#Misc

gravity=1






#Functions

def drawScene(platforms):
    for p in platforms:
        draw.rect(screen,green,p)

def move():
    keys=key.get_pressed()

    #if keys[K_SPACE] and vel[Y]



#Screens

def instructions():
    draw.rect(screen,yellow,(0,0,width,height))

def controls():
    draw.rect(screen,red,(0,0,width,height))

def level1():
    draw.rect(screen,white,(0,0,width,height))

    running=True
    counter=0

    platforms=[Rect(100,700,1000,100)]

    while running:
        for evt in event.get():
            if evt.type==QUIT:
                running=False
        
        counter+=1#frames
        drawScene(platforms)





        display.flip()


    return "mainMenu"




def mainMenu():
    running = True
    myClock = time.Clock()
    #button rects
    menuButtons=[Rect(100,100,200,50),
                 Rect(100,200,200,50)#level 1
                 ]

    while running:

        screen.fill(grey)
        mx,my=mouse.get_pos()
        mb=mouse.get_pressed()


        for evt in event.get():
            if evt.type == QUIT:
                return "exit"
            if evt.type == MOUSEBUTTONDOWN:
                if evt.button==1:   
                    if menuButtons[1].collidepoint(mx,my):
                        return "level1"
                    #implement if collide with button
            


        for b in menuButtons:
            draw.rect(screen,blue,b)



        
        display.flip()
        myClock.tick(60)

    











page="mainMenu"
while page !="exit":
    if page=="mainMenu":
        page=mainMenu()
    if page=="instructions":
        page=instructions()
    if page=="controls":
        page=controls()
    if page=="level1":
        page=level1()
            
quit()
