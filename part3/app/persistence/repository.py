"""SQLAlchemy repository – persistence layer backed by a relational DB."""
from app import db
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class SQLAlchemyRepository:
    """Generic repository over SQLAlchemy models."""

    MODEL_MAP = {
        "User": User,
        "Amenity": Amenity,
        "Place": Place,
        "Review": Review,
    }

    def _model(self, model_name):
        model = self.MODEL_MAP.get(model_name)
        if model is None:
            raise ValueError(f"Unknown model: {model_name}")
        return model

    def add(self, obj):
        db.session.add(obj)
        db.session.commit()
        return obj

    def get(self, model_name, obj_id):
        model = self._model(model_name)
        return db.session.get(model, obj_id)

    def get_all(self, model_name):
        model = self._model(model_name)
        return db.session.query(model).all()

    def update(self, model_name, obj_id, data):
        obj = self.get(model_name, obj_id)
        if obj is None:
            return None
        obj.update(data)
        db.session.commit()
        return obj

    def delete(self, model_name, obj_id):
        obj = self.get(model_name, obj_id)
        if obj is None:
            return False
        db.session.delete(obj)
        db.session.commit()
        return True

    def exists(self, model_name, obj_id):
        return self.get(model_name, obj_id) is not None

    def get_by_field(self, model_name, field_name, value):
        model = self._model(model_name)
        field = getattr(model, field_name, None)
        if field is None:
            raise ValueError(f"Unknown field {field_name} on {model_name}")
        return db.session.query(model).filter(field == value).first()
