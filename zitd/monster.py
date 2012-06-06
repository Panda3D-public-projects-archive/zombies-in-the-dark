from panda3d.core import *
from direct.interval.IntervalGlobal import *
from utils import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from AStar import pathFind
import random
import time


class Monster():
    def __init__(self, parent, type, pos):
        self.parent = parent
        self.hp = 100
        self.speed = 1
        self.pos = pos
        self.can_move = True
        
        if type == 'baby':
            self.node = Actor('models/baby', {'walk':'models/baby-walk', 
                                              'stand':'models/baby-stand',
                                              'idle':'models/baby-idle',
                                              'jump':'models/baby-jump',
                                              'bite1':'models/baby-bite1',
                                              'bite2':'models/baby-bite2',
                                              'head_attack':'models/baby-head_attack',                                
                                              'hit1':'models/baby-hit1',                                
                                              'hit2':'models/baby-hit2', 
                                              'die':'models/baby-die'})
            self.node.setH(180)
            self.node.flattenLight()
            self.node.setPos(pos[0]*TILE_SIZE,pos[1]*TILE_SIZE,0)
            self.node.setScale(0.03)
            self.node.setTexture(loader.loadTexture('models/Zomby_D.tga'))
            self.ts_normal = TextureStage('ts_normal')
            self.tex_normal = loader.loadTexture('models/Zomby_N.tga')
            self.ts_normal.setMode(TextureStage.MNormal)
            self.node.setTexture(self.ts_normal, self.tex_normal)
            self.node.reparentTo(render) 
            self.node.loop('stand')

        segs = LineSegs()
        segs.setThickness(23)
        segs.setColor(VBase4(1,0,0,1))
        segs.moveTo(0,0,0)
        segs.drawTo(0,30,0)
        self.linenode = self.node.attachNewNode(segs.create())
        self.linenode.setPos(0,0,35)
        self.linenode.setScale(5)
        self.linenode.setLightOff()

        self.action = 'stand'
        self.patrol_points = [(1,1), (4,11), (12,20), (18,4), (19,17)]
        taskMgr.doMethodLater(1, self.behaviourTask, 'behtask')

    def moveSequence(self):
        move = Sequence()
        start = self.node.getPos()
        for p in self.path:
            dest = Point3(p[0]*TILE_SIZE, p[1]*TILE_SIZE, 0)
            i = Sequence(self.node.posInterval(self.speed, dest, start), Func(self.updatePosition, p))
            start = dest
            move.append(i)
        move.append(Func(self.setAction, 'stand'))
        return move
        
    def updatePosition(self, dest):
        self.pos = dest

    def setAction(self, action):
        self.action = action

    def behaviourTask(self, task):
        if self.action == 'stand':
            if random.randint(0, 100) < 20:
                self.action = 'patrol'
                self.dest = self.pos
                while self.dest == self.pos:
                    self.dest = self.patrol_points[random.randint(0,4)]
                self.path = pathFind(self.parent.level, self.pos, self.dest)
                self.moveSequence().start()
                
        return task.again
