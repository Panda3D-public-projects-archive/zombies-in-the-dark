from panda3d.core import *
import random


TILE_SIZE = 10.
ASPECT = 0.8
HEADSHOT_DAMAGE = 50
BODYSHOT_DAMAGE = 30

# Code by preusser from Panda3D forums
# Link: http://www.panda3d.org/forums/viewtopic.php?t=11268
def loadImageAsPlane(filepath, yresolution = 600):
    """
    Load image as 3d plane
   
    Arguments:
    filepath -- image file path
    yresolution -- pixel-perfect width resolution
    """
   
    tex = loader.loadTexture(filepath)
    tex.setBorderColor(Vec4(0,0,0,0))
    tex.setWrapU(Texture.WMBorderColor)
    tex.setWrapV(Texture.WMBorderColor)
    cm = CardMaker(filepath + ' card')
    cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
    card = NodePath(cm.generate())
    card.setTexture(tex)
    card.setScale(card.getScale()/ yresolution)
    card.flattenLight() # apply scale
    return card 


def percent( num ):
    rnd = random.randint(1,100)
    if rnd <= num:
        return 1
    else:
        return 0

def d( num ):
    return random.randint(1,num)

def getTile( pos ):
    return ( int(pos[0]/TILE_SIZE), int(pos[1]/TILE_SIZE) )
    
    
    