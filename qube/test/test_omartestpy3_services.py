#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['OMARTESTPY3_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['OMARTESTPY3_MONGOALCHEMY_SERVER'] = ''
    os.environ['OMARTESTPY3_MONGOALCHEMY_PORT'] = ''
    os.environ['OMARTESTPY3_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.omartestpy3 import omartestpy3
    from qube.src.services.omartestpy3service import omartestpy3Service
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, omartestpy3ServiceError


class Testomartestpy3Service(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.omartestpy3Service = omartestpy3Service(context)
        self.omartestpy3_api_model = self.createTestModelData()
        self.omartestpy3_data = self.setupDatabaseRecords(self.omartestpy3_api_model)
        self.omartestpy3_someoneelses = \
            self.setupDatabaseRecords(self.omartestpy3_api_model)
        self.omartestpy3_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.omartestpy3_someoneelses.save()
        self.omartestpy3_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.omartestpy3_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.omartestpy3_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, omartestpy3_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            omartestpy3_data = omartestpy3(name='test_record')
            for key in omartestpy3_api_model:
                omartestpy3_data.__setattr__(key, omartestpy3_api_model[key])

            omartestpy3_data.description = 'my short description'
            omartestpy3_data.tenantId = "23432523452345"
            omartestpy3_data.orgId = "987656789765670"
            omartestpy3_data.createdBy = "1009009009988"
            omartestpy3_data.modifiedBy = "1009009009988"
            omartestpy3_data.createDate = str(int(time.time()))
            omartestpy3_data.modifiedDate = str(int(time.time()))
            omartestpy3_data.save()
            return omartestpy3_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_omartestpy3(self, *args, **kwargs):
        result = self.omartestpy3Service.save(self.omartestpy3_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.omartestpy3_api_model['name'])
        omartestpy3.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_omartestpy3(self, *args, **kwargs):
        self.omartestpy3_api_model['name'] = 'modified for put'
        id_to_find = str(self.omartestpy3_data.mongo_id)
        result = self.omartestpy3Service.update(
            self.omartestpy3_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.omartestpy3_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_omartestpy3_description(self, *args, **kwargs):
        self.omartestpy3_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.omartestpy3_data.mongo_id)
        result = self.omartestpy3Service.update(
            self.omartestpy3_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.omartestpy3_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy3_item(self, *args, **kwargs):
        id_to_find = str(self.omartestpy3_data.mongo_id)
        result = self.omartestpy3Service.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy3_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(omartestpy3ServiceError):
            self.omartestpy3Service.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy3_list(self, *args, **kwargs):
        result_collection = self.omartestpy3Service.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.omartestpy3_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy3_data.mongo_id)
        with self.assertRaises(omartestpy3ServiceError) as ex:
            self.omartestpy3Service.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy3_data.mongo_id)
        self.omartestpy3Service.auth_context.is_system_user = True
        self.omartestpy3Service.delete(id_to_delete)
        with self.assertRaises(omartestpy3ServiceError) as ex:
            self.omartestpy3Service.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.omartestpy3Service.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy3_someoneelses.mongo_id)
        with self.assertRaises(omartestpy3ServiceError):
            self.omartestpy3Service.delete(id_to_delete)
