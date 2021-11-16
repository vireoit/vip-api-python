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
            query_data = mongo_db.db.Resources.find({"resource_title": {"$regex": "{0}".format(search_by), '$options' : 'i'}}).skip((page-1) * limit_by).limit(limit_by)
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
        if parameters.get('resource_title'):
            resource_query_data = mongo_db.db.Resources.find_one({"resource_title": parameters.get('resource_title')})
            if resource_query_data:
                return {'is_unique': False, 'key': 'Resource title'}
            else:
                return {'is_unique': True, 'key': 'Resource title'}
        if parameters.get('link'):
            link_query_data = mongo_db.db.Resources.find_one({"link": parameters.get('link')})
            if link_query_data:
                return {'is_unique': False, 'key': 'Link'}
            else:
                return {'is_unique': True, 'key': 'Link'}


class AuditLogListService:
    @staticmethod
    def list_audit_log(filters, parameters, user_identity):
        limit_by = parameters.get('limit')
        page = parameters.get("page")
        order_by = -1
        if 'from_date' in filters and filters['from_date']:
            start_date = datetime.strptime(str(filters['from_date']) + " 00:00", "%m-%d-%Y %H:%M")
        if 'to_date' in filters and filters['to_date']:
            end_date = datetime.strptime(str(filters['to_date']) + " 23:59", "%m-%d-%Y %H:%M")
        if not filters:
            total_count = mongo_db.db.AuditLog.find({}).count()

            query_data = list(
                mongo_db.db.AuditLog.find().skip((page - 1) * limit_by).limit(limit_by).sort("created_at",
                                                                                             order_by).limit(
                    limit_by))
        else:
            filter_items = {
                "action": {"$in": tuple(filters['action'])} if filters['action'] else [],
                "action_type": {"$in": tuple(filters['action_type'])} if filters['action_type'] else [],
                "actor._id": filters['actor'] if filters['actor'] else "",
                "module": {"$in": tuple(filters['module'])} if filters['module'] else [],
                "event": {"$in": tuple(filters['event'])} if filters['event'] else [],
                "created_at": {"$lte": end_date, '$gt': start_date} if filters['from_date'] and filters['to_date'] else ""

            }
            new_dict = dict([(vkey, vdata) for vkey, vdata in filter_items.items() if (vdata)])
            total_count = mongo_db.db.AuditLog.find(new_dict).count()
            query_data = list(mongo_db.db.AuditLog.find(new_dict). \
                              skip((page - 1) * limit_by).limit(limit_by).sort("created_at", order_by).limit(limit_by))

        bs = dumps(query_data, json_options=RELAXED_JSON_OPTIONS)
        resource_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            resource_list.append(val)
        response_data = {
            'audit_log': resource_list,
            'total_count': total_count
        }
        return response_data

class AuditTrialFieldsListService:
    @staticmethod
    def get_audit_trial_fields_list(parameters):
        field = parameters.get('field')
        total_list = list(mongo_db.db.AuditLog.find({}))
        action_list = []
        event_list = []
        action_type_list = []
        module_list = []
        response_list = []
        if field == "action":
            for val in total_list:
                action_list.append(val['action'])
            for data in list(set(action_list)):
                response_list.append({'key': data})
            return {"action": response_list}
        elif field == "event":
            for val in total_list:
                event_list.append(val['event'])
            for data in list(set(event_list)):
                response_list.append({'key': data})
            return {"event": response_list}
        elif field == "action_type":
            for val in total_list:
                action_type_list.append(val['action_type'])
            for data in list(set(action_type_list)):
                response_list.append({'key': data})
            return {"action_type": response_list}
        elif field == "module":
            for val in total_list:
                module_list.append(val['module'])
            for data in list(set(module_list)):
                response_list.append({'key': data})
            return {"module": response_list}


