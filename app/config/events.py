from sqlalchemy import event, inspect
from app.config.settings import settings
from app.services.images import ImageService

image_service = ImageService()

def register_model_cleanup(model, fields: list):
    @event.listens_for(model, "before_update")
    def before_update_listener(mapper, connection, target):
        state = inspect(target)
        for field in fields:
            history = state.get_history(field, False)
            if history.has_changes() and history.deleted:
                old_url = history.deleted[0]
                if old_url:
                    image_service.delete_image(old_url)

    @event.listens_for(model, "before_delete")
    def before_delete_listener(mapper, connection, target):
        for field in fields:
            url = getattr(target, field)
            if url:
                image_service.delete_image(url)