from panda3d.core import *#@UnresolvedImport
from direct.gui.DirectGui import DirectButton, DirectEntry, DirectLabel#@UnresolvedImport
from direct.gui.OnscreenText import OnscreenText#@UnresolvedImport
from direct.gui.OnscreenImage import OnscreenImage
from direct.filter.CommonFilters import CommonFilters#@UnresolvedImport
from panda3d.rocket import *
import random

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
        
        
        
    def minusHealth(self, dh=1):
        self.parent.game.player.health -= dh
        if self.parent.game.player.health < 0:
            self.parent.game.player.health = 0
        self.refreshHealth()
    
    def plusHealth(self, dh=1):
        self.parent.game.player.health += dh
        if self.parent.game.player.health > self.parent.game.player.max_health:
            self.parent.game.player.health = self.parent.game.player.max_health
        self.refreshHealth()
        
    def minusBullets(self, db=1):
        self.parent.game.player.bullets -= db
        if self.parent.game.player.bullets < 0:
            self.parent.game.player.bullets = 0
        self.refreshBullets()
    
    def plusBullets(self, db=1):
        self.parent.game.player.bullets += db
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
    
class GameOverUI():
    
    def __init__(self, parent):
        self.parent = parent   
        
        LoadFontFace("ui/verdana.ttf")       #@UnresolvedImport 
        self.parent.rRegion.setActive(1)
        self.parent.rContext = self.parent.rRegion.getContext()
        
        self.parent.game.pause()
        
        self.gameover_list = []
        self.gameover_list.append('Brraaaains, brraaaaaaains!')
        self.gameover_list.append('The only thing missing is some fava beans and a nice chianti.')
        self.gameover_list.append('You died. The game is over.')
        
        #context.LoadDocument('assets/background.rml').Show()
        
        self.doc = self.parent.rContext.LoadDocument('ui/gameover.rml')
        self.doc.Show()

        random.seed()
        x = random.randint(0, len(self.gameover_list) - 1)
        element = self.doc.GetElementById('status_bar')
        element.inner_rml = self.gameover_list[x]
        
        element = self.doc.GetElementById('new')
        element.AddEventListener('click', self.newGameButPressed, True)

    def newGameButPressed(self):
        self.parent.fsm.request('NewGame')

    def cleanup(self):
        self.parent.rRegion.setActive(0)
        self.parent.rContext.UnloadAllDocuments()
        self.parent = None
        
class GameWinUI():
    
    def __init__(self, parent):
        self.parent = parent   
        
        self.parent.game.pause()
        LoadFontFace("ui/verdana.ttf")       #@UnresolvedImport 
        self.parent.rRegion.setActive(1)
        self.parent.rContext = self.parent.rRegion.getContext()
        
        self.doc = self.parent.rContext.LoadDocument('ui/gamewin.rml')
        self.doc.Show()

        element = self.doc.GetElementById('status_bar')
        element.inner_rml = 'Congratulations, you made it!'
        
        element = self.doc.GetElementById('new')
        element.AddEventListener('click', self.newGameButPressed, True)

    def newGameButPressed(self):
        self.parent.fsm.request('NewGame')

    def cleanup(self):
        self.parent.rRegion.setActive(0)
        self.parent.rContext.UnloadAllDocuments()
        self.parent = None