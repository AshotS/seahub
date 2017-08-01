# Copyright (c) 2012-2016 Seafile Ltd.

from django.db import models


class SharePermissionManager(models.Manager):
    def is_admin_users(self, repo_id, username):
        can_share_list = super(SharePermissionManager, self).filter(
            repo_id=repo_id, permission='admin', share_to=username
        )
        if len(can_share_list>0):
            return True
        else:
            return False

    def get_admin_users(self, repo_id):
        can_share_list = super(SharePermissionManager, self).filter(
            repo_id=repo_id, permission='admin'
        )
        can_share_user_list = [e.share_to for e in can_share_list]
        return can_share_user_list

    def get_share_records(self, repo_id, share_from, share_to):
        can_share_list = super(SharePermissionManager, self).filter(
            repo_id=repo_id, share_from=share_from, share_to=share_to
        )
        can_share_user_list = [e.share_from for e in can_share_list]
        return can_share_user_list


    def get_shared_repos_share_from_by_shared(self, username):
        shared_repos = super(SharePermissionManager, self).filter(
            share_to=username, permission='admin'
        )
        res_shared_repos = {}
        for e in shared_repos:
            res_shared_repos[e.repo_id] = e.share_from
        return res_shared_repos

    def get_admin_users_by_owner(self, repo_id, username):
        shared_repos = super(SharePermissionManager, self).filter(
            repo_id=repo_id, share_from=username, permission='admin'
        )
        shared_repos = [e.share_to for e in shared_repos]
        return shared_repos

    def create_share_permission(self, repo_id, share_from, username, permission):
        self.model(repo_id=repo_id, share_from=share_from, share_to=username, 
                    permission=permission).save()

    def delete_shared_admin_repos(self, repo_id, share_from, share_to):
            super(SharePermissionManager, self).filter(repo_id=repo_id, 
                                                       share_from=share_from, 
                                                       share_to=share_to).delete()

    def update_share_permission(self, repo_id, share_from, share_to, permission):
        super(SharePermissionManager, self).filter(repo_id=repo_id, 
                                                  share_from=share_from, 
                                                  share_to=share_to).delete()
        self.create_share_permission(repo_id, share_from, share_to, permission)


class SharePermission(models.Model):
    repo_id = models.CharField(max_length=36, db_index=True)
    share_from = models.CharField(max_length=255, db_index=True)
    share_to = models.CharField(max_length=255, db_index=True)
    permission = models.CharField(max_length=30)
    objects = SharePermissionManager()
