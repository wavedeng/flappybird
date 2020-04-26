'''
    incomplete flapy bird using pygame.
    main logic finished.
'''

import pygame
import os
import time
import random

WINDOW_W = 500
WINDOW_H = 900
pygame.font.init()
WINDOW = pygame.display.set_mode((WINDOW_W,WINDOW_H))
pygame.display.set_caption("美丽的小鸟")
FONT = pygame.font.SysFont("arial", 20)

def LoadImage(name):
    return pygame.transform.scale2x(pygame.image.load(os.path.join("images",name)).convert_alpha())

def LoadImageWithSize(name,size):
    return pygame.transform.scale(pygame.image.load(os.path.join("images",name)).convert_alpha(), size)

Bird_Images = [LoadImageWithSize("bird"+str(x)+".png",(50,50)) for x in range(1,4)]
PipeSection_Image = LoadImageWithSize("pipe-section.png",(100,100))
PipeHead_Image = LoadImage("pipe-head.png")
Background_Image = LoadImageWithSize("background.png",(WINDOW_W,WINDOW_H))

class Bird:
    INIT_Y = 400
    INIT_X = 80
    MAX_AGLE = 25
    ROT_V = 4
    SPAN = 5
    IMAGES = Bird_Images
    JUMP_V =  22
    AC = 3
    
    def __init__(self):
        self.y = self.INIT_Y
        self.x = self.INIT_X
        self.rotate = 0
        self.img_index = 0
        self.img = self.IMAGES[0]
        self.tick_count = 0
        self.vel = 0
        self.jumpY = self.INIT_Y
        self.lastDis = 0
        

    def jump(self):
        self.vel = -self.JUMP_V
        self.tick_count = 0
        self.jumpY = self.y
        self.lastDis =0

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
    def move(self):
        self.tick_count +=1 
        dis = self.vel*(self.tick_count) + 0.5*self.AC*(self.tick_count)**2
        if dis - self.lastDis>20:
            dis = self.lastDis + 20
        self.lastDis = dis

        self.y =dis  + self.jumpY 

        if dis < 0:
            if self.rotate < self.MAX_AGLE:
                self.rotate = self.MAX_AGLE
        else:
            if self.rotate > -90:
                self.rotate -= self.ROT_V

    def draw(self,window):
        if self.tick_count%self.SPAN==0:
            self.img_index += 1
    
        if self.img_index == len(self.IMAGES):
            self.img_index = 0

        self.img = self.IMAGES[self.img_index]


        if self.rotate <=-75:
            self.img = self.IMAGES[0]
            self.img_index = 0

        rotated_bird = pygame.transform.rotate(self.img, self.rotate)
        new_rect = rotated_bird.get_rect(center = self.img.get_rect(topleft = (self.x,self.y)).center)
        window.blit(rotated_bird, new_rect.topleft)


        
class Column():
    MIN_GAP = 120
    MAX_GAP = 200
    def __init__(self,vel,x):
        self.vel = vel
        self.x = x
        self.pipes = self.init_pipes()
        self.passed = False

    def init_pipes(self):
        gapCount = random.randrange(1, 3)
        pipes = []
        gaps = []
        starts = []

        for i in range(gapCount):
            gaps.append(random.randrange(self.MIN_GAP*3/5,self.MAX_GAP*3/5))
        
        no_chance = True
        for gap in gaps:
            if gap >= self.MIN_GAP:
                no_chance = False
    

        if no_chance:
            gaps[random.randrange(0,gapCount)] = random.randrange(self.MIN_GAP,self.MAX_GAP)

        for i in range(gapCount):
            start = random.randrange(0,WINDOW_H/gapCount - gaps[i])
            start += i * WINDOW_H/gapCount 
            starts.append(start)

        for index in range(gapCount+1):
            if index == 0:
                newPipe = Pipe(self.vel,self.x,-10,starts[0])
            elif index == gapCount:
                newPipe = Pipe(self.vel,self.x,starts[gapCount-1] +gaps[gapCount-1],WINDOW_H)
            else:
                newPipe = Pipe(self.vel,self.x,starts[index-1]+gaps[index-1],starts[index]-starts[index-1]-gaps[index])
            pipes.append(newPipe)


        return pipes
            



    def move(self):
        self.x -= self.vel
        for pipe in self.pipes:
            pipe.move()

    def draw(self,window):
        for pipe in self.pipes:
            pipe.draw(window)
        
    def collide(self,bird,window):
        pipes = self.pipes
        collided = False
        for pipe in pipes:
            if pipe.collide(bird,window):
                collided = True
                break

        return collided


class Pipe():
    width = 100
    head_width = 110
    head_height = 15
    def __init__(self,vel,x,y,height):
        self.vel = vel
        self.x = x
        self.y = y
        self.height = height
        self.top =  pygame.transform.scale(PipeHead_Image,(self.head_width,round(self.head_height)))
        self.bottom = pygame.transform.flip(self.top,False,True)
        self.section = pygame.transform.scale(PipeSection_Image,(self.width,round(self.height)))

    def move(self):
        self.x -= self.vel

    def draw(self,window):
        window.blit(self.section, (self.x,self.y))
        curse = (self.head_width-self.width)/2
        window.blit(self.top,(self.x-curse,self.y))
        window.blit(self.bottom,(self.x-curse,self.y+self.height-self.head_height))


    def collide(self,bird,window):
        bird_mask = bird.get_mask()
        section_mask = pygame.mask.from_surface(self.section)
        offset = (round(self.x - bird.x),round(self.y -bird.y))
        return bird_mask.overlap(section_mask,offset)




def play(window):
    run = True
    bird = Bird()
    clock = pygame.time.Clock()
    col_v = 5
    max_col_v = 8
    score = 0

    columns = [Column(col_v,WINDOW_W+30)]
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
            if event.type == pygame.KEYDOWN and  event.key == pygame.K_SPACE:
                bird.jump()
        
        col_v += 0.001
        if(col_v>max_col_v):
            col_v = max_col_v

        bird.move()
        for col in columns:
            col.move()
            if col.collide(bird,window):
                bird = Bird()

            if col.passed == False:
                if col.x < 100:
                    col.passed = True
                    score += 1
                    columns.append(Column(col_v,WINDOW_W+30))

            if col.x <-120:
                columns.remove(col)

        drawAll(window,bird,columns,score)


def drawAll(window,bird,columns,score):
    window.blit(Background_Image,(0,0))
    bird.draw(window)
    
    for col in columns:
        col.draw(window)

    score_label = FONT.render("score: " + str(score),1,(0,0,0))
    window.blit(score_label, (10, 10))
    pygame.display.update()

if __name__ == "__main__":
    play(WINDOW)