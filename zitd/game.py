from panda3d.core import *
from direct.showbase.ShowBase import ShowBase#@UnresolvedImport
from direct.showbase.DirectObject import DirectObject
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
        self.type = 'FPS' # 'FPS' or 'DEBUG'
        
        # Creating level geometry
        self.level = Level(self)
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
        #messenger.toggleVerbose()
        
        # Instance one monster (needs to be done after setting up collision manager
        self.baby = Monster(self, 'nos', (9,14))
        
        # Instance class for debug output
        self.debug = DebugOptions(self)
        
        # Debug
        #PStatClient.connect()
        #meter = SceneGraphAnalyzerMeter('meter', render.node())
        #meter.setupWindow(base.win) 
    
    def pause(self):
        self.player.clearKeyEvents()
        self.player.disconnectMouse()
        
    def resume(self):
        self.player.setKeyEvents()
        self.player.reconnectMouse()
