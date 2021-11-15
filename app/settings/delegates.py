from app.settings.services import RewardConfigurationService, ResourceConfigurationService, \
    ResourceConfigurationUniqueService, AuditTrialFieldsListService


class RewardConfigurationDelegate:
    @staticmethod
    def create_reward_configuration(filters, user_identity):
        data = RewardConfigurationService.create_reward_configuration(filters, user_identity)
        return data

    @staticmethod
    def get_reward_configuration(user_identity):
        data = RewardConfigurationService.get_reward_configuration(user_identity)
        return data

class ResourceConfigurationDelegate:
    @staticmethod
    def get_resources_configuration_settings(parameters):
        response = ResourceConfigurationService.get_resources_configuration_settings(parameters)
        return response

    @staticmethod
    def add_resources_configuration_settings(payload):
        response = ResourceConfigurationService.add_resources_configuration_settings(payload)
        return response

    @staticmethod
    def update_resources_configuration_settings(payload, resource_id):
        response = ResourceConfigurationService.update_resources_configuration_settings(payload, resource_id)
        return response

    @staticmethod
    def delete_resources_configuration_settings(payload):
        response = ResourceConfigurationService.delete_resources_configuration_settings(payload)
        return response

class ResourceConfigurationUniqueDelegate:
    @staticmethod
    def check_resources_configuration_uniqueness(parameters):
        response = ResourceConfigurationUniqueService.check_resources_configuration_uniqueness(parameters)
        return response
        
class AuditTrialFieldsListDelegate:
    @staticmethod
    def get_audit_trial_fields_list(parameters):
        response = AuditTrialFieldsListService.get_audit_trial_fields_list(parameters)
        return response

