from direct.task.Task import Task
from direct.showbase.PythonUtil import clampScalar
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase#@UnresolvedImport
from panda3d.core import WindowProperties
from panda3d.core import *
from utils import *
from bullet import Bullet

class Player(DirectObject):
    def __init__(self, parent, pos):
        self.parent = parent
        self.node = render.attachNewNode('PlayerNode')
        self.node.setPos(pos[0]*TILE_SIZE,pos[1]*TILE_SIZE,TILE_SIZE*ASPECT/1.5)
        taskMgr.add(self.updatePlayer, 'UpdatePlayerTask')
        taskMgr.add(self.updateBullets, 'UpdateBulletsTask')
        self.centerx = base.win.getProperties().getXSize()/2
        self.centery = base.win.getProperties().getYSize()/2
        self.speed = TILE_SIZE
        self.can_move = True
        self.camera = True
        self.mouse_owner = True
        self.max_health = 100
        self.health = 100
        self.max_bullets = 10
        self.bullets = 4
        self.bullet_objects = []
        
        props = WindowProperties()
        props.setCursorHidden(True) 
        base.win.requestProperties(props)
        
        # Create player flashlight
        self.slight = Spotlight('slight')
        self.slight.setColor(VBase4(1, 1, 0.6, 1))
        #self.lens = PerspectiveLens()
        #self.slight.setLens(self.lens)
        self.slnp = self.node.attachNewNode(self.slight)
        self.slnp.node().getLens().setFov(55)
        self.slnp.node().getLens().setNearFar(1, 10)
        self.slight.setExponent(45)
        self.slight.setAttenuation(Point3(0.737, 0.134, 0.001))
        render.setLight(self.slnp)
        self.flashlight = True
        
        self.shoot_sound = base.loader.loadSfx("audio/GUN_FIRE-GoodSoundForYou-820112263.wav")
        self.gun_click_sound = base.loader.loadSfx("audio/Dry Fire Gun-SoundBible.com-2053652037.wav")
        
        self.keys = {}
        self.keys['forward'] = 0
        self.keys['back'] = 0
        self.keys['strafe_left'] = 0
        self.keys['strafe_right'] = 0
    
        self.setKeyEvents()
    
    def setKeyEvents(self):
        self.accept('w', self.setKeys, ['forward', 1])
        self.accept('w-up', self.setKeys, ['forward', 0])
        self.accept('s', self.setKeys, ['back', 1])
        self.accept('s-up', self.setKeys, ['back', 0])                   
        self.accept('a', self.setKeys, ['strafe_left', 1])
        self.accept('a-up', self.setKeys, ['strafe_left', 0])
        self.accept('d', self.setKeys, ['strafe_right', 1])
        self.accept('d-up', self.setKeys, ['strafe_right', 0])
        self.accept('mouse1', self.shoot)
        self.accept('mouse3', self.toggleFlashlight)
        #TODO: maknuti ovo
        self.accept('x', self.toggleMovement)
        
    def clearKeyEvents(self):
        self.ignoreAll()
    
    def disconnectMouse(self):
        self.mouse_owner = False
        props = WindowProperties()
        props.setCursorHidden(False) 
        base.win.requestProperties(props)
        
    def reconnectMouse(self):
        self.mouse_owner = True
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        props = WindowProperties()
        props.setCursorHidden(True) 
        base.win.requestProperties(props)
        base.win.movePointer(0, self.centerx, self.centery)
    
    def toggleMovement(self):
        if self.can_move == True:
            self.can_move = False
        elif self.can_move == False:
            self.can_move = True
    
    def toggleFlashlight(self):
        if self.flashlight == True:
            self.flashlight = False
            render.clearLight(self.slnp)
        elif self.flashlight == False:
            self.flashlight = True
            render.setLight(self.slnp)
    
    def shoot(self):
        if self.bullets > 0:
            self.parent.parent.gameui.minusBullets()
            self.bullet_objects.append(Bullet(self, self.node.getHpr()))
            self.shoot_sound.play()
        else:
            self.gun_click_sound.play()
            None
    
    def setKeys(self, key, value):
        self.keys[key] = value    
    
    def updatePlayer(self, task):
        if self.can_move == False:
            return task.cont
        
        if self.parent.type == 'FPS':
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
    
            if self.mouse_owner and base.win.movePointer(0, self.centerx, self.centery):
                h, p, r = self.node.getHpr()
                h += (x - self.centerx) * -0.2
                p += (y - self.centery) * -0.2
                p = clampScalar(p, -80.0, 80.0)
                self.node.setHpr(h, p, 0)
    
            speed1 = 0
            speed2 = 0
            if self.keys['forward']:
                speed1 = self.speed * globalClock.getDt()
            if self.keys['back']:
                speed1 =  -self.speed * globalClock.getDt()
            if self.keys['strafe_left']:
                speed2 = -self.speed * globalClock.getDt()
            if self.keys['strafe_right']:
                speed2 = self.speed * globalClock.getDt()
    
            self.node.setFluidZ(TILE_SIZE*ASPECT/1.5)
            self.node.setFluidPos(self.node, speed2, speed1, 0)
        
        elif self.parent.type == 'DEBUG':
            speed1 = 0
            speed2 = 0
            if self.keys['forward']:
                speed1 = self.speed * globalClock.getDt()
            if self.keys['back']:
                speed1 =  -self.speed * globalClock.getDt()
            if self.keys['strafe_left']:
                speed2 = -self.speed * globalClock.getDt()
            if self.keys['strafe_right']:
                speed2 = self.speed * globalClock.getDt()
    
            self.node.setFluidZ(TILE_SIZE*ASPECT/1.5)
            self.node.setFluidPos(self.node, speed2, speed1, 0)
        return task.cont
    
    def updateBullets(self, task):
        for bullet in self.bullet_objects:
            bullet.update(globalClock.getDt())
   
        return task.cont