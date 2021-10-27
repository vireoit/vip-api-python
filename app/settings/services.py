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

class ResourceConfigurationService:
    @staticmethod
    def get_resources_configuration_settings(parameters):
        sorted_by = parameters.get('order')
        limit_by = parameters.get('limit')
        search_by = parameters.get('search')
        order_by = -1 if sorted_by == "desc" else 1
        page = parameters.get("page")
        total_count = mongo_db.db.Resources.find({}).count()
        if search_by is not None:
            mongo_db.db.Resources.create_index([('resource_title', 'text')])
            query_data = mongo_db.db.Resources.find({"$text": {"$search": search_by}}).skip((page-1) * limit_by).limit(limit_by)
        else:
            query_data = mongo_db.db.Resources.find().skip((page-1) * limit_by).limit(limit_by).sort("created_on", order_by).limit(limit_by)

        alldata = mongo_db.db.Resources.find().skip((page-1) * limit_by).limit(limit_by)
        bs = dumps(alldata, json_options=RELAXED_JSON_OPTIONS)
        resource_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            resource_list.append(val)
        response_data = {
            'resource_list': resource_list,
            'total_count': total_count
        }
        return response_data

    @staticmethod
    def add_resources_configuration_settings(payload):
        try:
            payload['created_on'] = datetime.now().replace(microsecond=0).isoformat()
            payload['updated_on'] = datetime.now().replace(microsecond=0).isoformat()
            payload['is_active'] = True
            mongo_db.db.Resources.insert_one(payload)
            return True
        except Exception as err:
            print(err)

    @staticmethod
    def update_resources_configuration_settings(payload, resource_id):
        try:
            payload['updated_on'] = datetime.now().replace(microsecond=0).isoformat()
            mongo_db.db.Resources.find_one_and_update({'_id': ObjectId(resource_id)},  {'$set': payload}) 
            return True
        except Exception as err:
            print(err)

    @staticmethod
    def delete_resources_configuration_settings(payload):
        try:
            resource_id = payload['id']
            mongo_db.db.Resources.remove({"_id": ObjectId(resource_id)})
            return True
        except Exception as err:
            print(err)

class ResourceConfigurationUniqueService:
    @staticmethod
    def check_resources_configuration_uniqueness(parameters):
        query_data = mongo_db.db.Resources.find_one({"resource_title": parameters.get('resource_title')})
        if query_data:
            return {'is_unique': False}
        return {'is_unique': True}
