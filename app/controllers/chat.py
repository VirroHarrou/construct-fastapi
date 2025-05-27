import json
from fastapi import APIRouter, WebSocket, Query, WebSocketDisconnect, WebSocketException, status
from fastapi.logger import logger
from app.services.chat import ConnectionManager
from app.dependencies.database import async_session
from app.dependencies.auth import get_current_user_from_token

router = APIRouter(tags=["chat"])
manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    try:
        async with async_session() as session:
            user = await get_current_user_from_token(token, session)
            await manager.connect(websocket, user)
            
            try:
                while True:
                    try:
                        data = await websocket.receive_json()
                        await manager.handle_action(data, user, session)
                    except json.JSONDecodeError:
                        await websocket.send_json({
                            "error": "Invalid JSON format"
                        })
                    except WebSocketException as e:
                        await websocket.send_json({
                            "status": "error",
                            "code": e.code,
                            "detail": e.reason
                        })
                        await websocket.close(code=e.code)
                        break
            except WebSocketDisconnect:
                manager.disconnect(user)
                
    except Exception as e:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=f"WebSocket error: {e}")
        logger.error(f"WebSocket error: {e}")