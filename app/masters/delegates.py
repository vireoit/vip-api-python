from app.masters.services import AdminListService, MasterEventService, MedicationImportService
from app import response


class AdminListDelegate:
    @staticmethod
    def get_admin_list(parameters):
        data = AdminListService.get_admin_list(parameters)
        return data


class MasterEventDelegate:
    @staticmethod
    def get_event_list(parameters):
        response = MasterEventService.get_event_list(parameters)
        return response

    @staticmethod
    def add_master_event(payload):
        response = MasterEventService.add_master_event(payload)
        return response

    @staticmethod
    def update_master_event(payload, event_id):
        response = MasterEventService.update_master_event(payload, event_id)
        return response

    @staticmethod
    def delete_master_event(payload):
        response = MasterEventService.delete_master_event(payload)
        return response


class MedicationImportDelegate:
    @staticmethod
    def import_medication_xlsx_file(file):
        response = MedicationImportService.import_medication_xlsx_file(file)
        return response