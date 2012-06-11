from panda3d.core import *
from utils import *

class Level():
    def __init__(self, parent):
        self.parent = parent
        self.node = render.attachNewNode('LevelNode')
        self.wall_node = self.node.attachNewNode('LevelWallNode')
        pnmi = PNMImage()
        pnmi.read(Filename('levels/eob1.png'))
        self.nav_graph = {}
        self.x_size = pnmi.getXSize()
        self.y_size = pnmi.getYSize()
        
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
                
                if ((pnmi.getRedVal(x,y) == 255 and pnmi.getBlueVal(x,y) == 255 and pnmi.getGreenVal(x,y) == 255) or
                    (pnmi.getRedVal(x,y) == 0 and pnmi.getBlueVal(x,y) == 255 and pnmi.getGreenVal(x,y) == 0) or
                    (pnmi.getRedVal(x,y) == 0 and pnmi.getBlueVal(x,y) == 0 and pnmi.getGreenVal(x,y) == 255)):
                    self.nav_graph[(x,pos_y)] = []
                    
                    
                    self.loadFloor(x, pos_y, 'TILE_FLOOR').reparentTo(self.floor_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    self.loadFloor(x, pos_y, 'TILE_CEIL').reparentTo(self.floor_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    
                    # neighbours
                    if x == 0:
                        self.loadWall(x, pos_y, 'TILE_EAST').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    if x == self.x_size-1:
                        self.loadWall(x, pos_y, 'TILE_WEST').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    if x > 0:
                        if pnmi.getRedVal(x-1,y) == 255 and pnmi.getBlueVal(x-1,y) == 0 and pnmi.getGreenVal(x-1,y) == 0:
                            self.loadWall(x, pos_y, 'TILE_EAST').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        else:
                            self.nav_graph[x, pos_y].append((x-1, pos_y))
                    if x < self.x_size-1:
                        if pnmi.getRedVal(x+1,y) == 255 and pnmi.getBlueVal(x+1,y) == 0 and pnmi.getGreenVal(x+1,y) == 0:
                            self.loadWall(x, pos_y, 'TILE_WEST').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        else:
                            self.nav_graph[x, pos_y].append((x+1, pos_y))
                    
                    
                    if y == 0:
                        self.loadWall(x, pos_y, 'TILE_SOUTH').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    if y == self.y_size-1:
                        self.loadWall(x, pos_y, 'TILE_NORTH').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                    if y > 0:
                        if pnmi.getRedVal(x,y-1) == 255 and pnmi.getBlueVal(x,y-1) == 0 and pnmi.getGreenVal(x,y-1) == 0:
                            self.loadWall(x, pos_y, 'TILE_SOUTH').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        else:
                            self.nav_graph[x, pos_y].append((x, pos_y+1))
                    if y < self.y_size-1:
                        if pnmi.getRedVal(x,y+1) == 255 and pnmi.getBlueVal(x,y+1) == 0 and pnmi.getGreenVal(x,y+1) == 0:
                            self.loadWall(x, pos_y, 'TILE_NORTH').reparentTo(self.wall_node_dict[(int(x/chunk_size), int(y/chunk_size))])
                        else:
                            self.nav_graph[x, pos_y].append((x, pos_y-1))
        
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
                        
    def loadTile(self, x, y, type):
        cm = CardMaker('cm')
        if type == 'TILE_CEIL' or type == 'TILE_FLOOR':
            cm.setFrame(-TILE_SIZE/2, TILE_SIZE/2, -TILE_SIZE/2, TILE_SIZE/2)
        else:
            cm.setFrame(-TILE_SIZE/2, TILE_SIZE/2, -TILE_SIZE*ASPECT/2, TILE_SIZE*ASPECT/2)
        cm_node = NodePath(cm.generate())
        cm_node.setTexture(loader.loadTexture('models/tex.png')) 
        if type == 'TILE_CEIL':
            cm_node.setPos(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE*ASPECT)
            cm_node.setP(90)
        elif type == 'TILE_FLOOR':
            cm_node.setPos(x*TILE_SIZE, y*TILE_SIZE, 0)
            cm_node.setP(-90)
        elif type == 'TILE_WEST':
            cm_node.setPos(x*TILE_SIZE+TILE_SIZE/2, y*TILE_SIZE, TILE_SIZE*ASPECT/2)
            cm_node.setH(-90)
        elif type == 'TILE_EAST':
            cm_node.setPos(x*TILE_SIZE-TILE_SIZE/2, y*TILE_SIZE, TILE_SIZE*ASPECT/2)
            cm_node.setH(90)
        elif type == 'TILE_NORTH':
            cm_node.setPos(x*TILE_SIZE, y*TILE_SIZE-TILE_SIZE/2, TILE_SIZE*ASPECT/2)
            cm_node.setH(180)
        elif type == 'TILE_SOUTH':
            cm_node.setPos(x*TILE_SIZE, y*TILE_SIZE+TILE_SIZE/2, TILE_SIZE*ASPECT/2)
        return cm_node
    
    def loadWall(self, x, y, type):
        model = loader.loadModel('models/wall')
        model.setTexture(loader.loadTexture('models/tex.png'))
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
        model.setTexture(loader.loadTexture('models/tex.png'))
        if type == 'TILE_CEIL':
            model.setPos(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE*ASPECT)
            model.setP(180)
        elif type == 'TILE_FLOOR':
            model.setPos(x*TILE_SIZE, y*TILE_SIZE, 0)
            #model.setP(-90)
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
