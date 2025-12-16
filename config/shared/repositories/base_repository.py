from config.shared.repositories.base_mixin_repository import ReadRepositoryMixin, CreateRepositoryMixin, UpdateRepositoryMixin, DeleteRepositoryMixin


class BaseRepositoryMixin(ReadRepositoryMixin, CreateRepositoryMixin, UpdateRepositoryMixin):
    # DI: inject the model
    def __init__(self, model):
        self.model = model

class BaseRepositoryAllMixin(ReadRepositoryMixin, CreateRepositoryMixin, UpdateRepositoryMixin, DeleteRepositoryMixin):
    # DI: inject the model
    def __init__(self, model):
        self.model = model



# ### OLD: without mixins -----------------------
class BaseRepository:
    # constructor: inject the model
    def __init__(self, model):
        self.model = model

    def find_all(self):
        return self.model.objects.all() # return queryset

    def find_one(self, pk) -> object | None:
        return self.model.objects.filter(pk=pk).first()
    def find_one_by_uuid(self, uuid) -> object | None:
        return self.model.objects.filter(uuid=uuid).first()
    def find_one_by_attr(self, attr: str, value) -> object | None:
        return self.model.objects.filter(**{attr: value}).first()
    def find_one_by_attrs(self, params: dict):
        # {attr: value, attr2: value2, ...}
        return self.model.objects.filter(**params).first()
    def find_last(self):
        return self.model.objects.last()

    def create(self, data) -> object:
        return self.model.objects.create(**data)

    def update(self, instance_id, data) -> object:
        instance = self.model.objects.get(pk=instance_id)
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    # def delete(self, instance_id) -> bool:
    #     instance = self.model.objects.filter(pk=instance_id).first()
    #     if not instance:
    #         return False
    #     instance.delete()
    #     return True
