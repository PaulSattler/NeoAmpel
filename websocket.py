import asyncio
import json
import logging
import websockets
import time
import board
import neopixel


pixel_pin = board.D18
num_pixels = 180
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER) #auto write ändern
logging.basicConfig()
STATE = {"valuer": 0, "valueg" : 0, "valueb" : 0, "valueh" : 0}
USERS = set()
colorr = 0
colorg = 0
colorb = 0

def state_event():
    return json.dumps({"type": "state", **STATE})
def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})
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
    
async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "dunkel":
                STATE["valueh"] -= 1
                await notify_state()
            elif data["action"] == "hell":
                STATE["valueh"] += 1
                await notify_state()
            elif data["action"] == "plusr":
                STATE["valuer"] += 1
                await notify_state()
            elif data["action"] == "minusr":
                STATE["valuer"] -= 1
                await notify_state()  
            elif data["action"] == "plusg":
                STATE["valueg"] += 1
                await notify_state()
            elif data["action"] == "minusg":
                STATE["valueg"] -= 1
                await notify_state()
            elif data["action"] == "plusb":
                STATE["valueb"] += 1
                await notify_state()
            elif data["action"] == "minusb":
                STATE["valueb"] -= 1
                await notify_state()
            else:
                logging.error("unsupported event: {}", data)
            #print(STATE["value"])
            colorr = ledchecker(STATE["valuer"])
            colorg = ledchecker(STATE["valueg"])
            colorb = ledchecker(STATE["valueb"])
            pixels.fill((colorr, colorg, colorb))
            pixels.show()
    finally:
        await unregister(websocket)


start_server = websockets.serve(counter, "192.168.188.24", 666)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()