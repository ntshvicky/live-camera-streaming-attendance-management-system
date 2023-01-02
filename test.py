import cv2
img  = cv2.imread("1.jpg")

x = 0
y = 0
w = 250
h = 90

color = (0,255,255)
thickness = 4
#################### Top - left ############
start_point = (x,y)
end_point = (x, (y+25))
img = cv2.line(img, start_point, end_point, color, thickness)

start_point = (x,y)
end_point = ((x+25),y)
img = cv2.line(img, start_point, end_point, color, thickness)

#################### Top - right ############
start_point = ((x+w),y)
end_point = ((x+w)-25,y)
img = cv2.line(img, start_point, end_point, color, thickness)

start_point = ((x+w),y)
end_point = ((x+w),y+25)
img = cv2.line(img, start_point, end_point, color, thickness)


#################### bottom - right ############
start_point = ((x+w),h)
end_point = ((x+w),h-25)
img = cv2.line(img, start_point, end_point, color, thickness)

start_point = ((x+w),h)
end_point = ((x+w)-25,h)
img = cv2.line(img, start_point, end_point, color, thickness)


#################### bottom - left ############
start_point = (x,h)
end_point = (x+25,h)
img = cv2.line(img, start_point, end_point, color, thickness)

start_point = (x,h)
end_point = (x,h-25)
img = cv2.line(img, start_point, end_point, color, thickness)



cv2.imshow("test", img)

cv2.waitKey(0)