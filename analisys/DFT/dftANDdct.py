# BASIC PROGRAM- shows images of:
#                        ORIGINAL -  original image  (stop.jpg)
#                         FOURIER -  the dft of the image
#                          COSINE -  the dct of the image
#                  FOURIER + INV. -  the image obtained after performing inverse
#                                     dft on the dft image
#                   COSINE + INV. -  the image obtained after performing inverse
#                                     dct on the dct image
# 
#   Press 'q' to quit
#

import cv2
import numpy as np


if __name__ == "__main__":

    bw = cv2.imread("../../img/stop.jpg",0)    #read image

    bwx = np.array(bw,dtype = float)           #convert the array to floats
    
    #APPLY DFT
    bwDFT = cv2.dft(bwx)
    aux  = cv2.dft(bwDFT,flags=cv2.DFT_INVERSE|cv2.DFT_SCALE)
    print aux
    resultF = np.array(aux, dtype = "uint8")
    print resultF
    print '******'
    #APPLY DCT
    bwDCT = cv2.dct(bwx)
    aux = cv2.dct(bwDCT,flags=cv2.DCT_INVERSE)
    resultC = np.array(aux, dtype = "uint8")
    
    cv2.imshow("ORIGINAL",bw)
    cv2.imshow("FOURIER",bwDFT)
    cv2.imshow("COSINE",bwDCT)

    cv2.imshow("FOURIER + INV.",resultF)
    cv2.imshow("COSINE + INV.",resultC)


    while True:
        
        k = cv2.waitKey(5)

        if (k == 113):    #quit on 'q'
            print "Quit"
            break
        
