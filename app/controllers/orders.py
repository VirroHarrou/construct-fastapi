from fastapi import APIRouter, Depends, HTTPException, Header, Path, status
from app.dependencies.auth import get_current_user
from app.schemas.users import UserResponse
from app.services.orders import OrderService
from app.schemas.orders import OrderCreate, OrderResponse, OrderUpdate
from app.dependencies.database import AsyncSession, get_db
from uuid import UUID

router = APIRouter(tags=["orders"])

def get_order_service(session: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(session)

@router.post("/orders/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    user: UserResponse = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.create_order(user.id, order_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.post("/orders/{order_id}/view")
async def mark_order_viewed(
    order_id: UUID,
    user: UserResponse = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    await service.mark_viewed(user.id, order_id)
    return {"status": "view marked"}

@router.get("/orders/")
async def get_all(
    service: OrderService = Depends(get_order_service),
):
    return await service.get_all_orders()

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID = Path(...),
    service: OrderService = Depends(get_order_service),
):
    return await service.get_order(order_id)

@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_data: OrderUpdate,
    order_id: UUID = Path(...),
    user: UserResponse = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    return await service.update_order(order_id, order_data, user.id)

@router.delete("/orders/{order_id}", status_code=204)
async def delete_order(
    order_id: UUID = Path(...),
    user: UserResponse = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    await service.delete_order(order_id, user.id)