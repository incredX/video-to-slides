import cv2
import pytesseract
import numpy as np
import yaml

# funzioni

def isDifferent(img1, img2,errore) -> bool:
    '''
    determina se la differenza tra le immagini è maggiore di errore
    '''
    # mean squared error
    h, w, d = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err/(float(h*w))
    #print(mse)
    return mse>errore

def cropped(frame,bordo):
    '''
    ritorna il frame croppato secondo l'array bordo
    0: riga iniziale 1: riga finale
    2: colonna iniziale 3: colonna finale
    '''
    return frame[bordo[0]:bordo[1],bordo[2]:bordo[3]]

def getSlidenumber(frame) -> int:
    '''
    ritorna il numero letto nel frame
    '''
    num = pytesseract.image_to_string(frame, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz')
    return num

# definizione variabili e init classi

config = yaml.safe_load(open('config/config.yml', 'rb'))# file config

pytesseract.pytesseract.tesseract_cmd = config['TESSERACT_PATH']

vidcap = cv2.VideoCapture(config['VIDEO_NAME'])

frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)           # frame totali
fps = vidcap.get(cv2.CAP_PROP_FPS)

bordo_std = config['IMG_CROP_BORDERS']                  # per cropping sul numero
skipFrames = config['READ_EVERY_N_FRAMES']              # controlla solo un frame ogni 'skipFrames'
errore = config['TOLERANCE']                            # tolleranza confronto slide
startFrame = config['START_FRAME']
frameSkipper = 1
c = startFrame
numeriSlide = []                                        # lista per evitare ripetizioni di slide
vidcap.set(cv2.CAP_PROP_POS_FRAMES, c)                  # imposta frame iniziale

isFrame, lastFrame = vidcap.read()                      # init del primo frame

# main loop

while c<frames:
    print('\033[K','\r{}s/{}s  slides salvate: {}'.format(round(c/fps),round(frames/fps),numeriSlide),end='') # avanzamento
    c+=1
    isFrame, nextFrame = vidcap.read() # legge frame

    if frameSkipper<skipFrames:
        frameSkipper+=1
        continue
    else:
        frameSkipper=1
        try:
            if isDifferent(cropped(lastFrame,bordo_std),cropped(nextFrame,bordo_std),errore): # controlla similitudine
                slidenum = int(getSlidenumber(cropped(nextFrame,bordo_std))) # controlla numero
                
            if slidenum not in numeriSlide: # se la slide non è ancora apparsa
                cv2.imwrite('{}\slide{}.png'.format(config['SLIDES_PATH'],slidenum),nextFrame) #salva frame successivo
                numeriSlide.append(slidenum)
        except Exception as e:
            #print(e)
            pass
            
    lastFrame = nextFrame # next frame diventa lastFrame