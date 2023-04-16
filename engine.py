import cv2
import numpy as np
import matplotlib.pyplot as plt


# Przejście z modelu RGB do modelu binarnego na podstawie kolejnych klatek
def calcPhase(img1, img2):
    #normalizacja do rozdzielczości 256x265
    img1 = cv2.resize(img1, (256, 256))
    img2 = cv2.resize(img2, (256, 256))

    #Przejście do skali szarosci
    img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

    c = []
    b = []
    times = 0
    #Porównanie klatek
    for k in range(0, len(img1)):
        for i in range(0, len(img1[0])):
            delta = abs(pow(img1[k, i], 2) - pow(img2[k, i], 2))
            if delta > 15000:
                c.append(img2[k, i])
                b.append(img1[k, i])
                times = times + 1
    if times < 15:
        return None
    means = [np.mean(c), np.mean(b)]
    stds = [np.std(c), np.std(b)]
    color = max(means)
    index = means.index(color)
    std = stds[index]
    print(color)
    #Przejście do modelu binarnego
    _, threshold = cv2.threshold(img2, color - std, color+std, cv2.THRESH_BINARY)

    #Oczyszczanie modelu binarnego
    kernel = np.ones((32, 32), np.uint8)
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

    return opening


def calcPercentage(img):
    p = 0
    for k in range(0, len(img)):
        for i in range(0, len(img[0])):
            if img[k, i]:
                p = p + 1

    return p * 100 / (len(img)*len(img[0]))

