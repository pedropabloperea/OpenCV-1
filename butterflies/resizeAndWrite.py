import cv2
import sys
import numpy as np
import datetime

if __name__ == '__main__':

    
    if (len(sys.argv)==2):
        name_images = [sys.argv[1]]
    else:
        name_images = ['BMC-1903_D.jpg', 'BMC-1923_D.jpg', 'BMC-1943_D.jpg', 'BMC-1956_D.jpg', 'BMC-1966_D.jpg', 'BMC-1905_D.jpg', 'BMC-1925_D.jpg', 'BMC-1944_D.jpg', 'BMC-1957_D.jpg', 'BMC-1968_D.jpg', 'BMC-1926_D.jpg', 'BMC-1946_D.jpg', 'BMC-1958_D.jpg', 'BMC-1969_D.jpg', 'BMC-1907_D.jpg', 'BMC-1933_D.jpg', 'BMC-1948_D.jpg',  'BMC-1959_D.jpg', 'BMC-1970_D.jpg', 'BMC-1913_D.jpg', 'BMC-1951_D.jpg', 'BMC-1960_D.jpg', 'BMC-1971_D.jpg', 'BMC-1916_D.jpg', 'BMC-1936_D.jpg', 'BMC-1953_D.jpg', 'BMC-1963_D.jpg', 'BMC-1972_D.jpg', 'BMC-1918_D.jpg', 'BMC-1954_D.jpg', 'BMC-1964_D.jpg', 'BMC-1919_D.jpg', 'BMC-1942_D.jpg', 'BMC-1955_D.jpg', 'BMC-1965_D.jpg']
    

    images = []
    images_resize = []
    special = [] #images in which not found the color rectangle
    for img in name_images:
        if (len(name_images)!=1):
            name = 'butterflies/'+str(img)
        else:
            name = sys.argv[1]
        images = images + [cv2.imread(name)]
    
    for img in images:

        template = cv2.imread('qp.jpg')
        imgfound = cv2.matchTemplate(img, template, cv2.TM_SQDIFF_NORMED)
        minVal,maxVal,minLoc,maxLoc = cv2.minMaxLoc(imgfound)

        imgt = np.zeros(img.shape,np.uint8)+255
        imgt[minLoc[1]-40:img.shape[0],minLoc[0]-40:img.shape[1]] = img[minLoc[1]-40:img.shape[0],minLoc[0]-40:img.shape[1]]
        v, imgthres = cv2.threshold(imgt,86,256,cv2.THRESH_BINARY_INV)
        imgcanny = imgthres.copy()
        imgcanny = cv2.Canny(cv2.cvtColor(imgcanny,cv2.cv.CV_RGB2GRAY), 147,600)

        contours, hierarchy = cv2.findContours(imgcanny.copy(),cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = [cv2.approxPolyDP(contour, 1, True) for contour in contours];

        final_rect = [0,0,0,0]
        rectangles = []
        for contour in contours:
            minrect = cv2.boundingRect(contour)        
            area = minrect[2]*minrect[3]  
            if area < 100800-100 and minrect[2]>minrect[3]*2 and area>10000 and minrect[2]/minrect[3]>2 and minrect[2]/minrect[3]< 4 :
                rectangles = rectangles + [minrect]
                final_rect = minrect
        if (len(rectangles)>1):
            dist = 5
            
            for i in range(len(rectangles)):
                if (dist > abs(rectangles[i][2]/rectangles[i][3]-3.5)):
                    dist = abs(rectangles[i][2]/rectangles[i][3]-3.5)
                    final_rect = rectangles[i]       

        
        cv2.imshow('img',img)
        imgResize = img.copy()
        
        if final_rect != [0,0,0,0]:
            #102 y 349 es el valor medio de w y h, respectivamente, de todas las imagenes en las que detecta qp
            w =  img.shape[0]*(102)/final_rect[3]
            h = img.shape[1]*(349)/final_rect[2]
            imgResize = cv2.resize(img,(h,w), None, 1, 1, cv2.INTER_CUBIC)
            now = datetime.datetime.now()
            images_resize = images_resize + ['foto'+str(now.day)+str(now.month)+str(now.minute)+str(now.second)+'.jpg']
            #cv2.imwrite('butterflies_resize/foto'+str(now.day)+str(now.month)+str(now.minute)+str(now.second)+'.jpg',imgResize)
            cv2.imshow('resize',imgResize)
        else:
            special = special + [img]
            cv2.imshow('special images', img)
           # cv2.imwrite('butterflies_special/foto'+str(now.day)+str(now.month)+str(now.minute)+str(now.second)+'.jpg',img)
            
        
        k = cv2.waitKey(0)