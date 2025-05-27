from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_view import OrderView
from app.schemas.orders import OrderCreate, OrderResponse, OrderUpdate

class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, user_id: UUID, order_data: OrderCreate) -> OrderResponse:
        new_order = Order(**order_data.model_dump(), user_id=user_id)
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)
        return OrderResponse.model_validate(new_order)

    async def mark_viewed(self, user_id: UUID, order_id: UUID) -> None:
        view = OrderView(user_id=user_id, order_id=order_id)
        self.session.add(view)
        await self.session.commit()
        
    async def update_order(
        self,
        order_id: UUID,
        order_data: OrderUpdate,
        user_id: UUID
    ) -> OrderResponse:
        order = await self.session.get(Order, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
                )
        if user_id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
                )
        
        for key, value in order_data.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
        
        await self.session.commit()
        await self.session.refresh(order)
        return OrderResponse.model_validate(order)
    
    async def get_order(self, order_id: UUID) -> OrderResponse:
        order = await self.session.get(Order, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
                )
        return OrderResponse.model_validate(order)
    
    async def get_all_orders(self) -> list[OrderResponse]:
        result = await self.session.execute(select(Order))
        orders = result.scalars().all()
        return [OrderResponse.model_validate(o) for o in orders]
    
    async def delete_order(self, order_id: UUID, user_id: UUID) -> None:
        order = await self.session.get(Order, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
                )
        if user_id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
                )
        
        await self.session.delete(order)
        await self.session.commit()