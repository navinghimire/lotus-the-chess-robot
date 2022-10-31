import numpy as np
import cv2 as cv
import glob
import time
import imutils
import yaml
from heapq import heappop, heappush
import cv2.aruco as aruco
from skimage import measure
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import os
import chess
import voice
def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err
 
def compare_images(imageA, imageB, board,grid = True):
    if grid:
        cellsize = 480//8
        offset = 10

        # compute the mean squared error and structural similarity
        # index for the images
        similarity = []

        radius = cellsize//2
        for x in range(0,8):
            for y in range (0,8):

                # cv.rectangle(flipped,(x+offset,y+offset),(x+cellsize-offset,y+cellsize-offset),(0,255,0))
                imageASection = imageA[x*cellsize+offset:x*cellsize+cellsize-offset,y*cellsize+offset:y*cellsize+cellsize-offset]
                imageBSection = imageB[x*cellsize+offset:x*cellsize+cellsize-offset,y*cellsize+offset:y*cellsize+cellsize-offset]
                # m = mse(imageASection, imageBSection)
                s = ssim(imageASection, imageBSection)
                cellname = str(chr(97+y)) + str(8-x)
                heappush(similarity,(s,(y*cellsize,x*cellsize, cellname)))
        return similarity
    else:
        return ssim(imageA,imageB)
def convertToTuple(list):
    return (*list,)

def getUserMoveFromCamera(board):
    # data = None
    # with open('calibration_matrix.yaml') as file:
    #     try:
    #         data = yaml.safe_load(file)
    #     except yaml.YAMLError as err:
    #         print(err)
    # camMat = data['camera_matrix']
    # distCoeff = data['dist_coeff']
    CAMERA_PATH = '/dev/v4l/by-id/usb-046d_0825_45D6C1E0-video-index0'
    
    if os.path.exists(CAMERA_PATH):
        cap = cv.VideoCapture(CAMERA_PATH)
      
    
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    oldImage = None
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    # print(aruco_dict)
    # # second parameter is id number
    # # last parameter is total image size
    # img = aruco.drawMarker(aruco_dict, 2, 700)
    # cv.imwrite("test_marker.jpg", img)


    flipped = None
    doneOnce = False
    pastHundredA = []
    pastHundredB = []
    doOnce = True
    similarityThreshold = 0.7
    motionThreshold = 0.90
    windowName = 'myWindow'
    cv.namedWindow(windowName)
    cv.moveWindow(windowName, 1280,0)
    print(board)
    while True:
        # Capture frame-by-frame
        ret, img = cap.read()
        
        # denoised = cv.fastNlMeansDenoisingColored(img,None,10,10,7,21)

        img_gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        
        # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
        parameters =  aruco.DetectorParameters_create()
    
        #print(parameters)
    
        '''    detectMarkers(...)
            detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
            mgPoints]]]]) -> corners, ids, rejectedImgPoints
            '''
            #lists of ids and the corners beloning to each id
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img_gray, aruco_dict, parameters=parameters)
        if len(corners) == 4:
            if doOnce:
                voice.say('beep')
                doOnce = False
            id = []
            for i in range (0,4):
                for j in range(0,4):
                    if i == ids[j]:
                        id.append(j)
            pt0 = [corners[id[0]][0][3][0],corners[id[0]][0][3][1]] #white
            pt1 = [corners[id[1]][0][1][0],corners[id[1]][0][1][1]] #red
            pt2 = [corners[id[2]][0][2][0],corners[id[2]][0][2][1]] #black
            pt3 = [corners[id[3]][0][0][0],corners[id[3]][0][0][1]] #blue

            cv.circle(img,convertToTuple(pt0), 10,(255,0,0),2)
            cv.circle(img,convertToTuple(pt1), 10,(0,255,0),2)
            cv.circle(img,convertToTuple(pt2), 10,(255,255,255),2)
            cv.circle(img,convertToTuple(pt3), 10,(0,0,255),2)
            
            

            pts1 = np.float32([pt0,pt1,pt2,pt3])
            pts2 = np.float32([[0,600],[0,0],[600,0],[600,600]])
            M = cv.getPerspectiveTransform(pts1,pts2)
            dst = cv.warpPerspective(img_gray,M,(600,600))
            imgCropped = dst[60:540,60:540]
            flipped = imgCropped.copy()

   
            if not doneOnce:
                oldImage = flipped.copy()
                # cv.imshow('OldImage', oldImage)
                doneOnce = True
            if oldImage is not None:
                similarity = compare_images(oldImage,flipped,board, True)
                # a = compare_images(oldImage,flipped,board,False)
                # if a < motionThreshold:
                #     print(a)
                #     continue
                
    #             mini = 1.0
    #             smallest = None
    #             for key,value in similarity.items():
    #                 if value < mini:
    #                     smallest = key
    #                     mini = value
    #             print(key,value)
    # # 
                v, (y,x, cell_name1) = heappop(similarity)
                v1, (y1,x1, cell_name2) = heappop(similarity)
                move1 = chess.Move.from_uci(cell_name1 + cell_name2)
                move2 = chess.Move.from_uci(cell_name2 + cell_name1)
                print(move1 in board.legal_moves, move2 in board.legal_moves)
                if not ((move1 in board.legal_moves) or (move2 in board.legal_moves)):
                    continue
                    
                cv.rectangle(flipped,(y,x),(y+(480//8),x+(480//8)),(255,255,255),3)
                cv.rectangle(flipped,(y1,x1),(y1+(480//8),x1+(480//8)),(255,255,255),3)
                # print(cell_name1, 'confidence: ', v)
                # print(cell_name2, 'confidence: ', v1)
                # if v < 0.5 and v1 < 0.5:
                #     return (cell_name2, cell_name2)
                pastHundredA.append(cell_name1)
                pastHundredB.append(cell_name2)
                if len(pastHundredA) > 5 and len(pastHundredB) > 5:
                    if len(set(pastHundredA + pastHundredB)) == 2:
                        if v < similarityThreshold and v1 < similarityThreshold:
                            return pastHundredA[0], pastHundredB[0]
                    else:
                        pastHundredA = []
                        pastHundredB = []
            
            # if oldImage is not None:
            #     cv.imshow(windowName, oldImage)
        
            cv.imshow(windowName, flipped)
            # cv.imshow("Warped", dst)
            # if oldImage is not None:
            #     detectChanges(oldImage, flipped)

        aruco.drawDetectedMarkers(img,corners,ids)

        # cv.imshow("Image",img)
        
   
        # time.sleep(2)
        if cv.waitKey(1) == ord('q'):
            break
        
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

# getUserMoveFromCamera()