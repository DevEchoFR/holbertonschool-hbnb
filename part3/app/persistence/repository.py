"""In-memory repository – our simple storage system."""


class InMemoryRepository:
    """Keeps all objects in Python dictionaries (no database needed)."""

    def __init__(self):
        # Main storage: { "User": { "uuid1": <User obj>, ... }, ... }
        self._storage = {}

    # --- private helper ---------------------------------------------------

    def _bucket(self, model_name):
        """Get (or create) the dict for a model type."""
        if model_name not in self._storage:
            self._storage[model_name] = {}
        return self._storage[model_name]

    # --- public methods ---------------------------------------------------

    def add(self, obj):
        """Save a new object."""
        bucket = self._bucket(type(obj).__name__)
        bucket[obj.id] = obj

    def get(self, model_name, obj_id):
        """Return one object by id, or None if not found."""
        return self._bucket(model_name).get(obj_id)

    def get_all(self, model_name):
        """Return a list of all objects for a model."""
        return list(self._bucket(model_name).values())

    def update(self, model_name, obj_id, data):
        """Update an object's fields. Returns the object or None."""
        obj = self.get(model_name, obj_id)
        if obj is None:
            return None
        obj.update(data)
        return obj

    def delete(self, model_name, obj_id):
        """Delete an object. Returns True if deleted, False if not found."""
        bucket = self._bucket(model_name)
        if obj_id not in bucket:
            return False
        del bucket[obj_id]
        return True

    def exists(self, model_name, obj_id):
        """Check if an object exists (True/False)."""
        return obj_id in self._bucket(model_name)
