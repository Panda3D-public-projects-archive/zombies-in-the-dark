from panda3d.core import *
from utils import *
import random

class Level():
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.node = render.attachNewNode('LevelNode')
        self.wall_node = self.node.attachNewNode('LevelWallNode')
        self.ghostwall_node = NodePath('GhostWallNode') # for collisions
        self.rf_light_node = self.node.attachNewNode('RedFlickeringLightNode')
        self.lights = []
        self.light_nodes = []
        pnmi = PNMImage()
        pnmi.read(Filename('levels/'+name+'.png'))
        self.nav_graph = {}
        self.x_size = pnmi.getXSize()
        self.y_size = pnmi.getYSize()

        self.ai_list = []
        
        self.finish_tile = (0,0)
        
        self.tex_ext = '.png'
        self.tex_offset = 0
        
        # Load textures
        self.ts_normal = TextureStage('wall_normal')
        self.ts_normal.setMode(TextureStage.MNormal)
        self.ts_gloss = TextureStage('wall_gloss')
        self.ts_gloss.setMode(TextureStage.MGloss)  
        self.ts_glow = TextureStage('wall_glow')
        self.ts_glow.setMode(TextureStage.MGlow)   
        self.ts_add = TextureStage('add')
        self.ts_add.setMode(TextureStage.MDecal) 
        self.ts_model_exit = TextureStage('exit_model')          
        
        self.texa = loader.loadTexture('models/pk02_wall02a_C'+self.tex_ext)
        self.texa_normal = loader.loadTexture('models/pk02_wall02a_N'+self.tex_ext)
        self.texa_gloss = loader.loadTexture('models/pk02_wall02a_S1'+self.tex_ext)
        self.texa_glow = loader.loadTexture('models/pk02_wall02a_I1'+self.tex_ext)
        
        self.texb = loader.loadTexture('models/pk02_wall02b_C'+self.tex_ext)
        self.texb_normal = loader.loadTexture('models/pk02_wall02b_N'+self.tex_ext)
        self.texb_gloss = loader.loadTexture('models/pk02_wall02b_S1'+self.tex_ext)
        self.texb_glow = loader.loadTexture('models/pk02_wall02b_I1'+self.tex_ext)   
        
        self.texc = loader.loadTexture('models/pk02_wall02c_C'+self.tex_ext)
        self.texc_normal = loader.loadTexture('models/pk02_wall02c_N'+self.tex_ext)
        self.texc_gloss = loader.loadTexture('models/pk02_wall02c_S1'+self.tex_ext)
        self.texc_glow = loader.loadTexture('models/pk02_wall02c_I1'+self.tex_ext) 
        
        self.tex_ceil = loader.loadTexture('models/pk02_ceiling03_C'+self.tex_ext)
        self.tex_ceil_normal = loader.loadTexture('models/pk02_ceiling03_N'+self.tex_ext)
        self.tex_ceil_gloss = loader.loadTexture('models/pk02_ceiling03_S1'+self.tex_ext)        
        
        self.tex_floor = loader.loadTexture('models/pk02_floor01_C'+self.tex_ext)
        self.tex_floor_normal = loader.loadTexture('models/pk02_floor01_N'+self.tex_ext)
        self.tex_floor_gloss = loader.loadTexture('models/pk02_floor01_S1'+self.tex_ext)  
        
        self.tex_floor_exit = loader.loadTexture('models/exit'+self.tex_ext)
        self.tex_floor_exit_glow = loader.loadTexture('models/exit_I'+self.tex_ext) 
        
        self.tex_model_exit = loader.loadTexture('models/exit_model.png') 
        self.tex_model_exit_glow = loader.loadTexture('models/exit_model_I.png')                
        
        self.texa.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texa.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texa_normal.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texa_normal.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texa_gloss.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texa_gloss.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texa_glow.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texa_glow.setMinfilter(Texture.FTLinearMipmapLinear)      
        
        self.texb.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texb.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texb_normal.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texb_normal.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texb_gloss.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texb_gloss.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texb_glow.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texb_glow.setMinfilter(Texture.FTLinearMipmapLinear)  

        self.texc.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texc.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texc_normal.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texc_normal.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texc_gloss.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texc_gloss.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texc_glow.setMagfilter(Texture.FTLinearMipmapLinear)
        self.texc_glow.setMinfilter(Texture.FTLinearMipmapLinear)  

        self.tex_ceil.setMagfilter(Texture.FTLinearMipmapLinear)
        self.tex_ceil.setMinfilter(Texture.FTLinearMipmapLinear)
        self.tex_ceil_normal.setMagfilter(Texture.FTLinearMipmapLinear)
        self.tex_ceil_normal.setMinfilter(Texture.FTLinearMipmapLinear)
        self.tex_ceil_gloss.setMagfilter(Texture.FTLinearMipmapLinear)
        self.tex_ceil_gloss.setMinfilter(Texture.FTLinearMipmapLinear)
        
        self.tex_floor.setMagfilter(Texture.FTLinearMipmapLinear)
        self.tex_floor.setMinfilter(Texture.FTLinearMipmapLinear)
        self.tex_floor_normal.setMagfilter(Texture.FTLinearMipmapLinear)
        self.tex_floor_normal.setMinfilter(Texture.FTLinearMipmapLinear)
        self.tex_floor_gloss.setMagfilter(Texture.FTLinearMipmapLinear)
        self.tex_floor_gloss.setMinfilter(Texture.FTLinearMipmapLinear)        
        
        # Create dict for parenting geometry
        self.floor_node_dict = {}
        self.wall_node_dict = {}
        chunk_size = 5
        
        chunk_num_x = int((self.x_size-1) / chunk_size) + 1
        chunk_num_y = int((self.y_size-1) / chunk_size) + 1
        
        for i in xrange(chunk_num_x):
            for j in xrange(chunk_num_y):
                self.floor_node_dict[(i,j)] = self.node.attachNewNode('Node_'+str(i)+'_'+str(j))
                self.wall_node_dict[(i,j)] = self.wall_node.attachNewNode('WallNode_'+str(i)+'_'+str(j))
        
        self.start_pos = (0,0)
        for x in xrange(self.x_size):
            for y in xrange(self.y_size):
                #print x,y,pnmi.getRedVal(x,y), pnmi.getGreenVal(x,y),pnmi.getBlueVal(x,y)
                pos_y = self.y_size-y-1
                if pnmi.getRedVal(x,y) == 0 and pnmi.getBlueVal(x,y) == 255 and pnmi.getGreenVal(x,y) == 0:
                    self.start_pos = (x, pos_y)
                
                if pnmi.getRedVal(x,y) == 128 and pnmi.getBlueVal(x,y) == 128 and pnmi.getGreenVal(x,y) == 128:
                    self.loadLight(x, pos_y, 'RED_FLICKERING')
                
                if (
                    (pnmi.getRedVal(x,y) == 255 and pnmi.getBlueVal(x,y) == 255 and pnmi.getGreenVal(x,y) == 255) or
                    (pnmi.getRedVal(x,y) == 0 and pnmi.getBlueVal(x,y) == 255 and pnmi.getGreenVal(x,y) == 0) or
                    (pnmi.getRedVal(x,y) == 0 and pnmi.getBlueVal(x,y) == 0 and pnmi.getGreenVal(x,y) == 255) or
                    (pnmi.getRedVal(x,y) == 128 and pnmi.getBlueVal(x,y) == 128 and pnmi.getGreenVal(x,y) == 128) or
                    (pnmi.getRedVal(x,y) == 255 and pnmi.getBlueVal(x,y) == 0 and pnmi.getGreenVal(x,y) == 216)
                    ):
                    self.nav_graph[(x,pos_y)] = []
                    
                    if (pnmi.getRedVal(x,y) == 255 and pnmi.getBlueVal(x,y) == 0 and pnmi.getGreenVal(x,y) == 216):
                        self.loadFloor(x, pos_y, 'TILE_EXIT').reparentTo(self.floor_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        self.finish_tile = (x, pos_y)
                        self.exit_model = self.loadExitModel(x, pos_y)
                        self.exit_model.reparentTo(self.node)
                    else:
                        self.loadFloor(x, pos_y, 'TILE_FLOOR').reparentTo(self.floor_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    self.loadFloor(x, pos_y, 'TILE_CEIL').reparentTo(self.floor_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    
                    # neighbours
                    if x == 0:
                        wall = self.loadWall(x, pos_y, 'TILE_EAST')
                        wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        wall.instanceTo(self.ghostwall_node)
                    if x == self.x_size-1:
                        wall = self.loadWall(x, pos_y, 'TILE_WEST')
                        wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        wall.instanceTo(self.ghostwall_node)
                    if x > 0:
                        if pnmi.getRedVal(x-1,y) == 255 and pnmi.getBlueVal(x-1,y) == 0 and pnmi.getGreenVal(x-1,y) == 0:
                            wall = self.loadWall(x, pos_y, 'TILE_EAST')
                            wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                            wall.instanceTo(self.ghostwall_node)
                        else:
                            self.nav_graph[x, pos_y].append((x-1, pos_y))
                    if x < self.x_size-1:
                        if pnmi.getRedVal(x+1,y) == 255 and pnmi.getBlueVal(x+1,y) == 0 and pnmi.getGreenVal(x+1,y) == 0:
                            wall = self.loadWall(x, pos_y, 'TILE_WEST')
                            wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                            wall.instanceTo(self.ghostwall_node)
                        else:
                            self.nav_graph[x, pos_y].append((x+1, pos_y))
                    
                    
                    if y == 0:
                        wall = self.loadWall(x, pos_y, 'TILE_SOUTH')
                        wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        wall.instanceTo(self.ghostwall_node)
                    if y == self.y_size-1:
                        wall = self.loadWall(x, pos_y, 'TILE_NORTH')
                        wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        wall.instanceTo(self.ghostwall_node)
                    if y > 0:
                        if pnmi.getRedVal(x,y-1) == 255 and pnmi.getBlueVal(x,y-1) == 0 and pnmi.getGreenVal(x,y-1) == 0:
                            wall = self.loadWall(x, pos_y, 'TILE_SOUTH')
                            wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                            wall.instanceTo(self.ghostwall_node)
                        else:
                            self.nav_graph[x, pos_y].append((x, pos_y+1))
                    if y < self.y_size-1:
                        if pnmi.getRedVal(x,y+1) == 255 and pnmi.getBlueVal(x,y+1) == 0 and pnmi.getGreenVal(x,y+1) == 0:
                            wall = self.loadWall(x, pos_y, 'TILE_NORTH')
                            wall.reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                            wall.instanceTo(self.ghostwall_node)
                        else:
                            self.nav_graph[x, pos_y].append((x, pos_y-1))
        
                    if (pnmi.getRedVal(x,y) == 0 and pnmi.getBlueVal(x,y) == 0 and pnmi.getGreenVal(x,y) == 255):
                        self.ai_list.append((x,pos_y))
                        
                    #if x==1 and y==22:
                    #    print pnmi.getRedVal(x,y), pnmi.getBlueVal(x,y), pnmi.getGreenVal(x,y)
        
        # doors
        """
        for x in xrange(self.x_size):
            for y in xrange(self.y_size):       
                pos_y = self.y_size-y-1             
                if pnmi.getRedVal(x,y) == 0 and pnmi.getBlueVal(x,y) == 0 and pnmi.getGreenVal(x,y) == 255:
                    if pnmi.getRedVal(x-1,y) == 255 and pnmi.getBlueVal(x-1,y) == 255 and pnmi.getGreenVal(x-1,y) == 255:
                        # verical wall
                        self.loadDoor(x, pos_y, 'VERTICAL').reparentTo(self.node)
                        self.nav_graph[x, pos_y] = []
                        self.nav_graph[x-1, pos_y].remove((x, pos_y))
                        self.nav_graph[x+1, pos_y].remove((x, pos_y))
                    elif pnmi.getRedVal(x,y-1) == 255 and pnmi.getBlueVal(x,y-1) == 255 and pnmi.getGreenVal(x,y-1) == 255:
                        self.loadDoor(x, pos_y, 'HORIZONTAL').reparentTo(self.node)
                        self.nav_graph[x, pos_y] = []
                        self.nav_graph[x, pos_y-1].remove((x, pos_y))
                        self.nav_graph[x, pos_y+1].remove((x, pos_y)) 
        """
        for i in xrange(chunk_num_x):
            for j in xrange(chunk_num_y):
                self.floor_node_dict[(i,j)].clearModelNodes()
                self.floor_node_dict[(i,j)].flattenStrong()
                self.wall_node_dict[(i,j)].clearModelNodes()
                self.wall_node_dict[(i,j)].flattenStrong()
                
        self.light_task_timer = 0
        self.light_task_state = True
        self.light_task_time = random.randint(1, 2)
        taskMgr.add(self.levelTask, 'LevelTask')
    
            
    def loadWall(self, x, y, type):
        model = loader.loadModel('models/wall')
        num = random.randint(0, 10)
        if num < 5:
            model.setTexture(self.texa)
            model.setTexture(self.ts_normal, self.texa_normal)
            model.setTexture(self.ts_gloss, self.texa_gloss)
            model.setTexture(self.ts_glow, self.texa_glow)
        elif num >= 5 and num < 9:
            model.setTexture(self.texb)
            model.setTexture(self.ts_normal, self.texb_normal)
            model.setTexture(self.ts_gloss, self.texb_gloss)
            model.setTexture(self.ts_glow, self.texb_glow)  
        else:
            model.setTexture(self.texc)
            model.setTexture(self.ts_normal, self.texc_normal)
            model.setTexture(self.ts_gloss, self.texc_gloss)
            model.setTexture(self.ts_glow, self.texc_glow)          
        if type == 'TILE_WEST':
            model.setPos(x*TILE_SIZE+TILE_SIZE/2, y*TILE_SIZE, TILE_SIZE*ASPECT/2)
            model.setP(90)
            model.setH(-90)
        elif type == 'TILE_EAST':
            model.setPos(x*TILE_SIZE-TILE_SIZE/2, y*TILE_SIZE, TILE_SIZE*ASPECT/2)
            model.setP(90)
            model.setH(90)          
        elif type == 'TILE_NORTH':
            model.setPos(x*TILE_SIZE, y*TILE_SIZE-TILE_SIZE/2, TILE_SIZE*ASPECT/2)
            model.setP(90)
            model.setH(180)             
        elif type == 'TILE_SOUTH':
            model.setPos(x*TILE_SIZE, y*TILE_SIZE+TILE_SIZE/2, TILE_SIZE*ASPECT/2)
            model.setP(90)            
        return model        
    
    def loadFloor(self, x, y, type):
        model = loader.loadModel('models/floor')
        if type == 'TILE_CEIL':
            model.setPos(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE*ASPECT)
            model.setP(180)
            model.setTexture(self.tex_ceil)
            model.setTexture(self.ts_normal, self.tex_ceil_normal)
            model.setTexture(self.ts_gloss, self.tex_ceil_gloss)     
        elif type == 'TILE_FLOOR':
            model.setPos(x*TILE_SIZE, y*TILE_SIZE, 0)
            model.setTexture(self.tex_floor)
            model.setTexture(self.ts_normal, self.tex_floor_normal)
            model.setTexture(self.ts_gloss, self.tex_floor_gloss)  
        elif type == 'TILE_EXIT':
            model.setPos(x*TILE_SIZE, y*TILE_SIZE, 0)
            model.setTexture(self.tex_floor)
            model.setTexture(self.ts_add, self.tex_floor_exit)
            model.setTexture(self.ts_glow, self.tex_floor_exit_glow)
        return model
    
    def loadExitModel(self, x, y):
        model = loader.loadModel('models/exit')
        model.setScale(TILE_SIZE, TILE_SIZE, TILE_SIZE*ASPECT)
        model.setPos(x*TILE_SIZE - TILE_SIZE/2, y*TILE_SIZE - TILE_SIZE/2, 0)
        model.setTransparency(TransparencyAttrib.MAlpha)
        model.setTexture(self.ts_model_exit, self.tex_model_exit)
        model.setTexture(self.ts_glow, self.tex_model_exit_glow)
        return model       
    
    def loadDoor(self, x, y, type):
        node = loader.loadModel('models/door')
        node.setScale(TILE_SIZE, 10, TILE_SIZE*ASPECT)
        node.setColor(1,0,0)
        if type == 'HORIZONTAL':
            node.setPos(x*TILE_SIZE - TILE_SIZE/2, y*TILE_SIZE, 0)
        elif type == 'VERTICAL':
            node.setPos(x*TILE_SIZE, y*TILE_SIZE - TILE_SIZE/2, 0)
            node.setH(90)
        return node
    
    def loadLight(self, x, y, type):
        if type == 'RED_FLICKERING':
            plight = PointLight('plight')
            plight.setColor(VBase4(0.7, 0.2, 0.2, 1))
            plight.setAttenuation(Point3(0, 0, 0.04))            
            plnp = self.rf_light_node.attachNewNode(plight)
            plnp.setPos(x*TILE_SIZE - TILE_SIZE/2, y*TILE_SIZE, 5)
            render.setLight(plnp)
            self.lights.append(plight)
            self.light_nodes.append(plnp)
            
    def levelTask(self, task):
        if self.parent.parent.fsm.state == 'Pause':
            return task.cont
        self.light_task_timer = self.light_task_timer + globalClock.getDt()
        if self.light_task_timer > self.light_task_time:
            if self.light_task_state:
                for l in self.lights:
                    l.setAttenuation(Point3(1,1,1))
                self.light_task_state = False
                self.light_task_timer = 0
                self.light_task_time = random.uniform(0.5, 1.5)                
            else:
                for l in self.lights:
                    l.setAttenuation(Point3(0, 0, 0.04))
                self.light_task_state = True
                self.light_task_timer = 0
                self.light_task_time = random.randint(1, 4)
        
        # Exit cube texture
        self.tex_offset += globalClock.getDt() * 0.5
        self.exit_model.setTexOffset(self.ts_model_exit, 0, self.tex_offset)
        return task.cont

    def getAiList(self):
        return self.ai_list
    
    def getFloorTiles(self):
        return self.nav_graph.keys()
        
    def getMaxX(self):
        return self.x_size
    
    def getMaxY(self):
        return self.y_size
    
    def destroy(self):
        taskMgr.remove('LevelTask')
        self.node.removeNode()
    
    """
    def __del__(self):
        print "Level deleted!"
    """
    