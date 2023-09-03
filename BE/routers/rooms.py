import asyncio
import json
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from typing import Dict
import uuid
from routers.data_manager import save_data_in_db, update_data_in_db
from routers.websocket_manager import room_websockets
from tinydb import TinyDB, Query, where
from routers.models import User, User_data, User_action, User_details
from fastapi.encoders import jsonable_encoder


router = APIRouter()

admin_user_id: str = ""
selected_storypoint: list = []


@router.post("/create_room", response_model=Dict[str, str])
async def create_room(request: Request):
    room_id = str(uuid.uuid4())
    room_data = {"roomId": room_id, "users": []}
    global admin_user_id
    admin_user_id = request.headers.get('SP-U')
    save_data_in_db(room_data)
    return {"room_id": room_id}


@router.post("/room/{room_id}/join")
async def join_room(room_id: str, user_details: User_details):
    db = TinyDB('rooms_data_db.json')
    rooms = db.table('rooms')
    Room = Query()
    Users = Query()
    if rooms.contains(Room.roomId == room_id):
        if not rooms.contains((Room.users.any(Users.userId == user_details.userId)) & (Room.roomId == room_id)):
            global admin_user_id
            user_to_be_stored = {
                "userId": user_details.userId,
                "displayName": user_details.displayName,
                "isAdmin": True if (user_details.userId == admin_user_id) else False,
                "isActive": True,
                "jobRole":user_details.jobRole,
                "data": {
                    "storyPoints": None
                }
            }
            update_data_in_db(user_to_be_stored, room_id)
            return user_to_be_stored
        else:
            return JSONResponse(status_code=403, content={"error": "User is already in the room"})
    else:
        return JSONResponse(status_code=404, content={"error": "Room not found"})

# "Scrum Master" if(user_details.userId == admin_user_id) else user_details.jobRole,

@router.put("/room/{room_id}/update")
async def update_room_data(room_id: str, user_action: User_action):
    db = TinyDB('rooms_data_db.json')
    rooms = db.table('rooms')
    Room = Query()
    Users = Query()
    user_id = user_action.userData.userId
    if rooms.contains((where('roomId') == room_id) & (where('users') != None)):
        room_document = rooms.search((Room.users.any(
            Users.userId == user_action.userData.userId)) & (Room.roomId == room_id))
        users = room_document[0]['users']
        user_index = next((index for (index, user) in enumerate(
            users) if user['userId'] == user_action.userData.userId), None)
        room_document[0]['users'][user_index]['data']['storyPoints'] = user_action.userData.data.storyPoints
        rooms.update(room_document[0], Room.roomId == room_id)
        for websocket in room_websockets[room_id]:
            if user_id != websocket['user_id']:
                await websocket['websocket'].send_text(json.dumps(jsonable_encoder(user_action)))
        return JSONResponse(content=jsonable_encoder(user_action))
    else:
        raise HTTPException(
            status_code=404, detail="Room not found or User not found in the room")


@router.put("/room/{room_id}/reveal")
async def update_room_data(room_id: str, user_action: User_action):
    db = TinyDB('rooms_data_db.json')
    rooms = db.table('rooms')
    Room = Query()
    room_document = rooms.search(where('roomId') == room_id)
    if rooms.contains(where('roomId') == room_id):
        if (user_action.actionType == "STORY_POINT_REVEAL"):
            admin_user = next(
                (user for user in room_document[0]['users'] if user['userId'] == user_action.userData.userId and user['isAdmin'] == True), None)
            if admin_user:
                for websocket in room_websockets[room_id]:
                    if user_action.userData.userId != websocket['user_id']:
                        await websocket['websocket'].send_text(json.dumps(jsonable_encoder(user_action)))
                return user_action
            else:
                return JSONResponse(status_code=403, content={"error": "User is not admin"})
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid Request"})
    else:
        return JSONResponse(status_code=404, content={"error": "Room not found"})


@router.put("/room/{room_id}/reset")
async def update_room_data(room_id: str, user_action: User_action):
    db = TinyDB('rooms_data_db.json')
    rooms = db.table('rooms')
    Room = Query()
    room_document = rooms.search(where('roomId') == room_id)
    if rooms.contains(where('roomId') == room_id):
        if (user_action.actionType == "STORY_POINT_RESET"):
            admin_user = next(
                (user for user in room_document[0]['users'] if user['userId'] == user_action.userData.userId and user['isAdmin'] == True), None)
            if admin_user:
                for user in room_document[0]['users']:
                    user['data']['storyPoints'] = None
                rooms.update(room_document[0], Room.roomId == room_id)
                for websocket in room_websockets[room_id]:
                    if user_action.userData.userId != websocket['user_id']:
                        await websocket['websocket'].send_text(json.dumps(jsonable_encoder(user_action)))
                return user_action
            else:
                return JSONResponse(status_code=403, content={"error": "User is not admin"})
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid Request"})
    else:
        return JSONResponse(status_code=404, content={"error": "Room not found"})


@router.put("/room/{room_id}/admin/change")
async def update_room_data(room_id: str, user_action: User_action, request: Request):
    db = TinyDB('rooms_data_db.json')
    rooms = db.table('rooms')
    Room = Query()
    room_document = rooms.search(where('roomId') == room_id)
    global admin_user_id
    if rooms.contains(where('roomId') == room_id):
        user_id = request.headers.get('SP-U')
        if (user_action.actionType == "CHANGE_ADMIN"):
            response_user_action = {
                'actionType': user_action.actionType, 'userData': []}
            admin_user = next(
                (user for user in room_document[0]['users'] if user['userId'] == user_id and user['isAdmin'] == True), None)
            if admin_user:
                for user in room_document[0]['users']:
                    if user_id == user['userId']:
                        user['isAdmin'] = False
                        response_user_action['userData'].append(user)
                    if user['userId'] == user_action.userData.userId:
                        user['isAdmin'] = True
                        response_user_action['userData'].append(user)
                rooms.update(room_document[0], Room.roomId == room_id)
                admin_user_id = user_action.userData.userId
                for websocket in room_websockets[room_id]:
                    if user_id != websocket['user_id']:
                        await websocket['websocket'].send_text(json.dumps(response_user_action))
                return response_user_action
            else:
                return JSONResponse(status_code=403, content={"error": "User is not admin"})
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid Request"})
    else:
        return JSONResponse(status_code=404, content={"error": "Room not found"})
