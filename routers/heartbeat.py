import json
from aiohttp import request
from fastapi import APIRouter
from tinydb import Query, TinyDB, where
from routers.websocket_manager import room_websockets
from pydantic import BaseModel
import time
from routers.models import User_action

router = APIRouter()

user_last_hit = {}


@router.post("/room/{room_id}/heartbeat")
async def startHeartBeat(room_id: str, userAction: User_action):
    if (userAction.actionType == "SENT_HEARTBEAT"):
        heartbeat_Received = await heartbeat(room_id, userAction)
        return heartbeat_Received
    else:
        not_Receive = await update_timers(userAction, None, room_id)
        return not_Receive


async def heartbeat(room_id: str, userAction: User_action):
    db = TinyDB('rooms_data_db.json')
    rooms = db.table('rooms')
    Room = Query()
    Users = Query()
    if rooms.contains(where('roomId') == room_id):
        if rooms.contains((Room.users.any(Users.userId == userAction.userData.userId)) & (Room.roomId == room_id)):
            user_id = userAction.userData.userId
            current_time = int(time.time())
            user_last_hit[user_id] = current_time
            userAction.actionType = "RECEIVED_HEARTBEAT"
            return userAction


async def update_timers(userAction: User_action, websocket: None, room_id: str):
    for last_hit in user_last_hit.values():
        current_time = int(time.time())
        elapsed_time = current_time - last_hit
        if elapsed_time > 15:
            message = ({"actionType": "USER_INACTIVE",
                       "userId": userAction.userData.userId})
            for web in room_websockets.get(room_id, []):
                if web["websocket"] != websocket:
                    await web['websocket'].send_text(json.dumps(message))
            userAction.actionType = "USER_INACTIVE"
            return userAction
        return userAction