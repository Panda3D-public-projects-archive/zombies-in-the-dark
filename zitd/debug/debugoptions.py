from direct.task.Task import Task
from direct.showbase.PythonUtil import clampScalar
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from utils import *
from debug.spotlightpanel import SpotlightPanel

class DebugOptions(DirectObject):
    def __init__(self, parent):
        self.parent = parent
        self.textPlayerPos = OnscreenText(text = '', parent=base.a2dTopLeft, pos = (0, -0.1), scale = 0.04,fg=(1, 1, 1, 1),align=TextNode.ALeft)
        
        self.showFps = True
        base.setFrameRateMeter(True)
        
        self.ambientLight = True
        self.parent.alight.setColor(VBase4(0.43, 0.43, 0.43, 1.0))
        
        self.flashlightFrustum = False
        
        self.autoShader = True
        render.setShaderAuto()
        
        self.playerPos = True
        taskMgr.add(self.refreshPlayerPos, 'RefreshPlayerPosTask')
        self.textPlayerPos.reparentTo(base.a2dTopLeft)
        
        self.bloom = False
        self.blur = False
        self.ao = False
        
        self.walls = True
        
        #spotlightpanel
        self.spot_light_panel = SpotlightPanel(self, self.parent.player.slight)
        
        base.accept('f1', self.toggleFps)
        base.accept('f2', self.toggleAmbientLight)
        base.accept('f3', self.toggleFlashlightFrustum)
        base.accept('f4', self.parent.player.getDamage)
        base.accept('f5', self.toggleAutoShader)
        base.accept('f6', self.togglePlayerPos)
        base.accept('f7', self.toggleBloom)
        base.accept('f8', self.toggleBlur)
        base.accept('f9', self.toggleAO)
        base.accept('f10', self.toggleWalls)
        base.accept('f11', render.analyze)
        base.accept('f12', self.debugPrint)
    
    def toggleFps(self):
        if self.showFps == False:
            self.showFps = True
            base.setFrameRateMeter(True)
        else:
            self.showFps = False
            base.setFrameRateMeter(False)
    
    def toggleAmbientLight(self):
        if self.ambientLight == False:
            self.ambientLight = True
            self.parent.alight.setColor(VBase4(0.43, 0.43, 0.43, 1.0))
        else:
            self.ambientLight = False
            self.parent.alight.setColor(VBase4(0.03, 0.03, 0.03, 1.0))
            
    def toggleFlashlightFrustum(self):
        if self.flashlightFrustum == False:
            self.flashlightFrustum = True
            self.parent.slight.showFrustum()
        else:
            self.flashlightFrustum = False
            self.parent.slight.hideFrustum()            
    
    def toggleAutoShader(self):
        if self.autoShader == False:
            self.autoShader = True
            render.setShaderAuto()
        else:
            self.autoShader = False
            render.setShaderOff()
            
    def toggleWalls(self):
        if self.walls == False:
            self.walls = True
            self.parent.level.wall_node.reparentTo(self.parent.level.node)
        else:
            self.walls = False
            self.parent.level.wall_node.detachNode()
    
    def togglePlayerPos(self): 
        if self.playerPos == False:
            self.playerPos = True
            taskMgr.add(self.refreshPlayerPos, 'RefreshPlayerPosTask')
            self.textPlayerPos.reparentTo(base.a2dTopLeft)
        else:
            self.playerPos = False
            taskMgr.remove('RefreshPlayerPosTask')
            self.textPlayerPos.detachNode() 
            
    def toggleBloom(self):
        if self.bloom == False:
            self.bloom = True
            self.parent.filters.setBloom()
        else:
            self.bloom = False
            self.parent.filters.delBloom()   
            
    def toggleBlur(self):
        if self.blur == False:
            self.blur = True
            self.parent.filters.setBlurSharpen()
        else:
            self.blur = False
            self.parent.filters.delBlurSharpen() 
            
    def toggleAO(self):
        if self.ao == False:
            self.ao = True
            self.parent.filters.setAmbientOcclusion()
        else:
            self.ao = False
            self.parent.filters.delAmbientOcclusion()             
        
    def refreshPlayerPos(self, task):
        px, py, pz = self.parent.player.node.getPos()
        self.textPlayerPos.setText('Player pos: (%0.3f, %0.3f, %0.3f)' % (px, py, pz))
        return task.cont         

    def debugPrint(self):
        print taskMgr