"""

Example Code:
from smartertesting.SNIntegration import get_update_set_dict
from smartertesting.SNIntegration import get_objects_from_update_set
from smartertesting.SNIntegration import SNInstance
from smartertesting.SNIntegration import test_paths
import json

test_dict = get_update_set_dict(test_paths[2])
objects = get_objects_from_update_set(test_dict)

sn_object = objects[0]
payload_dict = get_payload_dict_from_object(sn_object)

# print(json.dumps(test_dict, indent=4))
"""

import xmltodict
import requests
from requests.exceptions import HTTPError
import os


class SNInstance(object):
    """docstring for SNInstance"""
    def __init__(self, **kwargs):
        super(SNInstance, self).__init__()
        self.session = self.get_session(**kwargs)
        self.instance = self.get_instance(**kwargs)
        self.headers = {"Content-Type":"application/json","Accept":"application/json"}

        self.current_suite = ""

    def get_instance(self, **kwargs):
        """"""
        instance = kwargs.pop("instance", False)
        if(instance):
            return instance

        env_variable = "SN_INSTANCE"
        instance = os.environ.get(env_variable, False)
        if(instance):
            return instance

        raise RuntimeError(f'Environment Variable not found: {env_variable}')

    def get_session(self, **kwargs):
        """"""
        session = kwargs.pop("session", False)
        if(session):
            return session

        session = requests.Session()
        session.auth = self.get_auth()
        return session

    def get_auth(self):
        """"""
        env_variable = "SN_USERNAME"
        username = os.environ.get(env_variable, False)
        if(not username):
            raise RuntimeError(f'Environment Variable not found: {env_variable}')

        env_variable = "SN_PASSWORD"
        password = os.environ.get(env_variable, False)
        if(not password):
            raise RuntimeError(f'Environment Variable not found: {env_variable}')

        return (username, password)

    def get_records(self, table, encoded_query):
        """
            Base method to GET records from a servicenow instance

        """
        url = f'https://{self.instance}.service-now.com/api/now/table/{table}'
        url = url + f'?sysparm_query={encoded_query}'

        response = self.session.get(url, headers=self.headers)

        if(not response.ok):
            raise requests.HTTPError(response=response)

        return response.json()


    def create_record(self, table, payload):
        """
            Base method for creating records in a servicenow instance
        """
        url = f'https://{self.instance}.service-now.com/api/now/table/{table}'
        response = self.session.post(url, headers=self.headers, json=payload)

        if(response.status_code==201):
            return response.json()["result"]

        raise HTTPError(response)


    def get_tests(self, encoded_query):
        """"""
        table = "sys_atf_test"
        return self.get_records(table, encoded_query)


    def create_test_suite(self, name, **kwargs):
        """
            creates a test suite record in a servicenow instance and stores the id in the SNInstance's current_suite variable
        """
        table = "sys_atf_test_suite"

        description = kwargs.pop("description","")

        payload = {
        	"name":name,
        	"description":description,
        	"active":"True",}

        json_data = self.create_record(table, payload)

        self.current_suite = json_data["sys_id"]

        return json_data


    def add_test_to_suite(self, test_id, **kwargs):
        """"""
        # test_id = "052e804c53b0220002c6435723dc34d1"
        # override current suite if a test suite is passed in.
        test_suite = kwargs.pop("test_suite", self.current_suite)

        if(not test_suite):
            raise RuntimeError("No test suite found to add test to")

        table_name = "sys_atf_test_suite_test"

        add_test_payload = {
        	"test":test_id,
        	"test_suite":test_suite,
        	"order":"100",}

        json_data = self.create_record(table_name, add_test_payload)

        return json_data






test_paths = [
    'smartertesting/testXML/sys_remote_update_set.xml',
    'smartertesting/testXML/sys_remote_update_set2.xml',
    'smartertesting/testXML/sys_remote_update_set3.xml']



def get_update_set_dict(filepath):
    """Opens the update set xml file and returns a dictionary of its contents"""
    with open(filepath) as file:
        update_set_dict = xmltodict.parse(file.read())
    return update_set_dict


def get_objects_from_update_set(dictionary):
    """using the update set path, returns a list of updates as dictionary or a dictionary if only one"""
    update_set_path = ["unload", "sys_update_xml"]

    for step in update_set_path:
        dictionary = dictionary[step]

    return dictionary

def get_payload_dict_from_object(sn_object):
    """returns the xmlpayload of a sn object as a dictionary object"""
    xml_string = sn_object["payload"]

    payload_dict = xmltodict.parse(xml_string)

    return payload_dict

