from panda3d.core import *
from utils import *

class Bullet(object):    
    def __init__(self, parent, hpr, speed=900, life=5):
        self.node = loader.loadModel("models/nos")
        self.node.setPos(parent.node, 0, 1, 0)
        self.node.setHpr(hpr)
        self.node.reparentTo(render)
        self.node.setScale(0.1)
        self.node.setColor(1,1,0)
        self.node.setLightOff()
        self.speed = speed
        self.life = life
        self.alive = True
        
        parent.parent.collision_manager.createBulletCollision(self)
   
    def update(self, dt):
        if not self.alive:
            return
       
        self.life -= dt
       
        if self.life > 0:
            self.node.setFluidY(self.node, self.speed * dt)
        else:
            self.destroy()
            
    def destroy(self):
        self.node.removeNode()
        self.alive = False
