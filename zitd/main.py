from panda3d.core import *
from direct.showbase.ShowBase import ShowBase#@UnresolvedImport
from direct.showbase.DirectObject import DirectObject
from debug.debugoptions import DebugOptions
from debug.cameramanager import CameraManager
from utils import *
from panda3d.rocket import *
from gameui import *
from game import *
from direct.fsm import FSM#@UnresolvedImport
from direct.task.Task import Task

class App(DirectObject):
    def __init__(self):
        ShowBase()
        
        props = WindowProperties()
        props.setTitle( 'ZombiesInTheDark' )
        base.win.requestProperties( props )
        
        # use fmod for sound
        loadPrcFileData('', 'audio-library-name p3fmod_audio')
        
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
        
    def resume(self):
        self.fsm.request('ResumeGame')
        
    def gameOver(self):
        self.fsm.request('GameOver')                
        
class AppFSM(FSM.FSM):
    def __init__(self, parent, name):
        FSM.FSM.__init__(self, name)
        self.parent = parent

        self.defaultTransitions = {
            'Menu'       : ['NewGame'],
            'NewGame'    : ['Pause', 'GameOver', 'GameWin'],
            'Pause'      : ['ResumeGame', 'Menu'],
            'ResumeGame' : ['Pause', 'GameOver', 'GameWin'],
            'GameOver'   : ['NewGame'],
            'GameWin'    : ['NewGame']
            }
    
    def enterMenu(self):
        base.win.setClearColor(VBase4(0, 0, 0, 0))
        # Instancing main menu UI
        try:
            self.parent.game.player.heart_sound.stop()
            self.parent.game.player.heart_sound.pause()
        except:
            pass
         
        self.parent.menuui = MenuUI(self.parent)

        
    def exitMenu(self):
        self.parent.menuui.cleanup()
        
    def enterNewGame(self):
        try:
            for z in self.parent.game.zombies[:]:
                z.destroy()            
                self.parent.game.zombies.remove(z)
            self.parent.game.level.destroy()
            self.parent.game.level = None
            self.parent.game.player.cleanup()
            self.parent.game.player = None
            self.parent.game.collision_manager.cleanup()
            self.parent.game.collision_manager = None
            self.parent.game.cleanup()
            self.parent.game = None
            render.setShaderOff()
        except:
            pass
        self.parent.game = Game(self.parent)
        # Instancing game UI
        self.parent.gameui = GameUI(self.parent)
        """
        self.accept('u', self.parent.gameui.minusHealth)
        self.accept('i', self.parent.gameui.plusHealth)
        self.accept('o', self.parent.gameui.minusBullets)
        self.accept('p', self.parent.gameui.plusBullets)
        """
        
    def exitNewGame(self):
        self.parent.gameui.cleanup()
        """
        self.ignore('u')
        self.ignore('i')
        self.ignore('o')
        self.ignore('p')
        """

    def enterPause(self):
        self.parent.game.pause()
        # Instancing pause game UI
        self.parent.pauseui = PauseUI(self.parent)
        self.acceptOnce('escape', self.parent.resume)
        
    def exitPause(self):
        self.acceptOnce('escape', self.parent.pause)
        self.parent.pauseui.cleanup()
        
    def enterResumeGame(self):
        self.parent.game.resume()
        # Instancing game UI
        self.parent.gameui = GameUI(self.parent)
        
    def exitResumeGame(self):
        self.parent.gameui.cleanup()
        
    def enterGameOver(self):
        self.parent.gameoverui = GameOverUI(self.parent)
        self.ignore('escape')
    
    def exitGameOver(self):
        self.acceptOnce('escape', self.parent.pause)
        self.parent.gameoverui.cleanup()
        
    def enterGameWin(self):
        self.parent.gamewinui = GameWinUI(self.parent)
        self.ignore('escape')
    
    def exitGameWin(self):
        self.acceptOnce('escape', self.parent.pause)
        self.parent.gamewinui.cleanup()
    
a = App()
run()