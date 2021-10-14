from app.masters.services import AdminListService


class AdminListDelegate:
    @staticmethod
    def get_admin_list(parameters):
        data = AdminListService.get_admin_list(parameters)
        return data
        
