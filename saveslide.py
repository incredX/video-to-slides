import cv2
import pytesseract
import numpy as np
import yaml

def _isDifferent(img1, img2,errore: int) -> bool:
    '''
    determina se la differenza tra le immagini è maggiore di errore
    '''
    # mean squared error
    h, w, d = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err/(float(h*w))
    return mse>errore

def _cropped(frame,bordo: list):
    '''
    ritorna il frame croppato secondo la lista bordo
    0: riga iniziale 1: riga finale
    2: colonna iniziale 3: colonna finale
    '''
    return frame[bordo[0]:bordo[1],bordo[2]:bordo[3]]

def _getSlidenumber(frame) -> int:
    '''
    ritorna il numero letto nel frame
    '''
    num = pytesseract.image_to_string(frame, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz')
    return num



def _getBorder(borderperc: list,framedim: list) -> list:
    '''
    ritorna le coordinate del bordo formattate secondo lo standard della funzione _cropped
    '''
    maplist = [[1,1],[3,1],[0,0],[2,0]]
    '''
    maplist indica: i[0] il corrispondente indice in borderperc
    i[1] se considerare altezza o larghezza
    '''
    return [int(borderperc[i[0]]*framedim[i[1]]/100) for i in maplist]

def run(video_path:str):
    '''
    saves slides from 'video_path'
    '''
    # definizione variabili e init classi

    config = yaml.safe_load(open('video-to-slides/config/config.yml', 'rb'))# file config

    pytesseract.pytesseract.tesseract_cmd = config['TESSERACT_PATH']

    vidcap = cv2.VideoCapture(video_path)

    frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)           # frame totali
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    dim = [vidcap.get(cv2.CAP_PROP_FRAME_WIDTH),vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)]
    bordo_std = _getBorder(config['NUMBER_CROP_BORDERS'],dim)       # per cropping sul numero
    bordo_slide = _getBorder(config['IMG_CROP_BORDERS'],dim)        # per cropping slide definitiva
    skipFrames = config['READ_EVERY_N_FRAMES']              # controlla solo un frame ogni 'skipFrames'
    errore = config['TOLERANCE']                            # tolleranza confronto slide
    startFrame = config['START_FRAME']
    frameSkipper = 1
    c = startFrame
    numeriSlide = []                                        # lista per evitare ripetizioni di slide
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, c)                  # imposta frame iniziale

    lastFrame = vidcap.read()[1]                      # init del primo frame

    # main loop
    while c<frames:
        print('\033[K','\r{}s/{}s  slides salvate: {}'.format(round(c/fps),round(frames/fps),numeriSlide),end='') # avanzamento
        c+=1
        nextFrame = vidcap.read()[1] # legge frame

        if frameSkipper<skipFrames:
            frameSkipper+=1
            continue
        else:
            frameSkipper=1
            try:
                if _isDifferent(_cropped(lastFrame,bordo_std),_cropped(nextFrame,bordo_std),errore): # controlla similitudine
                    slidenum = int(_getSlidenumber(_cropped(nextFrame,bordo_std))) # controlla numero
                    
                if slidenum not in numeriSlide: # se la slide non è ancora apparsa
                    nextFrame = vidcap.read()[1] # skippa un frame per evitare slide blurrate
                    # orribile ma più veloce di 'vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame)' soprattutto con 1 solo frame skip
                    cv2.imwrite('{}\slide{}.png'.format(config['SLIDES_PATH'],slidenum),_cropped(nextFrame,bordo_slide)) #salva frame successivo
                    numeriSlide.append(slidenum)
            except Exception as e:
                #print(e)
                pass
                
        lastFrame = nextFrame # next frame diventa lastFrame