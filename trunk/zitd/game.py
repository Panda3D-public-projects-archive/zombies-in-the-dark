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
            self.aim_node = aspect2d.attachNewNode(cm.generate())
            self.aim_node.setTexture(loader.loadTexture('models/aim.png'))
            self.aim_node.setTransparency(TransparencyAttrib.MAlpha)
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
        
        self.zombies = []
        self.spawnEnemy()
        
        # Instance class for debug output
        #self.debug = DebugOptions(self)
        
        # Setup default options (which have been previously set in DebugOptions)
        # If you uncomment DebugOptions, comment out two lines below
        self.alight.setColor(VBase4(0.03, 0.03, 0.03, 1.0))
        render.setShaderAuto()
        
        # Instance common filters class (blur, AO, bloom)
        self.filters = CommonFilters(base.win, base.cam)
        
        # Debug
        #PStatClient.connect()
        #meter = SceneGraphAnalyzerMeter('meter', render.node())
        #meter.setupWindow(base.win) 
        #messenger.toggleVerbose()        
    
    def gameWin(self):
        self.player.can_move = False
        i = LEVELS.index(self.level.name)
        i += 1
        # Player finished all levels
        if len(LEVELS) == i:
            self.player.heart_sound.stop()
            self.parent.fsm.request('GameWin')
        # Player not yet finished all levels, move to next level
        else:
            self.player.heart_sound.stop()
            
            # Clean up
            for z in self.zombies[:]:
                z.destroy()            
                self.zombies.remove(z)
            for l in self.level.light_nodes:
                render.setLightOff(l)                
            self.level.destroy()
            self.level = None
            
            # Reinit
            self.level = Level(self, LEVELS[i])
            self.collision_manager.createLevelCollision(self.level)
            self.spawnEnemy()           
            self.player.node.setPos(self.level.start_pos[0]*TILE_SIZE,self.level.start_pos[1]*TILE_SIZE,TILE_SIZE*ASPECT/1.5)
            self.player.can_move = True
            self.player.bullets += 2
            if self.player.bullets > self.player.max_bullets:
                self.player.bullets = self.player.max_bullets
            self.parent.gameui.refreshBullets()
            render.setShaderAuto()
    
    def gameOver(self):
        self.player.heart_sound.stop()
        self.player.clearKeyEvents()
        self.player.disconnectMouse()
        self.parent.gameOver()
        
    def spawnEnemy(self):
        lst = self.level.getAiList()
        zombie_counter = 0
        for pos in lst:
            self.zombies.append( Monster(zombie_counter, self, 'baby', pos) )
            zombie_counter += 1
            #if zombie_counter > 3:
            #    break
            
    def removeEnemy(self, monster):
        monster.destroy()
        if monster in self.zombies:
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
        self.player.heart_sound.stop()        
        self.aim_node.removeNode()
        render.setLightOff(self.alnp)
        self.alnp.removeNode()        
        
    """
    def __del__(self):
        print "Game deleted!"
    """