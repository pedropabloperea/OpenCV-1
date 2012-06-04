import cv2
import numpy as np



def getSqHistogram(contours,dimension,sqNum):
	#compute the width and height of a square
	lh = dimension[0]/sqNum[0]
	lw = dimension[1]/sqNum[1]
	
	#print "lw "+str(lw)+" dimension[0] "+str(dimension[1])+" sqNum "+str(sqNum[1])
	#print "lh "+str(lh)+" dimension[1] "+str(dimension[0])+" sqNum "+str(sqNum[0])

	sqHist = np.zeros(sqNum,np.uint8) #create an appropiate histogram (2D)
	for cont in contours:	#for every contour, we update the histogram
		#print "new contour"
		center,r = cv2.minEnclosingCircle(cont) #take the minimal enclosing circle for the contour
		x,y = int(center[0]),int(center[1])
		r = int(r)
		
		#print "center "+str((x,y))+" radius "+str(r)

		xSq = min(x/lw,sqNum[1]-1)
		ySq = min(y/lh,sqNum[0]-1)


		#compute cardinal points for the center with distance r
		northSq = max((y-r)/lh,0)
		southSq = min((y+r)/lh,sqNum[0])
		
		westSq = max((x-r)/lw,0)
		eastSq = min((x+r)/lw,sqNum[1])
		

		#print "center row at "+str(ySq)+" up to "+str(northSq)+" down to "+str(southSq)
		#print "center col at "+str(xSq)+" left to "+str(westSq)+" right to "+str(eastSq)
		
		if northSq != southSq:
			for i in range(northSq,min(southSq+1,sqNum[0])):
				if eastSq != westSq:
					for j in range(westSq,min(eastSq+1,sqNum[1])):
						sqHist[i][j]+=1
				else:
					sqHist[i][xSq]+=1
		else:
			if eastSq != westSq:
				for j in range(westSq,min(eastSq+1,sqNum[1])):
					sqHist[ySq][j]+=1
			else:
				sqHist[ySq][xSq]+=1

	return sqHist


def paintSqHistogram(sqHist,imgShape,gradual):
	totalH,totalW = imgShape[0],imgShape[1]
	rowNum,colNum = sqHist.shape[:2]
	lh,lw = totalH/rowNum,totalW/colNum

	canvas = np.zeros((totalH,totalW),np.uint8)
	
	#paint the result
	for row in range(rowNum):
		for col in range(colNum):
			if sqHist[row][col]!=0:
				if gradual:
					plane = np.ones((lh,lw),np.uint8)*(120+20*sqHist[row][col])
				else:
					plane = np.ones((lh,lw),np.uint8)*255
				canvas[row*lh:(row+1)*lh,col*lw:(col+1)*lw]=plane	
	
	return canvas


def getPoints(dimension,sqHist):
	retPoints = []

	rowNum,colNum = sigSquares.shape[:2]
	lw = dimension[1]/colNum
	lh = dimension[0]/rowNum

	for row in range(rowNum):
		for col in range(colNum):
			if sigSquares[row][col]!=0:
				x,y = col*lw,row*lh
				aux = []
				for i in range(3):
					for j in range(3):
						aux.append((x+(lw/2)*i,y+(lh/2)*j))
				retPoints.append(aux)
	return retPoints


def significantSQS(bigCont,imgShape,histDim):
	sqHist = getSqHistogram(bigCont,(imgShape[0],imgShape[1]),histDim)
	removeNotConnected(sqHist)
	#aux = paintSqHistogram(sqHist,imgShape,False)
	return sqHist


def getSigSquares(contList,imgShape,histDim,thresh):
	sumSq = np.zeros(histDim,np.uint8)
	for contours in contList:
		sqHist = significantSQS(contours,imgShape,histDim)
		np.clip(sqHist,0,1,sqHist)
		sumSq = sumSq+sqHist

	sumSq = cv2.threshold(sumSq,thresh,200,cv2.cv.CV_THRESH_BINARY)[1]
	removeNotConnected(sumSq)
	return paintSqHistogram(sumSq,imgShape,False),sumSq


def removeNotConnected(sqHist):
	for row in range(sqHist.shape[0]-1):
		for col in range(sqHist.shape[1]-1):
			if (sqHist[row,col]!=0) and (not isConnected(row,col,sqHist)):
				sqHist[row,col]=0


def isConnected(row,col,matrix):
	leftB = max(0,col-1)
	rightB = min(col+1,matrix.shape[1]-1)
	upB = max(0,row-1)
	downB = min(row+1,matrix.shape[0]-1)
	for i in range(upB,downB+1,1):
		for j in range(leftB,rightB+1,1):
			if (i!=row or j!=col) and (matrix[i,j]!=0):
				return True
	return False





#quitar todos los parametros y pasarle directamente bigCont y punto
# def refineSqHistogram (sqHist,bigCont,imgShape):
# 	lh,lw=imgShape[0]/sqHist.shape[0],imgShape[1]/sqHist.shape[1]
	
# 	mask = np.zeros((imgShape),np.uint8)
	
# 	refSquares = np.zeros((sqHist.shape[0]**2,sqHist.shape[1]**2),np.uint8)
	
# 	for row in range(sqHist.shape[0]-1):
# 		for col in range(sqHist.shape[1]-1):
# 			#if the square value is greater than 0 (i.e there is a contour in this tile)
# 			#then we get the sqHist of this particular tile
# 			if sqHist[row,col]!=0:
# 				getSqHistogram(bigCont,dimension,sqNum)
# 				refSquares[row*refDim[1]:(row+1)*refDim[1],col*refDim[0]:(col+1)*refDim[0]]=patchSquares
# 	return refSquares
#removeNotConnected(refSquares)


# def isContained(pt,contours):
# 	for cont in contours:
# 		if cv2.pointPolygonTest(cont, pt, False)>=0:
# 			return True
# 	return False


# def getComponent(row,col,sigSquares,neig,diagonalNeig):
# 	if row>=0 and row<sigSquares.shape[0] and col>=0 and col<sigSquares.shape[1] and sigSquares[row][col]<0 and (row,col) not in neig:
# 		neig.add((row,col))
# 		getComponent(row-1,col,sigSquares,neig,diagonalNeig)
# 		getComponent(row+1,col,sigSquares,neig,diagonalNeig)
# 		getComponent(row,col-1,sigSquares,neig,diagonalNeig)
# 		getComponent(row,col+1,sigSquares,neig,diagonalNeig)
# 		#print neig


# def labelConectComp(sigSquares):
# 	#print sigSquares
# 	sigSquares= sigSquares*(-1)
# 	#print sigSquares
# 	label = 0
# 	for row in range(sigSquares.shape[0]-1):
# 		for col in range(sigSquares.shape[1]-1):
# 			if sigSquares[row][col]<0:
# 				label+=1
# 				aux = set()
# 				getComponent(row,col,sigSquares,aux,False)
# 				for tile in aux:
# 					sigSquares[tile[0]][tile[1]]=label
# 	#print sigSquares


if __name__ == "__main__":

	print 'only methods'






























