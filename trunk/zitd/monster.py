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
ACTION_CHASE = 2
ACTION_FOLLOW_PATH = 3
ACTION_MOVE = 4

ORDERS_PATROL = 1
ORDERS_IDLE = 0
ORDERS_HERDING = 2


MELEE_RANGE = 10
MELEE_TIME = 1.5 #seconds


SENSING_RANGE = 12
HEARING_RANGE = 20
VIEW_RANGE = 30


NORMAL_SPEED = 2
CHASE_SPEED = NORMAL_SPEED * 1.5


IDLE_TIME = 3 #seconds
IDLE_ROTATE_SPEED = 0.4


WAYPOINT_TIMER = 5 #sec

HERDING_TIMEOUT = 2 #sec



class Monster():
    def __init__(self, id, parent, type, pos):
        self.id = id
        self.parent = parent
        self.hp = 100
        self.speed = 1
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
            self.zpos = 0
            self.node.setPos(pos[0]*TILE_SIZE,pos[1]*TILE_SIZE,self.zpos)
            self.node.setScale(0.03)
            self.node.setTexture(loader.loadTexture('models/Zomby_D.png'))
            self.ts_normal = TextureStage('ts_normal')
            self.tex_normal = loader.loadTexture('models/Zomby_N.png')
            self.ts_normal.setMode(TextureStage.MNormal)
            self.node.setTexture(self.ts_normal, self.tex_normal)
            self.ts_gloss = TextureStage('ts_gloss')
            self.tex_gloss = loader.loadTexture('models/Zomby_S1.png')
            self.ts_gloss.setMode(TextureStage.MGloss)
            self.node.setTexture(self.ts_gloss, self.tex_gloss)            
            self.node.reparentTo(render) 
            self.node.loop('stand')
        elif type == 'nos':
            self.node = loader.loadModel('models/nos')
            self.zpos = 5
            self.node.setPos(pos[0]*TILE_SIZE,pos[1]*TILE_SIZE,self.zpos)
            self.node.setScale(2)
            if self.id == 1:
                self.node.setColor(1,0,0)
            elif self.id == 2:
                self.node.setColor(0,1,0)
            elif self.id == 3:
                self.node.setColor(0,0,1)
            else:
                self.node.setColor(1,1,1)
            self.node.reparentTo(render)


        #self.patrol_points = [(1,1), (4,11), (12,20), (18,4), (19,17)]
        
        #initialize 3d sound
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], base.camera)
        self.shot_head = self.audio3d.loadSfx('audio/Zombie In Pain-SoundBible.com-134322253.wav')
        self.shot_body = self.audio3d.loadSfx('audio/Zombie Moan-SoundBible.com-565291980.wav')
        self.moan1 = self.audio3d.loadSfx('audio/Mindless Zombie Awakening-SoundBible.com-255444348.wav')
        self.moan2 = self.audio3d.loadSfx('audio/Zombie Brain Eater-SoundBible.com-1076387080.wav')
        self.aggro_sound = self.audio3d.loadSfx('audio/Mummy Zombie-SoundBible.com-1966938763.wav')
        self.attack_sound = self.audio3d.loadSfx('audio/Chopping Off Limb-SoundBible.com-884800545.wav')
        self.audio3d.attachSoundToObject(self.moan1, self.node)
        self.audio3d.attachSoundToObject(self.moan2, self.node)
        self.audio3d.attachSoundToObject(self.shot_head, self.node)
        self.audio3d.attachSoundToObject(self.shot_body, self.node)
        self.audio3d.attachSoundToObject(self.aggro_sound, self.node)
        self.audio3d.attachSoundToObject(self.attack_sound, self.node)
        delay1 = Wait(25+d(15))
        delay2 = Wait(25+d(15))
        self.moan_sequence = Sequence(SoundInterval(self.moan1), delay1, SoundInterval(self.moan2), delay2)
        self.moan_sequence.loop()
        
        self.parent.collision_manager.createMonsterCollision(self)

        self.aggro_sound_last_played = 0
        #--------------------------brain-------------------------
        self.node.setH( 160 )
        
        self.pause = False

        self.action = ACTION_IDLE

        if percent(1):
            self.orders = ORDERS_PATROL
        else:
            self.orders = ORDERS_IDLE

        self.last_melee = 0
        
        self.player_last_seen_abs = None

        self.idle_timer = time.time()
        self.idle_value = 1

        self.current_waypoint = None

        #self.wait_until = None
        self.herding_timer = None

        self.path = None

        taskMgr.doMethodLater(1, self.behaviourTask, 'MonsterBehaviourTask'+str(self.id) )
        taskMgr.doMethodLater(1, self.debugMoveTask, 'MonsterMoveTask'+str(self.id))


    def getLOS(self):
        return self.parent.collision_manager.checkMonsterPlayerLos(self)


    def sensePlayer(self):
        """Return True if player sensed, and his last known coordinates are stored in self.player_last_seen_abs"""
        
        # if the player is dead, do not sense him
        if self.parent.player.health <= 0:
            return False

        #get player's position
        p_pos_abs = self.parent.player.node.getPos()
        my_pos_abs = self.node.getPos()


        #--------------------------------SENSE---------------------------------
        #if player is within SENSING_RANGE we know he is there
        if self.distanceToPlayer() < SENSING_RANGE:
            #print "TOO CLOSE LOOSER!"
            self.player_last_seen_abs = p_pos_abs
            return True


        #---------------------------------HEAR----------------------------------
        #if player is within HEARING_RANGE we know he is there
        effective_hearing_range = HEARING_RANGE
        
        if self.parent.player.gunshot_at:
            effective_hearing_range *= 3
        else:
            if self.parent.player.sprint:
                effective_hearing_range *= 2
            if not self.parent.player.moving:
                effective_hearing_range = 0
                
        if self.distanceToPlayer() < effective_hearing_range:
            print "I HEAR U!"
            self.parent.player.adrenaline()
            #if we can see go chase him
            if self.getLOS():
                self.player_last_seen_abs = p_pos_abs
                return True
                
            #we cannot see him, build new path to that tile
            else:
                dest = getTile( p_pos_abs )
                path = pathFind(self.parent.level, getTile( self.node.getPos()), dest)
                if path:
                    self.path = path 
                    self.orders = ORDERS_PATROL
                    self.action = ACTION_FOLLOW_PATH
                    return False
                

        #-------------------------------SEE---------------------------------
        #if player is in front of us
        if self.angleToPlayerAbs() <= 45:
            if self.id == 1:
                print self.id, "player in front LOS:", self.getLOS()
            #if he is close enough to see and we can see him
            if self.distanceToPlayer() <= VIEW_RANGE and self.getLOS():
                self.player_last_seen_abs = p_pos_abs
                print "vidim!"
                return True
            
            #if player has a flashlight lit, and we can see him go after him
            if self.parent.player.flashlight and self.getLOS():
                self.player_last_seen_abs = p_pos_abs
                print "vidim flashlight"
                return True
                
                
        #---------------------SEE MY OWN SHADOW---------------------------
        #if player is behind us and has a lit up flashlight and we have LOS to him
        if self.angleToPlayerAbs() > 135 and self.angleToPlayerAbs() < 225:
            if self.id == 1:            
                print self.id, "player in back, LOS:", self.getLOS()
            
            if self.parent.player.flashlight and self.getLOS():
            
                #if he is looking at us
                my_pos_rel = self.node.getPos( self.parent.player.node )
                forward = Vec2( 0, 1 )
                if math.fabs( forward.signedAngleDeg( Vec2( my_pos_rel[0], my_pos_rel[1] ) ) ) <= 30:
                    #go after my own shadow
                    print "herding"
                    self.orders = ORDERS_HERDING
                    self.node.setH( self.parent.player.node.getH() )
                    self.herding_timer = time.time()
                
        return False        


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
        if self.pause:
            return task.again
        
        #top priority, if we sense a player, go after him!
        if self.sensePlayer():
            if time.time() - self.aggro_sound_last_played > 5:
                self.aggro_sound.play()
                self.aggro_sound_last_played = time.time()
            
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
            dest = self.getNewPatrolPoint()
            self.path = pathFind(self.parent.level, getTile(self.node.getPos()), dest)
            self.action = ACTION_FOLLOW_PATH
                

        elif self.orders == ORDERS_HERDING:
            self.action = ACTION_MOVE
            if time.time() - self.herding_timer > HERDING_TIMEOUT:
                self.orders = ORDERS_IDLE
                
             
        return task.again
    
    
    def debugMoveTask(self, task):
        if self.pause:
            return task.cont

        #print "orders:", self.orders
        
        if self.action == ACTION_CHASE:
            self.parent.player.adrenaline()
            look_pos = Point3(self.player_last_seen_abs.getX(), self.player_last_seen_abs.getY(), self.zpos)
            self.node.lookAt( look_pos )
            self.node.setFluidPos(self.node, 0, CHASE_SPEED*globalClock.getDt(), 0)
                        
            if self.distanceToPlayer() <= MELEE_RANGE and self.angleToPlayerAbs() <= 45 and self.getLOS():
                if time.time() - self.last_melee >= MELEE_TIME:
                    self.attack_sound.play()
                    self.parent.player.getDamage()
                    self.last_melee = time.time()
        
 
        elif self.action == ACTION_IDLE:
            if time.time() - self.idle_timer > IDLE_TIME:
                #we are standing still and rotating, see on whic side we will rotate now
                self.idle_timer = time.time()
                if percent(20):
                    self.idle_value *= -1
            self.rotateBy( self.idle_value * IDLE_ROTATE_SPEED )


        elif self.action == ACTION_FOLLOW_PATH:
            #if we dont have a waypoint, calculate one
            if not self.current_waypoint:
                try:
                    #get next tile from path
                    tile = self.path[0]
                    self.path = self.path[1:]
                    
                    #calculate waypoint
                    varx= 5 - (d(4) + d(4))
                    vary= 5 - (d(4) + d(4))
                    self.current_waypoint = (Point3( tile[0] * TILE_SIZE + varx, tile[1] * TILE_SIZE + vary, self.zpos ), time.time() )
                    #print "waypoint:", self.current_waypoint 
                    self.node.lookAt( self.current_waypoint[0] )
                    
                except (IndexError, TypeError):
                    #we have reached the end of path
                    self.orders = ORDERS_IDLE
                    self.current_waypoint = None
                    
            #if we have a waypoint move forward towards it, and check if we arrived at it
            else:
                self.node.setFluidPos(self.node, 0, NORMAL_SPEED*globalClock.getDt(), 0)
                my_pos = self.node.getPos() 
                
                #if we are close enough to the waypoint or if we didnt get to waypoint in time, delete it so we know we need a new one
                if math.fabs( my_pos[0] - self.current_waypoint[0][0] ) < 1 and math.fabs( my_pos[1] - self.current_waypoint[0][1] ) < 2 \
                        or time.time() - self.current_waypoint[1] > WAYPOINT_TIMER:
                    self.current_waypoint = None 


        elif self.action == ACTION_MOVE:
            self.node.setFluidPos(self.node, 0, NORMAL_SPEED*globalClock.getDt(), 0)            
 
 
        return task.cont


    def rotateBy(self, value):
        self.node.setH( (self.node.getH() + value) % 360  )
        

    def getNewPatrolPoint(self):
        lvl = self.parent.level
        allTiles = lvl.getFloorTiles()
        while True:
            t = ( d(lvl.getMaxX()), d(lvl.getMaxY()) )
            if t in allTiles:
                return t
            

    def hitWall(self):
        
        if self.action == ACTION_CHASE:
            return
    
        #print "lupio!"
        """self.moan1.play()
        self.rotateBy( 180 )
        self.node.setFluidPos(self.node, 0, CHASE_SPEED*globalClock.getDt(), 0)            
        #self.action = IDLE
        """
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

    def pauze(self):
        if self.moan_sequence:
            self.moan_sequence.pause()
        self.pause = True

        
    def resume(self):
        if self.moan_sequence:
            self.moan_sequence.resume()
        self.pause = False
        
        
    def destroy(self):
        self.audio3d.detachSound(self.moan1)
        self.audio3d.detachSound(self.moan2)
        self.audio3d.detachSound(self.shot_head)
        self.audio3d.detachSound(self.shot_body)
        self.audio3d.detachSound(self.aggro_sound)
        self.audio3d.detachSound(self.attack_sound)
        if self.moan_sequence != None:
            self.moan_sequence.pause()
            self.moan_sequence = None
        taskMgr.remove('MonsterBehaviourTask'+str(self.id))
        taskMgr.remove('MonsterMoveTask'+str(self.id))
        self.cn_head.node().clearPythonTag('node')
        self.cn_body.node().clearPythonTag('node')
        self.cn_pusher.node().clearPythonTag('node')  
        self.cn_ray.node().clearPythonTag('node')
        #TODO: vratiti kad bude Actor
        #self.node.delete()
        #self.node.cleanup()
        self.node.removeNode()

    #TODO: Obavezno obrisati!!        
    def __del__(self):
        print("Zombie deleted")
    