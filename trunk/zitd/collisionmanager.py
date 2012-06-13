from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from utils import *

COLL_PLAYER_WALL = BitMask32.bit(0)
COLL_BULLET_WALL_MONSTER = BitMask32.bit(1)
COLL_MONSTER_WALL = BitMask32.bit(2)

class CollisionManager(DirectObject):
    def __init__(self, parent):
        self.parent = parent
        
        # Create player collision objects
        self.player_cn = self.parent.player.node.attachNewNode(CollisionNode('PlayerCollisionNode'))
        self.player_cn.node().addSolid(CollisionSphere(0, 0, 0, 1.8))
        self.player_cn.node().setFromCollideMask(COLL_PLAYER_WALL)
        #TODO: maknuti        
        self.player_cn.show()
        
        # Create wall collision objects
        self.parent.level.wall_node.setCollideMask(COLL_PLAYER_WALL | COLL_BULLET_WALL_MONSTER | COLL_MONSTER_WALL)        
        
        # FluidPusher will be used to handle player-wall collisions and automatically push player in the right direction
        self.pusher = CollisionHandlerFluidPusher()
        self.pusher.addCollider(self.player_cn, self.parent.player.node)
        
        # CollisionHandlerEvent will be used to handle bullet collisions
        self.coll_event = CollisionHandlerEvent()
        self.coll_event.addInPattern('%fn-into-%in')
        
        # Set up traverser and add it to base.cTrav, this will make Panda automatically traverse every frame
        self.traverser = CollisionTraverser()
        self.traverser.addCollider(self.player_cn, self.pusher)
        self.traverser.setRespectPrevTransform(True) 
        base.cTrav = self.traverser
        
        # For debug purposes show collisions
        #base.cTrav.showCollisions(render)
        
        self.accept('BulletCollisionNode-into-Wall', self.handleBulletWallCollision)
        self.accept('BulletCollisionNode-into-MonsterHeadCollisionNode', self.handleBulletMonsterHeadCollision)
        self.accept('BulletCollisionNode-into-MonsterBodyCollisionNode', self.handleBulletMonsterBodyCollision)
        self.accept('MonsterBodyCollisionNode-into-Wall', self.handleMonsterWallCollision)

    def createBulletCollision(self, bullet):
        bullet.cn = bullet.node.attachNewNode(CollisionNode('BulletCollisionNode'))
        bullet.cn.node().addSolid(CollisionSphere(0, 0, 0, 1.1))
        bullet.cn.node().setFromCollideMask(COLL_BULLET_WALL_MONSTER)
        bullet.cn.node().setPythonTag('node', bullet)
        #TODO: maknuti
        bullet.cn.show()        
        self.traverser.addCollider(bullet.cn, self.coll_event)
        
    def createMonsterCollision(self, monster):
        monster.cn_head = monster.node.attachNewNode(CollisionNode('MonsterHeadCollisionNode'))
        monster.cn_head.node().addSolid(CollisionSphere(0, 0, 0, 1.5))
        monster.cn_head.node().setCollideMask(COLL_BULLET_WALL_MONSTER)
        monster.cn_head.node().setPythonTag('node', monster)
        monster.cn_body = monster.node.attachNewNode(CollisionNode('MonsterBodyCollisionNode'))
        monster.cn_body.node().addSolid(CollisionSphere(0, 0, 0, 1.5))
        monster.cn_body.node().setCollideMask(COLL_BULLET_WALL_MONSTER)
        monster.cn_body.node().setFromCollideMask(COLL_MONSTER_WALL)
        monster.cn_body.node().setPythonTag('node', monster)
        #TODO: bolje podesiti collision sphere kad dodju pravi modeli
        monster.cn_body.setPos(0,0,-2)
        #TODO: maknuti        
        monster.cn_head.show()  
        monster.cn_body.show()   
        self.traverser.addCollider(monster.cn_body, self.coll_event)   
        #self.pusher.addCollider(monster.cn_body, monster.node)
        #self.traverser.addCollider(monster.cn_body, self.pusher)

    def handleBulletWallCollision(self, entry):
        bullet_cn = entry.getFromNodePath()
        bullet = bullet_cn.getPythonTag('node')
        bullet_cn.clearPythonTag('node')
        if bullet in self.parent.player.bullet_objects:
            self.parent.player.bullet_objects.remove(bullet)
        bullet.destroy()  
        
        
    def handleBulletMonsterHeadCollision(self, entry):
        bullet_cn = entry.getFromNodePath()
        bullet = bullet_cn.getPythonTag('node')
        bullet_cn.clearPythonTag('node')
        if bullet in self.parent.player.bullet_objects:
            self.parent.player.bullet_objects.remove(bullet)
        bullet.destroy() 
        
        monster_cn = entry.getIntoNodePath()
        monster = monster_cn.getPythonTag('node')
        monster.shot_head.play()
        if monster.hp > HEADSHOT_DAMAGE:
            monster.hp -= HEADSHOT_DAMAGE
        else:
            monster_cn.clearPythonTag('node')
            monster.cn_body.node().clearPythonTag('node')
            monster.destroy()
        print monster.hp
        
    def handleBulletMonsterBodyCollision(self, entry):
        bullet_cn = entry.getFromNodePath()
        bullet = bullet_cn.getPythonTag('node')
        bullet_cn.clearPythonTag('node')
        if bullet in self.parent.player.bullet_objects:
            self.parent.player.bullet_objects.remove(bullet)
        bullet.destroy()        
        
        monster_cn = entry.getIntoNodePath()
        monster = monster_cn.getPythonTag('node')
        monster.shot_body.play()
        if monster.hp > BODYSHOT_DAMAGE:
            monster.hp -= BODYSHOT_DAMAGE
        else:
            monster_cn.clearPythonTag('node')
            monster.cn_head.node().clearPythonTag('node')
            monster.destroy()
        print monster.hp
        
    def handleMonsterWallCollision(self, entry):
        #print dir( entry )
        #print entry
        monster_cn = entry.getFromNodePath()
        monster = monster_cn.getPythonTag('node')        
        #print monster.hp
        
        
        #print "point",entry.getInteriorPoint( monster_cn )
        #print "pos",entry.getContactPos( monster_cn )
        #print "pos",entry.getContactPos( render )
        #print "normal",entry.getContactNormal( monster_cn )
        #print "surface normal",entry.getSurfaceNormal( monster_cn )
        
        monster.hitWall( entry.getInteriorPoint( monster_cn ) )
        
        