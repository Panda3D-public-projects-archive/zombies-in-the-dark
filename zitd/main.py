from panda3d.core import *
from direct.showbase.ShowBase import ShowBase#@UnresolvedImport
from direct.showbase.DirectObject import DirectObject
from debug.debugoptions import DebugOptions
from debug.cameramanager import CameraManager
from player import Player
from utils import *
from level import Level
from monster import Monster
from panda3d.rocket import *
from gameui import *
from game import *
from direct.fsm import FSM#@UnresolvedImport
from direct.task.Task import Task

class App(DirectObject):
    def __init__(self):
        ShowBase()
        # Instancing fsm
        self.fsm = AppFSM(self, 'AppFSM')
        
        # Creating rocket region for ui
        self.rRegion = RocketRegion.make('zitd_ui', base.win)
        self.rContext = self.rRegion.getContext()
        ih = RocketInputHandler()
        base.mouseWatcher.attachNewNode(ih)
        self.rRegion.setInputHandler(ih)
        
        self.acceptOnce('escape', self.pause)
        
        self.fsm.request('Menu')
    
    def pause(self):
        self.fsm.request('Pause')
        
class AppFSM(FSM.FSM):
    def __init__(self, parent, name):
        FSM.FSM.__init__(self, name)
        self.parent = parent

        self.defaultTransitions = {
            'Menu'       : ['NewGame'],
            'NewGame'    : ['Pause'],
            'Pause'      : ['ResumeGame', 'Menu'],
            'ResumeGame' : ['Pause']
            }
    
    def enterMenu(self):
        base.win.setClearColor(VBase4(0, 0, 0, 0))
        # Instancing main menu UI
        self.parent.menuui = MenuUI(self.parent) 
        
    def exitMenu(self):
        self.parent.menuui.cleanup()
        
    def enterNewGame(self):
        self.parent.game = Game(self.parent)
        # Instancing game UI
        self.parent.gameui = GameUI(self.parent)
        self.accept('u', self.parent.gameui.minusHealth)
        self.accept('i', self.parent.gameui.plusHealth)
        self.accept('o', self.parent.gameui.minusBullets)
        self.accept('p', self.parent.gameui.plusBullets)
        
    def exitNewGame(self):
        self.parent.gameui.cleanup()
        self.ignore('u')
        self.ignore('i')
        self.ignore('o')
        self.ignore('p')

    def enterPause(self):
        self.parent.game.pause()
        # Instancing pause game UI
        self.parent.pauseui = PauseUI(self.parent)
        self.acceptOnce('escape', taskMgr.stop)
        
    def exitPause(self):
        self.acceptOnce('escape', self.parent.pause)
        self.parent.pauseui.cleanup()
        
    def enterResumeGame(self):
        self.parent.game.resume()
        # Instancing game UI
        self.parent.gameui = GameUI(self.parent)
        self.accept('u', self.parent.gameui.minusHealth)
        self.accept('i', self.parent.gameui.plusHealth)
        self.accept('o', self.parent.gameui.minusBullets)
        self.accept('p', self.parent.gameui.plusBullets)
        
    def exitResumeGame(self):
        self.parent.gameui.cleanup()
        self.ignore('u')
        self.ignore('i')
        self.ignore('o')
        self.ignore('p')

a = App()
run()