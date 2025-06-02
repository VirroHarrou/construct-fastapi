from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import case, func, select
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

    async def mark_viewed(self, user_id: UUID, order_id: UUID, status: str = None) -> None:
        if not await self.session.get(Order, order_id):
            raise HTTPException(status_code=404, detail="Order not found")
        
        view = await self.session.get(OrderView, (user_id, order_id))
        if view:
            view.status = status
        else:
            view = OrderView(user_id=user_id, order_id=order_id, status=status)
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
            raise HTTPException(status_code=404, detail="Order not found")
        
        views_count = await self.session.scalar(
            select(func.count()).where(OrderView.order_id == order_id)
        )
        
        status_priority = await self.session.scalar(
            select(func.max(
                case(
                    (OrderView.status == "ожидание", 1),
                    (OrderView.status == "в работе", 2),
                    (OrderView.status == "завершен", 3),
                    else_=0
                )
            )).where(OrderView.order_id == order_id)
        )
        status_map = {
            1: "ожидание",
            2: "в работе",
            3: "завершен"
        }
        status = status_map.get(status_priority)
        
        response = OrderResponse.model_validate(order)
        response.views_count = views_count or 0
        response.status = status
        return response
    
    async def get_all_orders(self) -> list[OrderResponse]:
        result = await self.session.execute(select(Order))
        orders = []
        for order in result.scalars().all():
            views_count = await self.session.scalar(
                select(func.count()).where(OrderView.order_id == order.id)
            )
            status_priority = await self.session.scalar(
                select(func.max(
                    case(
                        (OrderView.status == "ожидание", 1),
                        (OrderView.status == "в работе", 2),
                        (OrderView.status == "завершен", 3),
                        else_=0
                    )
                )).where(OrderView.order_id == order.id)
            )
            status_map = {
                1: "ожидание",
                2: "в работе",
                3: "завершен"
            }
            status = status_map.get(status_priority)
            
            order_data = OrderResponse.model_validate(order)
            order_data.views_count = views_count or 0
            order_data.status = status
            orders.append(order_data)
        
        return orders
    
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