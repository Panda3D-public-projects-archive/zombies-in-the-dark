from panda3d.core import *

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