# this is neccecary to correctly draw statisticIndicators who reley on matplotlibs artist class

class coordinateMock():
    def __init__(self,maxheight,pos):
        self.y1 = maxheight
        self.x0 = pos

class pathMock():
    def __init__(self,maxheight,pos):
        self.maxheight = maxheight
        self.pos = pos
    def get_extents(self):
        cM = coordinateMock(self.maxheight,self.pos)
        return cM

class artistMock():
    def __init__(self,maxheight,pos):
        self.maxheight = maxheight
        self.pos = pos
    def get_path(self):
        pM = pathMock(self.maxheight,self.pos)
        return pM