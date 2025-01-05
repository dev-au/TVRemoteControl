import random

from fastapi import Request
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse

from bot_src.handlers.start import users
from config import render, ROOM_MANAGER, bot

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def tv_client(request: Request):
    return render("client_side.html", {"request": request})


@router.websocket("/tv")
async def tv_websocket(websocket: WebSocket):
    await websocket.accept()
    room_code = None
    for _ in range(100):
        room_code = str(random.randint(1000, 9999))
        if room_code not in ROOM_MANAGER:
            break
    if not room_code:
        room_code = str(random.randint(100000, 999999))
    ROOM_MANAGER[room_code] = {'user': None, 'tv': websocket}
    await websocket.send_json({"type": "room_code", "room_code": room_code})
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        if ROOM_MANAGER[room_code]['user']:
            try:
                await bot.send_message(chat_id=ROOM_MANAGER[room_code]['user'], text='TV uzildi')
            except:
                pass
            del users[ROOM_MANAGER[room_code]['user']]
        del ROOM_MANAGER[room_code]
