from direct.task.Task import Task
from direct.showbase.PythonUtil import clampScalar
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase#@UnresolvedImport
from panda3d.core import WindowProperties
from panda3d.core import *
from utils import *
from bullet import Bullet
import random
from direct.interval.IntervalGlobal import *
import time

GUNSHOT_TIMEOUT = 2 #sec


class Player(DirectObject):
    def __init__(self, parent, pos):
        self.parent = parent
        self.node = render.attachNewNode('PlayerNode')
        self.node.setPos(pos[0]*TILE_SIZE,pos[1]*TILE_SIZE,TILE_SIZE*ASPECT/1.5)
        taskMgr.add(self.updatePlayer, 'UpdatePlayerTask')
        taskMgr.add(self.updateBullets, 'UpdateBulletsTask')
        self.centerx = base.win.getProperties().getXSize()/2
        self.centery = base.win.getProperties().getYSize()/2
        self.speed = TILE_SIZE - 4
        self.sprint_speed = self.speed * 1.8
        self.can_move = True
        self.camera = True
        self.mouse_owner = True
        self.max_health = 100
        self.health = self.max_health
        self.max_bullets = 10
        self.bullets = 4
        self.bullet_objects = []
        self.sprint = False
        self.moving = False
        self.gunshot_at = None
        
        props = WindowProperties()
        props.setCursorHidden(True) 
        base.win.requestProperties(props)
        
        # Create player flashlight
        self.slight = Spotlight('slight')
        self.slight.setColor(VBase4(1, 1, 0.6, 1))
        #self.lens = PerspectiveLens()
        #self.slight.setLens(self.lens)
        self.slnp = self.node.attachNewNode(self.slight)
        self.slnp.node().getLens().setFov(88)
        self.slnp.node().getLens().setNearFar(1, 70)
        self.slight.setExponent(10)
        self.slight.setAttenuation(Point3(0.737, 0.134, 0.001))
        render.setLight(self.slnp)
        self.flashlight = True
        
        self.shoot_sound = base.loader.loadSfx("audio/GUN_FIRE-GoodSoundForYou-820112263.wav")
        self.gun_click_sound = base.loader.loadSfx("audio/Dry Fire Gun-SoundBible.com-2053652037.wav")
        self.heart_sound = base.loader.loadSfx("audio/Slow_HeartBeat-Mike_Koenig-1853475164.wav")
        self.heart_sound.setLoop(True)
        self.heart_sound.setVolume(0.6)
        self.heart_sound.play()
        
        self.scratches = loadImageAsPlane('models/scr.png')
        self.scratches.setTransparency(TransparencyAttrib.MAlpha) 
        self.damage_anim = Parallel()
        
        self.keys = {}
        self.keys['forward'] = 0
        self.keys['back'] = 0
        self.keys['strafe_left'] = 0
        self.keys['strafe_right'] = 0
        self.keys['sprint'] = 0
    
        self.setKeyEvents()
    
        self.pause = False
    
    
    def setKeyEvents(self):
        self.accept('w', self.setKeys, ['forward', 1])
        self.accept('w-up', self.setKeys, ['forward', 0])
        self.accept('s', self.setKeys, ['back', 1])
        self.accept('s-up', self.setKeys, ['back', 0])                   
        self.accept('a', self.setKeys, ['strafe_left', 1])
        self.accept('a-up', self.setKeys, ['strafe_left', 0])
        self.accept('d', self.setKeys, ['strafe_right', 1])
        self.accept('d-up', self.setKeys, ['strafe_right', 0])
        self.accept('space', self.setKeys, ['sprint', 1])
        self.accept('space-up', self.setKeys, ['sprint', 0])
        self.accept('mouse1', self.shoot)
        self.accept('mouse3', self.toggleFlashlight)
        #TODO: maknuti ovo
        #self.accept('x', self.disconnectMouse)
        #self.accept('y', self.reconnectMouse)
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
            self.gunRecoil()
            self.shoot_sound.play()
            
            #remeber gunshot
            self.gunshot_at = ( getTile( self.node.getPos() ), time.time() )
        else:
            self.gun_click_sound.play()
            None
            
    def getDamage(self, damage=21):
        self.damage_anim.finish()
        self.damage_anim = Parallel()
        
        damage = 10 + d(15)
        print "dmg:", damage
        
        # player got damage but is still alive
        if self.health - damage > 0:
            # set up scratches interval
            s1 = Sequence(Func(self.scratches.reparentTo, aspect2d), 
                         LerpColorInterval(self.scratches, duration=1, color=Vec4(1,1,1,0)), 
                         Func(self.scratches.detachNode),
                         Func(self.scratches.setColor, Vec4(1,1,1,1)))
            
            # set up recoil interval
            """
            starthpr = self.node.getHpr()
            dh = random.uniform(-10,10)
            dp = random.uniform(-10,10)
            d2h = random.uniform(0, -dh)
            d2p = random.uniform(0, -dp)
            hpr1 = starthpr+Vec3(dh, dp, 0)
            hpr2 = hpr1+Vec3(d2h, d2p, 0)
            s2 = Sequence(Func(self.toggleMovement),
                          self.node.quatInterval(hpr=hpr1, startHpr=starthpr, duration = 0.03),
                          self.node.quatInterval(hpr=hpr2, startHpr=hpr1, duration = 0.03),
                          Func(self.toggleMovement))
            self.damage_anim.append(s1)
            self.damage_anim.append(s2)
            
            self.damage_anim.start()
            """
            s1.start()
            self.parent.parent.gameui.minusHealth(damage)
            print "Damaged me!"
        # player got damage and died
        else:
            s1 = Sequence(Func(self.scratches.reparentTo, aspect2d), 
                         LerpColorInterval(self.scratches, duration=1, color=Vec4(1,1,1,0)), 
                         Func(self.scratches.detachNode),
                         Func(self.scratches.setColor, Vec4(1,1,1,1)))
            
            # set up die interval
            startpos = self.node.getPos()
            pos = startpos+Vec3(0, 0, -3)
            starthpr = self.node.getHpr()
            hpr = starthpr+Vec3(0, 0, 15)
            s2 = Sequence(LerpPosInterval(self.node, pos=pos, duration=0.5))
            s3 = Sequence(LerpHprInterval(self.node, hpr=hpr, duration=0.5))
            self.damage_anim.append(s1)
            self.damage_anim.append(s2)
            self.damage_anim.append(s3)
            
            self.damage_anim.start()
            self.parent.parent.gameui.minusHealth(damage)
            
            # shut down player
            self.clearKeyEvents()
            taskMgr.remove('UpdatePlayerTask')
            self.parent.gameOver()
            print "Killed me!"
    
    def setKeys(self, key, value):
        self.keys[key] = value    
        
    def gunRecoil(self):
        starthpr = self.node.getHpr()
        dh = random.uniform(-5,5)
        dp = random.uniform(-5,5)
        d2h = random.uniform(0, -dh)
        d2p = random.uniform(0, -dp)
        hpr1 = starthpr+Vec3(dh, dp, 0)
        hpr2 = hpr1+Vec3(d2h, d2p, 0)
        s = Sequence(self.node.quatInterval(hpr=hpr1, startHpr=starthpr, duration = 0.05),
                     self.node.quatInterval(hpr=hpr2, startHpr=hpr1, duration = 0.05))
        s.start()
    
    def updatePlayer(self, task):
        if self.pause:
            return task.cont
        
        if self.can_move == False:
            return task.cont
        

        if getTile( self.node.getPos() ) == self.parent.level.finish_tile:
            self.parent.gameWin()
        
        #monsters only think once per second so we need to keep gunshots remembered for at least 2 seconds
        if self.gunshot_at:
            if time.time() - self.gunshot_at[1] > GUNSHOT_TIMEOUT:
                self.gunshot_at = None
            
        self.cooldown( globalClock.getDt() )
        
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
            
            if self.keys['sprint']:
                player_speed = self.sprint_speed
            else:
                player_speed = self.speed
                
            if self.keys['forward']:
                speed1 = player_speed * globalClock.getDt()
            if self.keys['back']:
                speed1 =  -player_speed * globalClock.getDt()
            if self.keys['strafe_left']:
                speed2 = -player_speed * globalClock.getDt()
            if self.keys['strafe_right']:
                speed2 = player_speed * globalClock.getDt()
    
            if speed1 or speed2:
                if self.keys['sprint']:
                    self.sprint = True
                else:
                    self.sprint = False
                self.moving = True
            else:
                self.moving = False
                self.sprint = False
    
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
    
            if speed1 or speed2:
                self.moving = True
            else:
                self.moving = False
                
            self.node.setFluidZ(TILE_SIZE*ASPECT/1.5)
            self.node.setFluidPos(self.node, speed2, speed1, 0)
        return task.cont
    
    def updateBullets(self, task):
        if self.pause:
            return task.cont
        
        for bullet in self.bullet_objects:
            bullet.update(globalClock.getDt())
   
        return task.cont
    
    
    def adrenaline(self):
        #self.heart_sound.setVolume(0.4)
        rate = self.heart_sound.getPlayRate()
        rate += 0.2
        if rate > 2:
            rate = 2
        self.heart_sound.setPlayRate( rate )
        
        
    def cooldown(self, dt):
        rate = self.heart_sound.getPlayRate()
        rate -= 0.02 * dt
        if rate < 1:
            rate = 1
        self.heart_sound.setPlayRate( rate )
        
    def cleanup(self):
        self.clearKeyEvents()
        taskMgr.remove('UpdatePlayerTask')
        taskMgr.remove('UpdateBulletsTask')
        render.setLightOff(self.slnp)
        self.node.removeNode()
            
    """
    def __del__(self):
        print "Player deleted!"
    """