from tinydb import TinyDB, Query, where


db = TinyDB('rooms_data_db.json')


def save_data_in_db(data_to_be_stored):
    rooms = db.table('rooms')
    rooms.insert(data_to_be_stored)


def update_data_in_db(data_to_be_stored, room_id: str):
    rooms = db.table('rooms')
    Room = Query()
    room_list = rooms.search(Room.roomId == room_id)
    room_list[0]['users'].append(data_to_be_stored)
    rooms.upsert(room_list[0],  Room.roomId == room_id)


def delete_users(room_id: str, user_id: str):
    rooms = db.table('rooms')
    Room = Query()
    room_list = rooms.search(Room.roomId == room_id)
    user_index = next((index for (index, user) in enumerate(
        room_list[0]['users']) if user['userId'] == user_id), None)
    del room_list[0]['users'][user_index]
    rooms.upsert(room_list[0], Room.roomId == room_id)


def delete_room(room_id: str):
    rooms = db.table('rooms')
    Room = Query()
    room_list = rooms.search(Room.roomId == room_id)
    if len(room_list[0]['users']) == 0:
        rooms.remove(where('roomId') == room_id)
