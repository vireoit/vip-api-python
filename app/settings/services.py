from app import ma, response, mongo_db
from app.utils.mongo_encoder import format_cursor_obj

import json

from datetime import datetime, timedelta, date

from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS


class RewardConfigurationService:
    @staticmethod
    def create_reward_configuration(data, user_identity):
        data['AddedOn'] = datetime.utcnow()
        data['updated_on'] = datetime.utcnow()
        data['IsActive'] = True
        old_rewards = mongo_db.db.Rewards.find_one({'IsActive': True})
        if old_rewards:
            data['AddedOn'] = old_rewards['AddedOn']
            mongo_db.db.Rewards.find_one_and_update({'_id': ObjectId(old_rewards['_id'])}, {'$set': data})
        else:
            create_data = mongo_db.db.Rewards.insert_one(data)

    @staticmethod
    def get_reward_configuration(user_identity):
        rewards = mongo_db.db.Rewards.find_one({'IsActive': True})
        bs = dumps(rewards, json_options=RELAXED_JSON_OPTIONS)

        return format_cursor_obj(json.loads(bs))