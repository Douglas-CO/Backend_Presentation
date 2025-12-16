class ReadRepositoryMixin:
    def find_all(self):
        return self.model.objects.all()  # return queryset

    def find_all_by_attrs(self, params: dict):
        return self.model.objects.filter(**params)  # return queryset

    def find_all_by_pk_list(self, pks: list):
        return self.model.objects.filter(pk__in=pks)  # return queryset

    def find_all_by_pk_list_and_attrs(self, pks: list, params: dict):
        return self.model.objects.filter(pk__in=pks, **params)

    def find_one(self, pk):
        return self.model.objects.filter(pk=pk).first()  # return instance

    def find_one_qs(self, pk):
        return self.model.objects.filter(pk=pk)  # return queryset

    def find_one_active(self, pk) -> object | None:
        instance = self.model.objects.filter(pk=pk).first()
        if instance and hasattr(instance, 'state'):
            if instance.state:
                return instance
            return None
        return instance

    def find_one_by_uuid(self, uuid) -> object | None:
        return self.model.objects.filter(uuid=uuid).first()

    def find_one_by_uuid_qs(self, uuid):
        return self.model.objects.filter(uuid=uuid)  # return queryset

    def find_one_by_attr(self, attr: str, value) -> object | None:
        return self.model.objects.filter(**{attr: value}).first()

    def find_one_by_attr_qs(self, attr: str, value):
        return self.model.objects.filter(**{attr: value})  # return queryset

    def find_one_by_attrs(self, params: dict) -> object | None:
        # {attr: value, attr2: value2, ...}
        return self.model.objects.filter(**params).first()

    def find_one_by_attrs_qs(self, params: dict):
        # {attr: value, attr2: value2, ...}
        return self.model.objects.filter(**params)  # return queryset

    def find_last(self):
        return self.model.objects.last()


class CreateRepositoryMixin:
    def create(self, data) -> object:
        return self.model.objects.create(**data)


class UpdateRepositoryMixin:
    # pre_instance= None

    def update(self, instance_id, data) -> object:
        instance = self.model.objects.get(pk=instance_id)
        # self.pre_instance = instance.__dict__.copy()  # Store pre-update state
        # print('=====', self.pre_instance, '=====')
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class DeleteRepositoryMixin:
    def delete(self, instance_id) -> bool:
        instance = self.model.objects.filter(pk=instance_id).first()
        if not instance:
            return False
        instance.delete()
        return True
