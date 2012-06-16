from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *

class SpotlightPanel():
    def __init__(self, parent, light):
        self.parent = parent
        self.light = light
        
        #label for sliders
        self.aLabel = OnscreenText(text = "FOW", pos = (0.3,-0.56), scale = 0.04, fg=(1,0,0,1),mayChange=1)
        self.bLabel = OnscreenText(text = "Near", pos = (0.3,-0.62), scale = 0.04, fg=(0,1.0,0,1), mayChange=1)
        self.cLabel = OnscreenText(text = "Far", pos = (0.3,-0.68), scale = 0.05, fg=(0,0,1,1), mayChange=1)
        self.dLabel = OnscreenText(text = "Exp", pos = (0.3,-0.76), scale = 0.05, fg=(0,0,1,1), mayChange=1)
        self.eLabel = OnscreenText(text = "AttX", pos = (0.3,-0.82), scale = 0.05, fg=(0,0,1,1), mayChange=1)
        self.fLabel = OnscreenText(text = "AttY", pos = (0.3,-0.88), scale = 0.05, fg=(0,0,1,1), mayChange=1)
        self.gLabel = OnscreenText(text = "AttZ", pos = (0.3,-0.94), scale = 0.05, fg=(0,0,1,1), mayChange=1)

        #set up sliders
        self.Aslider=DirectSlider(range=(0,100), value=self.light.getLens().getFov()[0], pageSize=0.01, command=self.setAF, scale = 0.25, pos=Point3(0.62, 0, -0.56))
        self.Bslider=DirectSlider(range=(0,200), value=self.light.getLens().getNear(), pageSize=0.01, command=self.setBF, scale = 0.25, pos=Point3(0.62, 0, -0.62))
        self.Cslider=DirectSlider(range=(0,200), value=self.light.getLens().getFar(), pageSize=0.01, command=self.setCF, scale = 0.25, pos=Point3(0.62, 0, -0.68))
        self.Dslider=DirectSlider(range=(0,100), value=self.light.getExponent(), pageSize=0.1, command=self.setDF, scale = 0.25, pos=Point3(0.62, 0, -0.76))
        self.Eslider=DirectSlider(range=(0,1), value=self.light.getAttenuation().getX(), pageSize=0.0001, command=self.setEF, scale = 0.25, pos=Point3(0.62, 0, -0.82))
        self.Fslider=DirectSlider(range=(0,1), value=self.light.getAttenuation().getY(), pageSize=0.0001, command=self.setFF, scale = 0.25, pos=Point3(0.62, 0, -0.88))
        self.Gslider=DirectSlider(range=(0,0.1), value=self.light.getAttenuation().getZ(), pageSize=0.0001, command=self.setGF, scale = 0.25, pos=Point3(0.62, 0, -0.94))

        #setup output box 
        self.ABCValuesLabel = DirectLabel(text = " ", pos = (-0.9, 0, -0.9), scale = 0.05, text_fg=(1,0.0,0.0,1))
        self.refreshSliders()   
    
    def refreshSliders(self):
        self.ABCValuesLabel ['text'] = "spotlight(fow,near,far)(%.2f, %.2f, %.2f %.2f (%.3f %.3f %.3f))" % \
                                        (self.light.getLens().getFov()[0], self.light.getLens().getNear(), self.light.getLens().getFar(), self.light.getExponent(), \
                                         self.light.getAttenuation().getX(), self.light.getAttenuation().getY(), self.light.getAttenuation().getZ())   
    
    def setAF(self):   
        self.light.getLens().setFov(self.Aslider['value'])
        self.refreshSliders() 
    def setBF(self):  
        self.light.getLens().setNear(self.Bslider['value'])
        self.refreshSliders() 
    def setCF(self):  
        self.light.getLens().setFar(self.Cslider['value'])
        self.refreshSliders()
    def setDF(self):  
        self.light.setExponent(self.Dslider['value'])
        self.refreshSliders()
    def setEF(self):  
        att = self.light.getAttenuation()
        self.light.setAttenuation(Point3(self.Eslider['value'], att.getY(), att.getZ()))
        self.refreshSliders()
    def setFF(self):  
        att = self.light.getAttenuation()
        self.light.setAttenuation(Point3(att.getX(), self.Fslider['value'], att.getZ()))
        self.refreshSliders()
    def setGF(self):  
        att = self.light.getAttenuation()
        self.light.setAttenuation(Point3(att.getX(), att.getY(), self.Gslider['value']))
        self.refreshSliders()