
from app.domains.users.repo_interface import UserRepositoryInterface

class UserSerice:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo
