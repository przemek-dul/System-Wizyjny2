import cv2
import numpy as np
import matplotlib.pyplot as plt


def calcPhase(img1, img2):
    img1 = cv2.resize(img1, (256, 256))
    img2 = cv2.resize(img2, (256, 256))

    img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

    c = []
    b = []
    times = 0
    for k in range(0, len(img1)):
        for i in range(0, len(img1[0])):
            delta = abs(pow(img1[k, i], 2) - pow(img2[k, i], 2))
            if delta > 15000:
                c.append(img2[k, i])
                b.append(img1[k, i])
                times = times + 1
    if times < 15:
        return None
    color = max(np.mean(c), np.mean(b))
    print(color)
    _, threshold = cv2.threshold(img2, color - int(0.18*color), 255, cv2.THRESH_BINARY)
    kernel = np.ones((16, 16), np.uint8)
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

    return opening


def calcPercentage(img):
    p = 0
    for k in range(0, len(img)):
        for i in range(0, len(img[0])):
            if img[k, i]:
                p = p + 1

    return p * 100 / (len(img)*len(img[0]))

