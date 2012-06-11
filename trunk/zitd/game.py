from panda3d.core import *
from direct.showbase.ShowBase import ShowBase#@UnresolvedImport
from direct.showbase.DirectObject import DirectObject
from debug.debugoptions import DebugOptions
from debug.cameramanager import CameraManager
from player import Player
from utils import *
from level import Level
from monster import Monster

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
        # Create player flashlight
        self.slight = Spotlight('slight')
        self.slight.setColor(VBase4(1, 1, 0.6, 1))
        #self.lens = PerspectiveLens()
        #self.slight.setLens(self.lens)
        self.slnp = self.player.node.attachNewNode(self.slight)
        self.slnp.node().getLens().setFov(55)
        self.slnp.node().getLens().setNearFar(1, 10)
        self.slight.setExponent(45)
        self.slight.setAttenuation(Point3(0.737, 0.134, 0.001))
        render.setLight(self.slnp)
        
        # Instance one monster
        self.baby = Monster(self, 'nos', (19,17))
        
        # Create ambient light
        self.alight = AmbientLight("alight")
        self.alnp = render.attachNewNode(self.alight)
        render.setLight(self.alnp)
        
        # Instance collision objects
        self.pusher = CollisionHandlerFluidPusher()
        self.pusher.addCollider(self.player.cn, self.player.node)
        self.traverser = CollisionTraverser()
        self.traverser.addCollider(self.player.cn, self.pusher)
        self.traverser.setRespectPrevTransform(True) 
        base.cTrav = self.traverser
        #base.cTrav.showCollisions(render)
        self.level.wall_node.setCollideMask(BitMask32.bit(0))
        
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
