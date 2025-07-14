from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_view import OrderView
from app.schemas.orders import OrderCreate, OrderResponse, OrderUpdate

class OrderService:
    STATUS_MAP = {1: "ожидание", 2: "в работе", 3: "завершен"}
    
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
        status_num = next((k for k, v in self.STATUS_MAP.items() if v == status), None)
        
        if view:
            current_level = view.status if view.status is not None else 0
            new_level = status_num if status_num is not None else 0
            
            if new_level >= current_level:
                view.status = status_num
        else:
            view = OrderView(user_id=user_id, order_id=order_id, status=status_num)
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
            select(func.max(OrderView.status))
            .where(OrderView.order_id == order_id)
        )
        status = self.STATUS_MAP.get(status_priority)
        
        connected_user_ids = await self.session.scalars(
            select(OrderView.user_id).where(
                and_(
                    OrderView.order_id == order_id,
                    OrderView.status == status_priority,
                    OrderView.status >= 1,
                )
            )
        )
        
        response = OrderResponse.model_validate(order)
        response.views_count = views_count or 0
        response.status = status
        response.connected_user_ids = list(connected_user_ids)
        return response
    
    async def get_all_orders(self, offset: int, limit: int) -> list[OrderResponse]:
        current_time = datetime.now(timezone.utc) 
        stmt = select(
            Order,
            func.count(OrderView.order_id).label('views_count'),
            func.max(OrderView.status).label('status_priority') 
        ).outerjoin(
            OrderView, Order.id == OrderView.order_id
        ).where(
            Order.end_time > current_time 
        ).group_by(Order.id).offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        orders = []
        
        for row in result:
            order = row[0]
            views_count = row[1] or 0
            status_priority = row[2] 
            
            order_data = OrderResponse.model_validate(order)
            order_data.views_count = views_count
            order_data.status = self.STATUS_MAP.get(status_priority)
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
        
    async def get_connected_orders(self, user_id: UUID) -> list[OrderResponse]:
        OrderViewAll = aliased(OrderView)
        
        stmt = select(
            Order,
            func.count(OrderViewAll.order_id).label('views_count'),
            func.max(OrderViewAll.status).label('status_priority')
        ).outerjoin(
            OrderViewAll, Order.id == OrderViewAll.order_id
        ).where(
            or_(
                Order.user_id == user_id,
                and_(
                    Order.user_id != user_id,
                    exists().where(
                        and_(
                            OrderView.order_id == Order.id,
                            OrderView.user_id == user_id,
                            OrderView.status.isnot(None)
                        )
                    )
                )
            )
        ).group_by(Order.id)

        result = await self.session.execute(stmt)
        rows = result.all()
        
        orders = []
        for row in rows:
            order = row[0]
            views_count = row[1] or 0
            status_priority = row[2]
            
            order_data = OrderResponse.model_validate(order)
            order_data.views_count = views_count
            order_data.status = self.STATUS_MAP.get(status_priority)
            orders.append(order_data)
        
        if not orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orders not found"
            )
        
        return orders