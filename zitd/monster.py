from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.interval.SoundInterval import SoundInterval
from utils import *
from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from AStar import pathFind
import random
import time
import math
from utils import *


ACTION_IDLE = 0
ACTION_MOVE = 1
ACTION_CHASE = 2
ACTION_FOLLOW_PATH = 3

ORDERS_PATROL = 1
ORDERS_IDLE = 0

MELEE_RANGE = 10
MELEE_TIME = 1.5 #seconds

SENSING_RANGE = 12

NORMAL_SPEED = 2
CHASE_SPEED = NORMAL_SPEED * 1.5


IDLE_TIME = 3 #seconds
IDLE_ROTATE_SPEED = 0.4



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
        elif type == 'nos':
            self.node = loader.loadModel('models/nos')
            self.node.setPos(pos[0]*TILE_SIZE,pos[1]*TILE_SIZE,5)
            self.node.setScale(2)
            self.node.setColor(1,0,0)
            self.node.reparentTo(render)

        self.patrol_points = [(1,1), (4,11), (12,20), (18,4), (19,17)]
        
        #initialize 3d sound
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], base.camera)
        self.shot_head = self.audio3d.loadSfx('audio/Zombie In Pain-SoundBible.com-134322253.wav')
        self.shot_body = self.audio3d.loadSfx('audio/Zombie Moan-SoundBible.com-565291980.wav')
        self.moan1 = self.audio3d.loadSfx('audio/Mindless Zombie Awakening-SoundBible.com-255444348.wav')
        self.moan2 = self.audio3d.loadSfx('audio/Zombie Brain Eater-SoundBible.com-1076387080.wav')
        self.audio3d.attachSoundToObject(self.moan1, self.node)
        self.audio3d.attachSoundToObject(self.moan2, self.node)
        self.audio3d.attachSoundToObject(self.shot_head, self.node)
        self.audio3d.attachSoundToObject(self.shot_body, self.node)
        delay = Wait(15)
        self.moan_sequence = Sequence(SoundInterval(self.moan1), delay, SoundInterval(self.moan2), delay).loop()
        self.moan_sequence = None
        self.move_sequence = None
        
        self.parent.collision_manager.createMonsterCollision(self)


        #--------------------------brain-------------------------
        self.node.setH( 160 )
        self.old_pos = self.node.getPos()
        
        self.pause = False

        self.action = ACTION_IDLE

        if percent(50):
            self.orders = ORDERS_PATROL
        else:
            self.orders = ORDERS_IDLE

        self.last_melee = 0
        
        self.player_last_seen_abs = None

        self.idle_timer = time.time()
        self.idle_value = 1

        self.current_waypoint = None

        taskMgr.doMethodLater(1, self.behaviourTask, 'behtask')
        taskMgr.doMethodLater(1, self.debugMoveTask, 'DebugMoveMonsterTask')



    def moveSequence(self):
        move = Sequence()
        start = self.node.getPos()
        for p in self.path:
            dest = Point3(p[0]*TILE_SIZE, p[1]*TILE_SIZE, 5)
            i = Sequence(self.node.posInterval(self.speed, dest, start), Func(self.updatePosition, p))
            start = dest
            move.append(i)
        move.append(Func(self.setAction, 'stand'))
        return move
        
        
    def updatePosition(self, dest):
        self.pos = dest


    def setAction(self, action):
        self.action = action


    def sensePlayer(self):
        """Return True if player sensed, and his last known coordinates are stored in self.player_last_seen_abs"""

        p_pos_abs = self.parent.player.node.getPos()
        my_pos_abs = self.node.getPos()

        
        #if player is within SENSING_RANGE we know he is there
        if self.distanceToPlayer() < SENSING_RANGE:
            #print "TOO CLOSE LOOSER!"
            self.player_last_seen_abs = p_pos_abs
            
            #print "tile:", ( p_pos_abs[0]/TILE_SIZE, p_pos_abs[1]/TILE_SIZE ), "  pos:", p_pos_abs
            
            return True
        
        
        
        #if player is in front of us
        if self.angleToPlayerAbs() <= 45:
            #print "napred mi je"
            #TODO: if LOS return True
            pass
        
        pass


    def distanceToPlayer(self):
        p_pos_abs = self.parent.player.node.getPos()
        my_pos_abs = self.node.getPos()
        return math.sqrt( math.pow( p_pos_abs[0] - my_pos_abs[0], 2) +  math.pow( p_pos_abs[1] - my_pos_abs[1], 2) )
        
        
    def angleToPlayer(self):
        p_pos_rel = self.parent.player.node.getPos( self.node )        
        forward = Vec2( 0, 1 )
        return forward.signedAngleDeg( Vec2( p_pos_rel[0], p_pos_rel[1] ) )
        
        
    def angleToPlayerAbs(self):
        return math.fabs( self.angleToPlayer() )


    def behaviourTask(self, task):
        
        #top priority, if we sense a player, go after him!
        if self.sensePlayer():
            print "CHASE!!!!"
            self.action = ACTION_CHASE
            return task.again

        
        elif self.orders == ORDERS_IDLE:
            
            #percent chance to go on patrol
            if percent( 10 ):
                self.orders = ORDERS_PATROL
                return task.again
                      
            self.action = ACTION_IDLE
            
        
        elif self.orders == ORDERS_PATROL:
            
            #percent chance to get idle
            if percent( 1 ):
                self.orders = ORDERS_IDLE
                return task.again
                      
            #if we are already patroling, dont change anything 
            if self.action == ACTION_FOLLOW_PATH:
                return task.again


            #build a new path for patrol                
            self.action = ACTION_FOLLOW_PATH
            self.dest = self.pos
            while self.dest == self.pos:
                self.dest = self.patrol_points[random.randint(0,4)]
            self.path = pathFind(self.parent.level, self.pos, self.dest)
            #self.move_sequence = self.moveSequence()
            #self.move_sequence.start()

             
        return task.again
    
    
    def debugMoveTask(self, task):
        if self.pause:
            return task.cont
        
        if self.action == ACTION_CHASE:
            self.node.lookAt( self.player_last_seen_abs )
            self.node.setPos(self.node, 0, CHASE_SPEED*globalClock.getDt(), 0)
                        
            if self.distanceToPlayer() <= MELEE_RANGE and self.angleToPlayerAbs() <= 45:
                if time.time() - self.last_melee >= MELEE_TIME:
                    self.parent.player.getDamage()
                    self.last_melee = time.time()

        
        elif self.action == ACTION_MOVE:
            self.old_pos = self.node.getPos()
            self.node.setPos(self.node, 0, NORMAL_SPEED*globalClock.getDt(), 0)

 
        elif self.action == ACTION_IDLE:
            if time.time() - self.idle_timer > IDLE_TIME:
                
                #we are standing still and rotating, see on whic side we will rotate now
                self.idle_timer = time.time()
                if percent(20):
                    self.idle_value *= -1
                    
            self.rotateBy( self.idle_value * IDLE_ROTATE_SPEED )


        if self.action == ACTION_FOLLOW_PATH:
            
            #if we dont have a waypoint, calculate one
            if not self.current_waypoint:
                try:
                    #get next tile from path
                    tile = self.path[0]
                    self.path = self.path[1:]
                    
                    #calculate waypoint
                    varx= 6 - (d(5) + d(5))
                    vary= 6 - (d(5) + d(5))
                    self.current_waypoint = Point3( tile[0] * 10 + varx, tile[1] * 10 + vary, 0 )
                    #print "waypoint:", self.current_waypoint 
                    self.node.lookAt( self.current_waypoint )
                    
                except IndexError:
                    #we have reached the end of path
                    self.orders = ORDERS_IDLE
                    self.current_waypoint = None
                    
            #if we have a waypoint move forward towards it, and check if we arrived at it
            else:
                self.node.setPos(self.node, 0, NORMAL_SPEED*globalClock.getDt(), 0)
                my_pos = self.node.getPos() 
                
                #if we are close enough to the waypoint, delete it so we know we need a new one
                if math.fabs( my_pos[0] - self.current_waypoint[0] ) < 1 and math.fabs( my_pos[1] - self.current_waypoint[1] ) < 1:
                    self.current_waypoint = None 
 
        return task.cont


    def rotateBy(self, value):
        self.node.setH( (self.node.getH() + value) % 360  )
        

    def hitWall(self, pos):
        
        #self.action = IDLE
        
        #move a step back
        #self.node.setPos(render, self.old_pos)        
        """
        old = self.node.getH()
        rnd = 80 + random.randint( 0, 20 )

        forward = Vec2( 0, 1 )
        impact = Vec2( pos[0], pos[1] )

        angle = forward.signedAngleDeg( impact )
        #print "angle:", angle
        
        if angle < 0:
            #+ cause angle is negative
            rnd = 91 + angle
            self.node.setH( (self.node.getH() + rnd)%360 )            
        elif angle > 0:
            rnd = -91 + angle
            self.node.setH( (self.node.getH() + rnd)%360 )
        
        #print "stari:", old, "  novi:", self.node.getH()    
        """ 
        pass

    def pause(self):
        self.moan_sequence.pause()
        self.pause = True
        
        
    def resume(self):
        self.moan_sequence.resume()
        self.pause = False
        
        
    def destroy(self):
        self.audio3d.detachSound(self.moan1)
        self.audio3d.detachSound(self.moan2)
        self.audio3d.detachSound(self.shot_head)
        self.audio3d.detachSound(self.shot_body)
        if self.moan_sequence != None:
            self.moan_sequence.pause()
            self.moan_sequence = None
        if self.move_sequence != None:
            self.move_sequence.pause()
            self.move_sequence = None    
        taskMgr.remove('behtask')
        taskMgr.remove('DebugMoveMonsterTask')
        #TODO: vratiti kad bude Actor
        #self.node.delete()
        #self.node.cleanup()
        self.node.removeNode()

        
    """
    def __del__(self):
        print("Instance of Custom Class Alpha Removed")
    """        