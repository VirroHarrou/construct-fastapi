import json
from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, Query, WebSocketDisconnect, WebSocketException, status
from fastapi.logger import logger
from app.schemas.chat_messages import ChatListItem, ChatMessageResponse
from app.schemas.users import UserResponse
from app.services.chat import ChatService
from app.services.connection_manager import ConnectionManager
from app.dependencies.database import async_session, get_db
from app.dependencies.auth import get_current_user, get_current_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession

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
        
@router.get("/chats/", response_model=list[ChatListItem])
async def get_user_chats(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ChatService(db)
    return await service.get_user_chats(current_user.id)

@router.get("/{partner_id}/messages", response_model=list[ChatMessageResponse])
async def get_chat_history(
    partner_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    service = ChatService(db)
    return await service.get_chat_history(
        current_user.id, 
        partner_id, 
        limit, 
        offset
    )