import json
from seaserv import seafile_api, ccnet_api
from django.core.urlresolvers import reverse
from tests.common.utils import randstring
from seahub.test_utils import BaseTestCase

class ReposBatchViewTest(BaseTestCase):

    def create_new_repo(self, username):
        new_repo_id = seafile_api.create_repo(name=randstring(10),
                desc='', username=username, passwd=None)

        return new_repo_id

    def setUp(self):
        self.user_name = self.user.username
        self.admin_name = self.admin.username

        self.repo_id = self.repo.id
        self.group_id = self.group.id

        self.url = reverse('api-v2.1-repos-batch')

    def tearDown(self):
        self.remove_repo()
        self.remove_group()

    def test_can_share_repos_to_user(self):
        tmp_repo_id = self.create_new_repo(self.user_name)

        self.login_as(self.user)

        data = {
            'operation': 'share',
            'share_type': 'user',
            'username': self.admin_name,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert len(json_resp['success']) == 1
        assert len(json_resp['failed']) == 0

        # share repo again will failed
        data = {
            'operation': 'share',
            'share_type': 'user',
            'username': self.admin_name,
            'repo_id': [self.repo_id, tmp_repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert len(json_resp['success']) == 1
        assert len(json_resp['failed']) == 1
        assert self.repo_id in json_resp['failed'][0]['repo_id']

        self.remove_repo(tmp_repo_id)

    def test_can_share_repos_to_group(self):
        tmp_repo_id = self.create_new_repo(self.user_name)

        self.login_as(self.user)

        data = {
            'operation': 'share',
            'share_type': 'group',
            'group_id': self.group_id,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert len(json_resp['success']) == 1
        assert len(json_resp['failed']) == 0

        # share repo again will failed
        data = {
            'operation': 'share',
            'share_type': 'group',
            'group_id': self.group_id,
            'repo_id': [self.repo_id, tmp_repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert len(json_resp['success']) == 1
        assert len(json_resp['failed']) == 1
        assert self.repo_id in json_resp['failed'][0]['repo_id']

        self.remove_repo(tmp_repo_id)

    def test_share_with_invalid_operation(self):
        self.login_as(self.user)

        data = {
            'operation': 'invalid_operation',
            'share_type': 'user',
            'username': self.admin_name,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(400, resp.status_code)

        data = {
            'operation': 'invalid_operation',
            'share_type': 'group',
            'group_id': self.group_id,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(400, resp.status_code)

    def test_share_with_invalid_share_type(self):
        self.login_as(self.user)

        data = {
            'operation': 'share',
            'share_type': 'invalid_share_type',
            'username': self.admin_name,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(400, resp.status_code)

        data = {
            'operation': 'share',
            'share_type': 'invalid_share_type',
            'group_id': self.group_id,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(400, resp.status_code)

    def test_share_with_invalid_permisson(self):
        self.login_as(self.user)

        data = {
            'operation': 'share',
            'share_type': 'user',
            'permission': 'invalid_permission',
            'username': self.admin_name,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(400, resp.status_code)

        data = {
            'operation': 'share',
            'share_type': 'group',
            'permission': 'invalid_permission',
            'group_id': self.group_id,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(400, resp.status_code)

    def test_share_with_invalid_user(self):
        self.login_as(self.user)

        data = {
            'operation': 'share',
            'share_type': 'user',
            'username': 'invalid@user.com',
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(404, resp.status_code)

    def test_share_with_not_exist_group(self):
        self.login_as(self.user)

        data = {
            'operation': 'share',
            'share_type': 'group',
            'group_id': -1,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(404, resp.status_code)

    def test_share_with_not_group_member(self):
        tmp_group_id = ccnet_api.create_group(randstring(10), self.admin_name)

        self.login_as(self.user)

        data = {
            'operation': 'share',
            'share_type': 'group',
            'group_id': tmp_group_id,
            'repo_id': [self.repo_id]
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(403, resp.status_code)


class ReposBatchCreateDirViewTest(BaseTestCase):

    def setUp(self):
        self.user_name = self.user.username
        self.admin_name = self.admin.username
        self.repo_id = self.repo.id
        self.url = reverse('api-v2.1-repos-batch-create-dir')

    def tearDown(self):
        self.remove_repo()
        self.remove_group()

    def get_random_path(self):
        return '/%s/%s/%s/' % (randstring(2), \
                randstring(2), randstring(2))

    def test_create_dir(self):

        path_1 = self.get_random_path()
        path_2 = self.get_random_path()
        path_3 = self.get_random_path()

        self.login_as(self.user)

        data = {
            'repo_id': self.repo_id,
            'path': [path_1, path_2, path_3],
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        assert len(json_resp['success']) == 3
        assert len(json_resp['failed']) == 0

        assert seafile_api.get_dir_id_by_path(self.repo_id,
                path_1) is not None
        assert seafile_api.get_dir_id_by_path(self.repo_id,
                path_2) is not None
        assert seafile_api.get_dir_id_by_path(self.repo_id,
                path_3) is not None

    def test_create_dir_with_invalid_repo_permission(self):

        # admin has NO permission for user's repo
        self.login_as(self.admin)

        data = {
            'repo_id': self.repo_id,
            'path': 'path',
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(403, resp.status_code)
