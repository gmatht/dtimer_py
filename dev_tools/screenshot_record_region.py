import pyautogui
import os
if os.name == 'nt':
	import pygetwindow as gw
else:
	import pywinctl as gw
import time

print("Move mouse to top left of region to record, and press Enter")
input()
x1, y1 = pyautogui.position()

print("Move mouse to bottom right of region, and press Enter")
input()
x2, y2 = pyautogui.position()

print("recording")
w = x2 - x1
h = y2 - y1

d = {}

i=0

while True:
    img = pyautogui.screenshot(region=(x1,y1,w,h))
    i_hash=hash(img.tobytes())
    if i_hash not in d:
        img.save(f"img{i}.png")
        print(i, i_hash)
        d[i_hash]=1
        i+=1
