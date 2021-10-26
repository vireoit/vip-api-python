from app.settings.services import RewardConfigurationService


class RewardConfigurationDelegate:
    @staticmethod
    def create_reward_configuration(filters, user_identity):
        data = RewardConfigurationService.create_reward_configuration(filters, user_identity)
        return data

    @staticmethod
    def get_reward_configuration(user_identity):
        data = RewardConfigurationService.get_reward_configuration(user_identity)
        return data

