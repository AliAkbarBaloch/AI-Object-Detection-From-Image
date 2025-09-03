import os
import importlib
import unittest
from types import SimpleNamespace
from unittest.mock import patch

VALID_OID = '507f1f77bcf86cd799439011'


def reload_db_module():
    import models.db as db
    return importlib.reload(db)


class DbModuleTests(unittest.TestCase):
    def test_ci_dummy_behavior(self):
        with patch.dict(os.environ, {"CI": "true"}, clear=False):
            db = reload_db_module()
            # Module-level objects in CI
            self.assertIsNone(db.client)
            self.assertIsNone(db.db)
            self.assertIsNone(db.results_collection)
            self.assertIsNone(db.users_collection)

            # Functions should return CI dummies
            self.assertEqual(db.save_result('p', 't', 1, user_id='u'), "ci-dummy-id")
            self.assertIsNone(db.update_correction('rid', 2))
            self.assertIsNone(db.get_result('rid'))
            self.assertIsNone(db.get_user_by_email('x@example.com'))
            self.assertEqual(db.create_user('x@example.com', 'pass'), "ci-user-id")
            self.assertIsNone(db.verify_user('x@example.com', 'pass'))
            self.assertIsNone(db.get_password_for_email('x@example.com'))
            self.assertEqual(db.get_results_for_user('u'), [])

    def test_non_ci_initialization_and_calls(self):
        # Fake PyMongo stack
        class FakeCursor:
            def __init__(self, items):
                self._items = list(items)
            def sort(self, *args, **kwargs):
                return self
            def limit(self, *args, **kwargs):
                return self
            def __iter__(self):
                return iter(self._items)

        class FakeCollection:
            def __init__(self, name):
                self.name = name
            def insert_one(self, doc):
                return SimpleNamespace(inserted_id=VALID_OID)
            def update_one(self, flt, update):
                return SimpleNamespace(modified_count=1)
            def find_one(self, flt):
                if self.name == 'users':
                    # Simulate existing user only for verify (email+password)
                    # or for a known existing email. Otherwise, no existing user.
                    email = flt.get('email')
                    if 'password' in flt and email:
                        return {'_id': 'u1', 'email': email, 'password': flt['password']}
                    if email == 'user@example.com':
                        return {'_id': 'u1', 'email': email, 'password': 'pass123'}
                    return None
                return {'_id': VALID_OID, 'user_id': 'u'}
            def find(self, flt):
                return FakeCursor([{'_id': 'r1', 'user_id': flt.get('user_id')}, {'_id': 'r2', 'user_id': flt.get('user_id')}])

        class FakeDB:
            def __init__(self):
                self._users = FakeCollection('users')
                self._results = FakeCollection('results')
            def __getitem__(self, name):
                # Return a collection when indexing by collection name
                if name == 'results':
                    return self._results
                if name == 'users':
                    return self._users
                # Return self for DB name access (client[DB_NAME])
                return self
            def get_collection(self, name):
                return self._users if name == 'users' else self._results
            @property
            def results(self):
                return self._results

        class FakeClient:
            def __getitem__(self, name):
                return FakeDB()

        with patch.dict(os.environ, {"CI": "false"}, clear=False), \
             patch('pymongo.MongoClient', return_value=FakeClient()):
            db = reload_db_module()
            # Ensure collections are set
            self.assertIsNotNone(db.results_collection)
            self.assertIsNotNone(db.users_collection)

            rid = db.save_result('/tmp/img.png', 'cat', 2, user_id='u')
            self.assertEqual(rid, VALID_OID)
            upd = db.update_correction(rid, 3)
            self.assertEqual(getattr(upd, 'modified_count', 1), 1)
            r = db.get_result(rid)
            self.assertIn('_id', r)
            self.assertIsNotNone(db.get_user_by_email('user@example.com'))
            uid = db.create_user('new@example.com', 'pass123')
            # In this fake, we return inserted_id='oid123'
            self.assertEqual(uid, VALID_OID)
            self.assertIsNotNone(db.verify_user('user@example.com', 'pass123'))
            self.assertEqual(db.get_password_for_email('user@example.com'), 'pass123')
            res = db.get_results_for_user('u')
            self.assertTrue(len(res) >= 1)


if __name__ == '__main__':
    unittest.main()
