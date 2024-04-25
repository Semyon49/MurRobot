import cv2
import pymurapi as mur
import time

auv = mur.mur_init()
speed = 10
counter = 0

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

# функция движения по вертикали
def z_drave(x): 
    x=ogr(x)
    auv.set_motor_power(0,x)
    auv.set_motor_power(3,x)

# функция регулировки глубине в метрах
def kd(x): 
    z=auv.get_depth()-x
    z_drave((abs(z/3)**(1/3))*16*zch(z)*3)

# Функция для поиска линии в поле зрения камеры
def  Find_odject(image, name):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

    # значеня настраиваются в зависимости от цвета
    hsv_low = (5, 100, 100)
    hsv_max = (150, 255, 255)

    mask = cv2.inRange(img, hsv_low, hsv_max)
    cnt, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    try:   
        moments = cv2.moments(cnt[0])
        x = moments["m10"] / moments["m00"]
        y = moments['m01'] / moments['m00']

        cv2. circle(image, (int(x), int(y)), 5, (0, 255, 0))

        cv2.imshow(name, image)
        cv2.waitKey(1)
        return x, y
    
    except ZeroDivisionError:
        return None
    except IndexError:
        return None

# Функция выравнивания робота по центру относительно 2/3 изображения
def search_2_line(cor2, k=0.2):
    if cor2: 
        x, y = cor2
        controlX = 2 * (x - width / 2) / width

        if abs(controlX) < k:
            y_drave(15)

        elif controlX > k:
            auv.set_motor_power(1,-speed)
            auv.set_motor_power(0,speed)
            
        elif controlX < -k:
            auv.set_motor_power(1,speed)
            auv.set_motor_power(0,-speed)
        else:
            y_drave(0)

# Функция выравнивания робота по центру относительно 1/3 изображения
def search_1_line(cor1, cor2, k=0.2):
    if cor1: 
        x, y = cor1
        controlX = 2 * (x - width / 2) / width

        if abs(controlX) < k:
            search_2_line(cor2)

        elif controlX > k:
            auv.set_motor_power(1,-speed)
            auv.set_motor_power(0, speed)
            
        elif controlX < -k:
            auv.set_motor_power(1,speed)
            auv.set_motor_power(0,-speed)
        else:
            y_drave(0)

# Функция удержания заданной высоты 
def dive(z=5):
    global counter
    if counter == 0:
        kd(z)
        counter = 10
    counter -= 1

image = auv.get_image_bottom()
height, width = image.shape[:2]

while True:
    time.sleep(0)
    dive()

    image = auv.get_image_bottom()
    img1 = image[0:height//3, 0:width]
    img2 = image[height//3:height//3*2, 0:width]

    cor1 = Find_odject(img1, 'CCV1')
    cor2 = Find_odject(img2, 'CCV2')

    search_1_line(cor1, cor2)