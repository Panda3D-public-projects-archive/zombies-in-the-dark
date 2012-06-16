from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from utils import *

COLL_PLAYER_WALL = BitMask32.bit(0)
COLL_BULLET_WALL_MONSTER = BitMask32.bit(1)
COLL_MONSTER_WALL = BitMask32.bit(2)
COLL_MONSTER_PLAYER_LOS = BitMask32.bit(3)

class CollisionManager(DirectObject):
    def __init__(self, parent):
        self.parent = parent
        
        # Create player collision objects
        self.player_cn = self.parent.player.node.attachNewNode(CollisionNode('PlayerCollisionNode'))
        self.player_cn.node().addSolid(CollisionSphere(0, 0, 0, 2))
        self.player_cn.node().setFromCollideMask(COLL_PLAYER_WALL)
        self.player_cn.node().setIntoCollideMask(COLL_MONSTER_PLAYER_LOS)
        #TODO: maknuti        
        #self.player_cn.show()    
        
        # FluidPusher will be used to handle player-wall collisions and automatically push player in the right direction
        self.pusher = CollisionHandlerFluidPusher()
        self.pusher.addInPattern('%fn-into-%in')
        self.pusher.addCollider(self.player_cn, self.parent.player.node)
        
        # CollisionHandlerEvent will be used to handle bullet collisions
        self.coll_event = CollisionHandlerEvent()
        self.coll_event.addInPattern('%fn-into-%in')
        
        # CollisionHandlerQueue will be used to handle monster-player wall collision
        self.coll_queue = CollisionHandlerQueue()
        
        # Set up traverser and add it to base.cTrav, this will make Panda automatically traverse every frame
        self.traverser = CollisionTraverser()
        self.traverser.addCollider(self.player_cn, self.pusher)
        self.traverser.setRespectPrevTransform(True) 
        base.cTrav = self.traverser
        
        # Set up another traverser for monster-player LoS checks
        self.los_traverser = CollisionTraverser() 
        
        # For debug purposes show collisions
        #base.cTrav.showCollisions(render)
        #self.los_traverser.showCollisions(render)
        
        self.accept('BulletCollisionNode-into-Wall', self.handleBulletWallCollision)
        self.accept('BulletCollisionNode-into-MonsterHeadCollisionNode', self.handleBulletMonsterHeadCollision)
        self.accept('BulletCollisionNode-into-MonsterBodyCollisionNode', self.handleBulletMonsterBodyCollision)
        self.accept('MonsterPusherCollisionNode-into-Wall', self.handleMonsterWallCollision)
        
        taskMgr.doMethodLater(1, self.monsterLosTraverseTask, 'MonsterLosTraverseTask')

    def createLevelCollision(self, level):
        level.ghostwall_node.setCollideMask(COLL_PLAYER_WALL | COLL_BULLET_WALL_MONSTER | COLL_MONSTER_WALL | COLL_MONSTER_PLAYER_LOS) 
    
    def createBulletCollision(self, bullet):
        bullet.cn = bullet.node.attachNewNode(CollisionNode('BulletCollisionNode'))
        bullet.cn.node().addSolid(CollisionSphere(0, 0, 0, 1.1))
        bullet.cn.node().setFromCollideMask(COLL_BULLET_WALL_MONSTER)
        bullet.cn.node().setIntoCollideMask(BitMask32.allOff())
        bullet.cn.node().setPythonTag('node', bullet)
        #TODO: maknuti
        #bullet.cn.show()        
        self.traverser.addCollider(bullet.cn, self.coll_event)
        
    def createMonsterCollision(self, monster):
        monster.cn_head = monster.head_node.attachNewNode(CollisionNode('MonsterHeadCollisionNode'))
        monster.cn_head.node().addSolid(CollisionSphere(0, 0, 0, 35))
        monster.cn_head.node().setIntoCollideMask(COLL_BULLET_WALL_MONSTER)
        monster.cn_head.node().setPythonTag('node', monster)
        monster.cn_head.setPos(0, -10, 30)
        monster.cn_body = monster.body_node.attachNewNode(CollisionNode('MonsterBodyCollisionNode'))
        monster.cn_body.node().addSolid(CollisionSphere(0, 0, 0, 40))
        monster.cn_body.node().setIntoCollideMask(COLL_BULLET_WALL_MONSTER)
        monster.cn_body.node().setPythonTag('node', monster)
        monster.cn_body.setPos(0, 0, 0)        
        # For some reason if we position collision node a bit below original node, collision pusher does not work
        monster.cn_pusher = monster.node.attachNewNode(CollisionNode('MonsterPusherCollisionNode'))
        monster.cn_pusher.node().addSolid(CollisionSphere(0, 0, 0, 1.8))
        monster.cn_pusher.node().setFromCollideMask(COLL_MONSTER_WALL)
        monster.cn_pusher.node().setIntoCollideMask(BitMask32.allOff())
        monster.cn_pusher.node().setPythonTag('node', monster)

        #TODO: maknuti        
        #monster.cn_head.show()  
        #monster.cn_body.show() 
        #monster.cn_pusher.show()
        
        # CollisionRay for monster-player LoS detection
        monster.ray = CollisionRay()
        monster.cn_ray = monster.node.attachNewNode(CollisionNode('MonsterRayCollisionNode'))
        monster.cn_ray.node().addSolid(monster.ray) 
        monster.cn_ray.node().setFromCollideMask(COLL_MONSTER_PLAYER_LOS)
        monster.cn_ray.node().setIntoCollideMask(BitMask32.allOff())
        monster.cn_ray.node().setPythonTag('node', monster)
        self.los_traverser.addCollider(monster.cn_ray, self.coll_queue)
        
        # Pusher for monster-wall detection
        self.pusher.addCollider(monster.cn_pusher, monster.node)
        self.traverser.addCollider(monster.cn_pusher, self.pusher)

    def checkMonsterPlayerLos(self, monster):
        """
        vector = self.player_cn.getPos(monster.cn_ray) - monster.cn_ray.getPos()
        vector.normalize()
        monster.ray.setDirection(vector)
        self.los_traverser.traverse(render)
        self.coll_queue.sortEntries()
        """
        if self.coll_queue.getNumEntries() > 0:
            for entry in self.coll_queue.getEntries():
                if monster == entry.getFromNodePath().getPythonTag('node'):
                    if entry.getIntoNode().getName() == 'PlayerCollisionNode':
                        return True
                    else:
                        return False
        return False

    def handleBulletWallCollision(self, entry):
        bullet_cn = entry.getFromNodePath()
        bullet = bullet_cn.getPythonTag('node')
        bullet_cn.clearPythonTag('node')
        if bullet in self.parent.player.bullet_objects:
            self.parent.player.bullet_objects.remove(bullet)
        if bullet != None:
            bullet.destroy()  
        
        
    def handleBulletMonsterHeadCollision(self, entry):
        bullet_cn = entry.getFromNodePath()
        bullet = bullet_cn.getPythonTag('node')
        if bullet in self.parent.player.bullet_objects:
            self.parent.player.bullet_objects.remove(bullet)
        if bullet != None:
            bullet.destroy() 
        
        monster_cn = entry.getIntoNodePath()
        monster = monster_cn.getPythonTag('node')
        monster.shot_head.play()
        monster.node.play('hit1')
        duration = monster.node.getNumFrames('hit1') / 24  # animation play rate
        taskMgr.doMethodLater(duration, monster.finishedAnim, 'FinishedAnim', extraArgs = [])        
        if monster.hp > HEADSHOT_DAMAGE:
            monster.hp -= HEADSHOT_DAMAGE
        else:
            monster.node.stop()
            monster.pauze()             
            monster.node.play('die')
            taskMgr.doMethodLater(3, self.parent.removeEnemy, 'RemoveEnemy', extraArgs = [monster])
        print monster.hp
        
    def handleBulletMonsterBodyCollision(self, entry):
        bullet_cn = entry.getFromNodePath()
        bullet = bullet_cn.getPythonTag('node')
        if bullet in self.parent.player.bullet_objects:
            self.parent.player.bullet_objects.remove(bullet)
        if bullet != None:
            bullet.destroy()        
        
        monster_cn = entry.getIntoNodePath()
        monster = monster_cn.getPythonTag('node')
        monster.shot_body.play()
        monster.node.play('hit2')
        duration = monster.node.getNumFrames('hit2') / 24  # animation play rate
        taskMgr.doMethodLater(duration, monster.finishedAnim, 'FinishedAnim', extraArgs = [])
        if monster.hp > BODYSHOT_DAMAGE:
            monster.hp -= BODYSHOT_DAMAGE
        else:          
            monster.node.stop()
            monster.pauze()            
            monster.node.play('die')
            taskMgr.doMethodLater(3, self.parent.removeEnemy, 'RemoveEnemy', extraArgs = [monster])             
        print monster.hp
        
    def handleMonsterWallCollision(self, entry):
        monster_cn = entry.getFromNodePath()
        monster = monster_cn.getPythonTag('node')        
        monster.hitWall()
        
    def monsterLosTraverseTask(self, task):
        for monster in self.parent.zombies:
            vector = self.player_cn.getPos(monster.cn_ray) - monster.cn_ray.getPos()
            vector.normalize()
            monster.ray.setDirection(vector)
        self.los_traverser.traverse(render)
        self.coll_queue.sortEntries()
        return task.again
        
    def cleanup(self):
        self.ignoreAll()
        taskMgr.remove('MonsterLosTraverseTask')
    
    """
    def __del__(self):
        print "Collision Manager deleted!"
    """