import cv2
import pymurapi as mur
import time

auv = mur.mur_init()
speed = 10
counter = 0

# Функция определения знака числа
def zch(x): 
    if x == 0: return 1 
    return (abs(x) / x)

# Функция приведения скорости двигателей в рабочий диапазон
def ogr(x): 
    if abs(x) > 100: x = 100 * zch(x)
    return x
    
# Функция движения по курсу
def course_drive(x): 
    x = ogr(x)
    auv.set_motor_power(0, x)
    auv.set_motor_power(1, -x)

# Функция движения по горизонтали
def y_drive(x): 
    x = ogr(x)
    auv.set_motor_power(0, x)
    auv.set_motor_power(1, x)

# Функция движения по вертикали
def z_drive(x): 
    x = ogr(x)
    auv.set_motor_power(0, x)
    auv.set_motor_power(3, x)

# Функция регулировки глубины в метрах
def kd(x): 
    z = auv.get_depth() - x
    z_drive((abs(z / 3) ** (1 / 3)) * 16 * zch(z) * 3)

# Функция для поиска линии в поле зрения камеры
def Find_object(image, name):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

    # Значения настраиваются в зависимости от цвета
    hsv_low = (5, 100, 100)
    hsv_max = (150, 255, 255)

    mask = cv2.inRange(img, hsv_low, hsv_max)
    cnt, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    # Поиск координат центра найденной фигуры
    try:
        moments = cv2.moments(cnt[0])
        x = moments["m10"] / moments["m00"]
        y = moments['m01'] / moments['m00']

        cv2.circle(image, (int(x), int(y)), 10, (0, 255, 0))
        cv2.imshow(name, image)
        cv2.waitKey(1)
        return x, y
    
    except ZeroDivisionError:
        return None
    except IndexError:
        return None

def search_line_1(img2, k=0.2):
    if coordinates1: 
        x, y = coordinates1
        controlX = 2 * (x - width / 2) / width

        if abs(controlX) < k:
            search_line_2(img2)

        elif abs(controlX) > k:
            course_drive(speed * zch(controlX))

        else:
            y_drive(0)

def search_line_2(img, k=0.2):
    if coordinates2: 
        x, y = coordinates2
        controlX = 2 * (x - width / 2) / width

        if abs(controlX) < k:
            y_drive(15)
        elif abs(controlX) > k:
            course_drive(speed * zch(controlX))
        else:
            y_drive(0)

def dive():
    global counter
    if counter == 0:
        kd(5)
        counter = 10
    counter -= 1

image = auv.get_image_bottom()
height, width = image.shape[:2]
         
while True:
    time.sleep(0)
    if counter == 0:
        kd(5)
        counter = 10
    counter -= 1
    
    image = auv.get_image_bottom()
    img1 = image[0:height // 3, 0:width]
    img2 = image[height // 3:height // 3 * 2, 0:width]

    coordinates1 = Find_object(img1, 'CCV1')
    coordinates2 = Find_object(img2, 'CCV2')

    search_line_1(img2)