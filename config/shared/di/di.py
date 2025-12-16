from dependency_injector import containers, providers


from log.models.role_model import Role
from log.repositories.role_repositories import RoleRepository
from log.services.role_services import RoleService


class Container(containers.DeclarativeContainer):
    role_model = providers.Object(Role)
    role_repository = providers.Singleton(RoleRepository, model=role_model)
    role_service = providers.Singleton(RoleService, repository=role_repository)


container = Container()
