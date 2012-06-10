from panda3d.core import *#@UnresolvedImport
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
        inner_rml = ""
        for x in xrange(0, self.parent.game.player.bullets):
            inner_rml += '<div class="bullet"><div class="bullet_image"><img src="bullet.png" width="10px" height="29px"></img></div></div>'
        
        for x in xrange(self.parent.game.player.bullets, self.parent.game.player.max_bullets + 1):
            inner_rml += '<div class="bullet"></div>'
        
        element = self.doc.GetElementById('top_right_container')
        element.inner_rml = inner_rml
        
        element = self.doc.GetElementById('health_left')
        element.style.width = str(self.parent.game.player.health * 1.5) + 'px'
        
        self.doc.Show()
        
    def minusHealth(self):
        self.parent.game.player.health -= 1
        if self.parent.game.player.health < 0:
            self.parent.game.player.health = 0
        self.refreshHealth()
    
    def plusHealth(self):
        self.parent.game.player.health += 1
        if self.parent.game.player.health > self.parent.game.player.max_health:
            self.parent.game.player.health = self.parent.game.player.max_health
        self.refreshHealth()
        
    def minusBullets(self):
        self.parent.game.player.bullets -= 1
        if self.parent.game.player.bullets < 0:
            self.parent.game.player.bullets = 0
        self.refreshBullets()
    
    def plusBullets(self):
        self.parent.game.player.bullets += 1
        if self.parent.game.player.bullets > self.parent.game.player.max_bullets:
            self.parent.game.player.bullets = self.parent.game.player.max_bullets
        self.refreshBullets()
        
    def refreshHealth(self):
        element = self.doc.GetElementById('health_left')
        element.style.width = str(self.parent.game.player.health * 1.5) + 'px'
        
    def refreshBullets(self):
        inner_rml = ""
        for x in xrange(0, self.parent.game.player.bullets):
            inner_rml += '<div class="bullet"><div class="bullet_image"><img src="bullet.png" width="10px" height="29px"></img></div></div>'
        
        for x in xrange(self.parent.game.player.bullets, self.parent.game.player.max_bullets + 1):
            inner_rml += '<div class="bullet"></div>'
        
        element = self.doc.GetElementById('top_right_container')
        element.inner_rml = inner_rml
    
    def cleanup(self):
        self.parent.rRegion.setActive(0)
        self.parent.rContext.UnloadAllDocuments()
        self.parent = None
    
