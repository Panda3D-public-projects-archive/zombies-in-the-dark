from panda3d.core import *

class Bullet(object):    
    def __init__(self, parent, hpr, speed, life):
        self.node = loader.loadModel("models/nos")
        self.node.setPos(parent.node, 0, 1, 0)
        self.node.setHpr(hpr)
        self.node.reparentTo(render)
        self.node.setScale(0.1)
        self.speed = speed
        self.life = life
        self.alive = True
   
    def update(self, dt):
        if not self.alive:
            return
       
        self.life -= dt
       
        if self.life > 0:
            self.node.setFluidY(self.node, self.speed * dt)
        else:
            self.node.removeNode()
            self.alive = False
