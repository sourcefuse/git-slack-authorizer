from github import Github
from abc import ABCMeta, abstractmethod


class InvalidAccessType(Exception):
    pass


class UserNotInOrganization(Exception):
    pass


class BaseAdapter(metaclass=ABCMeta):
    """Base Class for Building the Adapters"""

    @property
    @abstractmethod
    def access_types(self):
        """Return a list of access types supported by provider"""

    @abstractmethod
    def is_valid_access_type(self, access_type):
        """Check if requested access type is valid or not.
        if not then raises InvalidAccessType"""

    @abstractmethod
    def grant_access(self, access_type: str, repo_url: str, username: str):
        """
        :param access_type: type of access to grant to user, default is push
        :param repo_url: URL for the repository
        :param username: username for the user who needs access
        :return:
        """

    @abstractmethod
    def is_user_in_organization(self, organization_name: str, username: str):
        """
        :param organization_name:  Name of the organization
        :param username: Name of the user
        :return: boolean
        """

    @abstractmethod
    def execute(self, access_type: str, repo_url: str, username: str):
        """

        :param access_type: type of access to grant to user, default is push
        :param repo_url: URL for the repository
        :param username: username for the user who needs access
        :return:
        """


class GitHubAdapter(BaseAdapter):
    """Main Class implementing the access control for Github"""
    __ACCESS_TYPES = ('push', 'pull', 'admin')

    def __init__(self, token):
        self.gh = Github(token)

    @property
    def access_types(self):
        return list(self.__ACCESS_TYPES)

    def is_valid_access_type(self, access_type):
        return access_type in self.access_types

    def grant_access(self, access_type: str, repo_name: str, username: str):
        repo = self.gh.get_repo(repo_name)
        repo.add_to_collaborators(username, permission=access_type)

    @staticmethod
    def parse_url(url: str):
        """Parse URL and return string contaning the organization name and repo name
        Ex.  https://github.com/sourcefuse/terraform-test -> sourcefuse/terraform-test"""
        return '/'.join(url.split("/")[-2:])

    def is_user_in_organization(self, organization_name: str, username: str):
        user = self.gh.get_user(username)
        organization = self.gh.get_organization(organization_name)
        return organization.has_in_members(user)

    def execute(self, access_type: str, repo_url: str, username: str):
        if self.is_valid_access_type(access_type):
            organization, repo = self.parse_url(repo_url).split("/")

            if self.is_user_in_organization(organization, username):
                self.grant_access(access_type, self.parse_url(repo_url), username)
            else:
                raise UserNotInOrganization("User {} is not part of organization {}".format(
                    username, organization
                ))
        else:
            raise InvalidAccessType("Access Type: {} is not supported by github".format(
                access_type
            ))


class BitbucketAdapter(BaseAdapter):

    def __init__(self):
        pass

    def is_valid_access_type(self, access_type):
        pass

    def access_types(self):
        pass

    def grant_access(self, access_type: str, repo_url: str, username: str):
        pass

    def is_user_in_organization(self, organization_name: str, username: str):
        pass

    def execute(self, access_type: str, repo_url: str, username: str):
        pass