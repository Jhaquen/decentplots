import numpy as np

class Indicator:

    currentConnectionNumber = 0
    startStopMap = {}
    levelHeightMap = {}
    vLineStartMap = {}

    def __init__(self,length,artists,datarange):
        # length represents the number of boxes, columns in array
        self.datarange = datarange
        self.grid = np.zeros((1,length))
        self.baseHeights = self.getBaseHeight(artists)
        self.calcHeightForLevel(0)
    
    def newConnections(self,connections):
         for connection in connections:
            self.newConnection(connection[0],connection[1])

    def newConnection(self,start,stop):
        # this checks if the space is avalible at the current height.
        # If not create new row
        # Also add the connection after check
        currentLevel = 0
        while any([pos for pos in self.grid[currentLevel][start:stop+1]]):
                currentLevel += 1
                if currentLevel == self.grid.shape[0]: self.addLevel(currentLevel)
        self.startStopMap[self.currentConnectionNumber] = {"start":start,"stop":stop, "level":currentLevel}
        self.addConnectionOnLevel(currentLevel,start,stop)
        self.currentConnectionNumber += 1
    
    def addConnectionOnLevel(self,height,start,stop):
        # this should block rows in self.grid according to passed positions
        for i in range(start,stop+1):
            self.grid[height][i] = self.currentConnectionNumber+1
    
    def addLevel(self,level):
        # this simply adds a new Row
        self.grid = np.vstack((self.grid, np.zeros((1,self.grid.shape[1]))))
        self.calcHeightForLevel(level)

    def calcHeightForLevel(self,level):
        # this should calculate the height of each level on the axes
        # The miniumum height for all connections on lvl 0 should be above all artist components
        if level==0: self.levelHeightMap[level] = np.max(self.baseHeights) + self.datarange/10
        else: self.levelHeightMap[level] = self.levelHeightMap[level-1] + self.datarange/10

    def getBaseHeight(self,artists):
        baseHeighs = []
        upperWhiskers = [whisker for i,whisker in enumerate(artists["whiskers"]) if i%2]
        for flier,whisker in zip(artists["fliers"],upperWhiskers):
            flierHeight = flier.get_path().get_extents().y1
            whiskerHeight = whisker.get_path().get_extents().y1
            baseHeighs.append(*[flierHeight if flierHeight != -np.inf else whiskerHeight])
        return baseHeighs

    def calcHeightForVlines(self):
        # this puts the startheights of each vertical line in a second grid
        # This is dependend on baseHeights and the height levels of the existing grid if a spot underneath is blocked
        startHeightMap_levels = {level:{} for level in self.startStopMap}
        startHeightMap = {level:{} for level in self.startStopMap}
        for connectionIndex, connection in self.startStopMap.items():
            for vLine in [connection["start"],connection["stop"]]:
                level = connection["level"]
                while level != 0:
                    if self.grid[level-1][vLine]:
                        break
                    level -= 1
                startHeightMap_levels[connectionIndex][vLine] = level
        for connectionIndex,connection in startHeightMap_levels.items():
            for vLineX,level in connection.items():
                if level == 0: 
                    startHeightMap[connectionIndex][vLineX] = self.baseHeights[vLineX] + self.datarange/20
                else:
                    startHeightMap[connectionIndex][vLineX] = self.levelHeightMap[level] - self.datarange/20
        return startHeightMap


    def drawConnections(self,ax,artists,color,lw):
        # this simply draws the connection
        vLineStartHeight = self.calcHeightForVlines()
        topWhiskers = [whisker for i,whisker in enumerate(artists["whiskers"]) if i%2==0]
        for connectionIndex, connection in self.startStopMap.items():
            startX = topWhiskers[connection["start"]].get_path().get_extents().x0
            endX = topWhiskers[connection["stop"]].get_path().get_extents().x0
            height = self.levelHeightMap[connection["level"]]
            ax.plot([startX,endX],[height,height],color=color,lw=lw)
            for boxIndex,conY in vLineStartHeight[connectionIndex].items():
                # Change how X-Pos is calculated
                boxXPos = topWhiskers[boxIndex].get_path().get_extents().x0
                ax.plot([boxXPos,boxXPos],[conY,height],color=color,lw=lw)
    
    def drawStars(self,data,ax,artist,color):
        pass