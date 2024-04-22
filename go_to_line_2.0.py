import cv2
import pymurapi as mur
import time

auv = mur.mur_init()
speed = 10

# функция определения знака числа
def zch(x): 
    if x==0: return 1 
    return (abs(x)/x)

# функция преведения скорости двигателей в работчий диапозон
def ogr(x): 
    if abs(x)>100: x=100*zch(x)
    return x

# функция движения по горизонтали
def y_drave(x): 
    x=ogr(x)
    auv.set_motor_power(0,x)
    auv.set_motor_power(1,x)

def  Find_odject(image, name):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

    # значеня настраиваются в зависимости от цвета
    hsv_low = (5, 100, 100)
    hsv_max = (150, 255, 255)

    mask = cv2.inRange(img, hsv_low, hsv_max)
    cnt, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(image, cnt, -1, (0,255,0), 2)

    

    # поиск координат центра найденной фигуры
    if cnt:
        try:
            # hull = cv2.convexHull(image)
            # approx = cv2.approxPolyDP(hull, cv2.arcLength(cnt, True), True)
            # ((x1, y1), (h, w), angele) = cv2.minAreaRect(approx)

            # print(x1, y1, h, w, angele)
            
            moments = cv2.moments(cnt[0])
            x1 = moments["m10"] / moments["m00"]
            x = moments["m10"] / (moments["m00"] * 2)
            y1 = moments['m01'] / moments['m00']
            y = moments['m01'] / (moments['m00'] * 2)

            # y = 0

            cv2. circle(image, (int(x), int(y)), 10, (0, 255, 0))
            cv2. circle(image, (int(x1), int(y1)), 10, (0, 255, 255))

            cv2.imshow(name, image)
            cv2.waitKey(1)
            return x, y
        except ZeroDivisionError:
            return None

image = auv.get_image_bottom()
height, width = image.shape[:2]

while True:
    image = auv.get_image_bottom()
    cor = Find_odject(image)

    if cor: 
        x, y = cor
        controlX = 2 * (x - width / 2) / width
        controlY = 2 * (y - height / 2) / height

        if abs(controlX) < 0.25:
            y_drave(15)

        elif controlX > 0.17:
            auv.set_motor_power(1,speed / 3)
            auv.set_motor_power(0, speed)
            
        elif controlX < -0.17:
            auv.set_motor_power(1,speed)
            auv.set_motor_power(0,speed / 3)
        else:
            y_drave(0)
            
# while True:
#     image = auv.get_image_bottom()
#     img1 = image[0:height//3, 0:width]
#     img2 = image[height//3:height//3*2, 0:width]

#     # cv2.imshow('1', img1)
#     # cv2.imshow('2', img2)
#     # cv2.waitKey(1)
#     cor = Find_odject(img1, '123')
#     cor = Find_odject(img2, '234')

    # if cor: 
    #     x, y = cor
    #     controlX = 2 * (x - width / 2) / width
    #     controlY = 2 * (y - height / 2) / height

    #     if abs(controlX) < 0.25:
    #         y_drave(15)

    #     elif controlX > 0.17:
    #         auv.set_motor_power(1,speed / 3)
    #         auv.set_motor_power(0, speed)
            
    #     elif controlX < -0.17:
    #         auv.set_motor_power(1,speed)
    #         auv.set_motor_power(0,speed / 3)
    #     else:
    #         y_drave(0)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            