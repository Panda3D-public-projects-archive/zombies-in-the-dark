from panda3d.core import TextNode, BitMask32, TextureStage, NodePath, DirectionalLight, AmbientLight, Vec4, Vec3, VBase4#@UnresolvedImport
from direct.gui.DirectGui import DirectButton, DirectEntry, DirectLabel#@UnresolvedImport
from direct.gui.OnscreenText import OnscreenText#@UnresolvedImport
from direct.gui.OnscreenImage import OnscreenImage
from direct.filter.CommonFilters import CommonFilters#@UnresolvedImport
from panda3d.rocket import *


class MenuUI():
    
    def __init__(self, parent):
        self.parent = parent   
        
        LoadFontFace("ui/verdana.ttf")       #@UnresolvedImport 
        self.parent.rRegion.setActive(1)
        self.parent.rContext = self.parent.rRegion.getContext()
        
        #context.LoadDocument('assets/background.rml').Show()
        
        self.doc = self.parent.rContext.LoadDocument('ui/menu.rml')
        self.doc.Show()

        element = self.doc.GetElementById('newgame')
        element.AddEventListener('click', self.newgameButPressed, True)

    def newgameButPressed(self):
        self.parent.fsm.request('NewGame')

    def cleanup(self):
        self.parent.rRegion.setActive(0)
        self.parent.rContext.UnloadAllDocuments()
        self.parent = None

class PauseUI():
    
    def __init__(self, parent):
        self.parent = parent   
        
        LoadFontFace("ui/verdana.ttf")       #@UnresolvedImport 
        self.parent.rRegion.setActive(1)
        self.parent.rContext = self.parent.rRegion.getContext()
        
        #context.LoadDocument('assets/background.rml').Show()
        
        self.doc = self.parent.rContext.LoadDocument('ui/pause.rml')
        self.doc.Show()

        element = self.doc.GetElementById('resume')
        element.AddEventListener('click', self.resumeButPressed, True)
        element = self.doc.GetElementById('menu')
        element.AddEventListener('click', self.menuButRedPressed, True)

    def resumeButPressed(self):
        self.parent.fsm.request('ResumeGame')

    def menuButRedPressed(self):
        self.parent.fsm.request('Menu')
        
    def cleanup(self):
        self.parent.rRegion.setActive(0)
        self.parent.rContext.UnloadAllDocuments()
        self.parent = None
        
class GameUI():
    
    def __init__(self, parent):
        self.parent = parent   
        
        LoadFontFace("ui/verdana.ttf")       #@UnresolvedImport 
        self.parent.rRegion.setActive(1)
        self.parent.rContext = self.parent.rRegion.getContext()
        
        #context.LoadDocument('assets/background.rml').Show()
        
        self.doc = self.parent.rContext.LoadDocument('ui/gameui.rml')
        self.doc.Show()
        
        element = self.doc.GetElementById('status_bar')
        element.inner_rml = 'Game UI'
    
    def cleanup(self):
        self.parent.rRegion.setActive(0)
        self.parent.rContext.UnloadAllDocuments()
        self.parent = None
    
