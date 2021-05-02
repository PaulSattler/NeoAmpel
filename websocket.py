import asyncio
import json
import logging
import websockets
import time
import board
import neopixel
import threading

pixel_pin = board.D18
num_pixels = 180
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER) #auto write ändern
logging.basicConfig()
STATE = {"valuer": 0, "valueg" : 0, "valueb" : 0, "time" : 0}
USERS = set()
colorr = 0
colorg = 0
colorb = 0
stopRainbow = False
def state_event():
    return json.dumps({"type": "state", **STATE})
def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})
def user_ping():
    return 
async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])
async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])
async def register(websocket):
    USERS.add(websocket)
    await notify_users()
async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()
    
def ledchecker(i):
    if i <= 0:
        return 0
    elif i >= 255:
        return 255
    else:
        return i
def wheel(pos):
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait=0.001):
    while True:
        global STATE
        global stopRainbow
        wait = STATE["time"]
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
                if stopRainbow == True:
                    colorr = 128
                    colorg = 128
                    colorb = 128
                    pixels.fill((colorr, colorg, colorb))
                    pixels.show()
                    break  
            pixels.show()
            time.sleep(wait)
        if stopRainbow == True:
            colorr = 128
            colorg = 128
            colorb = 128
            pixels.fill((colorr, colorg, colorb))
            pixels.show()
            break        
               
        
async def counter(websocket, path):
    global stopRainbow
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if "R" in data["action"]:
                x = data["action"]
                STATE["valuer"] = x[1:]
                await notify_state()
            elif "G" in data["action"]:
                x = data["action"]
                STATE["valueg"] = x[1:]
                await notify_state()
            elif "B" in data["action"]:
                x = data["action"]
                STATE["valueb"] = x[1:]
                await notify_state()
            elif "X" in data["action"]:
                #start
                stopRainbow = False
                rainbow_thread = threading.Thread(target = rainbow_cycle)
                rainbow_thread.start()
                await notify_state()
            elif "Y" in data["action"]:
                STATE["time"] = 0.001
                stopRainbow = True
                await notify_state()
            elif "T" in data["action"]:
                x = data["action"]
                STATE["time"] = int(x[1:]) / 100000
                #print(STATE["time"])
            else:
                logging.error("unsupported event: {}", data)
            #print(STATE["value"])
            colorr = ledchecker(int(STATE["valuer"]))
            colorg = ledchecker(int(STATE["valueg"]))
            colorb = ledchecker(int(STATE["valueb"]))
            pixels.fill((colorr, colorg, colorb))
            pixels.show()
            
    finally:
        await unregister(websocket)


start_server = websockets.serve(counter, "192.168.188.24", 666)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
