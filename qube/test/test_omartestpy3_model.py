#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class Testomartestpy3Model(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_omartestpy3_model(self):
        from qube.src.models.omartestpy3 import omartestpy3
        omartestpy3_data = omartestpy3(name='testname')
        omartestpy3_data.tenantId = "23432523452345"
        omartestpy3_data.orgId = "987656789765670"
        omartestpy3_data.createdBy = "1009009009988"
        omartestpy3_data.modifiedBy = "1009009009988"
        omartestpy3_data.createDate = str(int(time.time()))
        omartestpy3_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            omartestpy3_data.save()
            self.assertIsNotNone(omartestpy3_data.mongo_id)
            omartestpy3_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
