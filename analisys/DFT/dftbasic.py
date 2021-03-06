# USAGE:     python dftbasic.py (img path)
#
# Shows various images:
#            ORIGINAL  -  original image (BW) (given trough command terminal)
#            DFT -> DFT_INV  -  result of applying th dft and afterwards the
#                                inverse dft.
#            DCT -> DCT_INV  -  result of applying th dct and afterwards the
#                                inverse dct.
#      Press 'q' to quit


import cv2
import cv2.cv as cv
import numpy as np
import sys

if __name__ == "__main__":

    bw = cv2.imread(sys.argv[1],0)             #read image

    bwx = np.array(bw,dtype = float)           #convert the array to floats

    bwDFT = cv2.dft(bwx)                       #APPLY DFT and DCT
    bwDCT = cv2.dct(bwx)

    auxF = cv2.dft(bwDFT,flags = cv.CV_DXT_INV_SCALE)
    auxC = cv2.dct(bwDCT,flags = cv.CV_DXT_INV_SCALE)

    resultF = np.array(auxF, dtype = "uint8")
    resultC = np.array(auxC, dtype = "uint8")

    cv2.imshow("ORIGINAL",bw)
    #cv2.imshow("FOURIER",bwDFT)
    #cv2.imshow("COSINE",bwDCT)

    cv2.imshow("DFT -> DFT_INV",resultF)
    cv2.imshow("DCT -> DCT_INV",resultC)


    while True:
        
        k = cv2.waitKey(5)

        if (k == 113):    #quit on 'q'
            print "Quit"
            break
        
