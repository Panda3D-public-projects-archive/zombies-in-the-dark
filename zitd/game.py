from panda3d.core import *
from direct.showbase.ShowBase import ShowBase#@UnresolvedImport
from direct.showbase.DirectObject import DirectObject
from direct.filter.CommonFilters import CommonFilters
from debug.debugoptions import DebugOptions
from debug.cameramanager import CameraManager
from player import Player
from utils import *
from level import Level
from monster import Monster
from collisionmanager import CollisionManager

class Game(DirectObject):
    def __init__(self, parent):
        base.win.setClearColor(VBase4(0, 0, 0, 0))
        self.parent = parent
        # GAMETYPE
        self.type = 'DEBUG' # 'FPS' or 'DEBUG'
        self.type = 'FPS' # 'FPS' or 'DEBUG'
        
        # Creating level geometry
        self.level = Level(self, LEVELS[0])
        # Instance the player controller
        self.player = Player(self, self.level.start_pos)
        if self.type == 'FPS':
            base.disableMouse()
            base.camera.reparentTo(self.player.node)
            base.camLens.setFov(100)
            # Load aim icon
            cm = CardMaker('aim_node')
            cm.setFrame(-0.02, 0.02, -0.02, 0.02)
            aim_node = aspect2d.attachNewNode(cm.generate())
            aim_node.setTexture(loader.loadTexture('models/aim.png'))
            aim_node.setTransparency(TransparencyAttrib.MAlpha)
        elif self.type == 'DEBUG':
            base.disableMouse()
            self.camera = CameraManager(self)
        
        # Create ambient light
        self.alight = AmbientLight("alight")
        self.alnp = render.attachNewNode(self.alight)
        render.setLight(self.alnp)
        
        # Instance collision manager
        self.collision_manager = CollisionManager(self)
        self.collision_manager.createLevelCollision(self.level)
        #messenger.toggleVerbose()
        
        self.zombies = []
        self.zombie_counter = 0
        # Instance one monster (needs to be done after setting up collision manager
        for i in xrange(3):
            self.spawnEnemy()
        
        # Instance class for debug output
        self.debug = DebugOptions(self)
        
        # Instance common filters class (blur, AO, bloom)
        self.filters = CommonFilters(base.win, base.cam)
        
        # Debug
        #PStatClient.connect()
        #meter = SceneGraphAnalyzerMeter('meter', render.node())
        #meter.setupWindow(base.win) 
    
    def gameWin(self):
        self.player.can_move = False
        i = LEVELS.index(self.level.name)
        i += 1
        # Player finished all levels
        if len(LEVELS) == i:
            print "YOU WIN THA GAME!"
        # Player not yet finished all levels, move to next level
        else:
            self.cleanup()
            self.level = Level(self, LEVELS[i])
            self.collision_manager.createLevelCollision(self.level)
            self.zombie_counter = 0
            for i in xrange(3):
                self.spawnEnemy()           
            self.player.node.setPos(self.level.start_pos[0]*TILE_SIZE,self.level.start_pos[1]*TILE_SIZE,TILE_SIZE*ASPECT/1.5)
            self.player.can_move = True
            
    def spawnEnemy(self):
        allTiles = self.level.getFloorTiles()
        while True:
            t = ( d(self.level.getMaxX()), d(self.level.getMaxY()) )
            if t in allTiles:
                break
        self.zombie_counter += 1
        #if self.zombie_counter == 1:
        #    t = (9,13)
        self.zombies.append( Monster(self.zombie_counter, self, 'baby', t) )
    
    def removeEnemy(self, monster):
        monster.destroy()
        self.zombies.remove(monster)
      
    def pause(self):
        self.player.clearKeyEvents()
        self.player.disconnectMouse()
        self.player.pause = True
        for z in self.zombies:
            z.pauze()
        
    def resume(self):
        self.player.setKeyEvents()
        self.player.reconnectMouse()
        self.player.pause = False
        for z in self.zombies:
            z.resume()
            
    def cleanup(self):
        for z in self.zombies[:]:
            z.destroy()            
            self.zombies.remove(z)
        self.level.destroy()
        self.level = None