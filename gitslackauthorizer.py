from errbot import BotPlugin, arg_botcmd
from adapters import GitHubAdapter, BitbucketAdapter, UserNotInOrganization


class Gitslackauthorizer(BotPlugin):
    """
    Give access to github repos
    """

    # def activate(self):
    #     """
    #     Triggers on plugin activation

    #     You should delete it if you're not using it to override any default behaviour
    #     """
    #     super(Gitslackauthorizer, self).activate()

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return {
                'GITHUB_ADMINS': ["@manvendra.singh"],
                'GITHUB_ACCESS_TOKEN': "0x****************0x",
               }

    def __notify_admins(self, message: str, frm):
        """

        :param message: Message which will be forwarder to all the members of self.config["GITHUB_ADMINS"]
        :param frm: Identifier instance which have sent the message
        :return: None
        """

        for admin in self.config["GITHUB_ADMINS"]:
            admin_identifier = self.build_identifier(admin)
            if admin_identifier != frm:
                self.send(
                    admin_identifier,
                    message
                )

    @arg_botcmd('access', type=str, choices=["pull", "push", "admin"],
                help="Access type")
    @arg_botcmd('--url', type=str, dest='url', required=True,
                help="Github/BitBucket Repository URL")
    @arg_botcmd('--username', type=str, dest='username', required=True,
                help="Github/Bitbcuket Username who needs the access")
    def gitbot_get(self, msg, access=None, url=None, username=None):
        """
        Give access to github repos to users
        """
        user_request = UserRequest(access=access, repo_url=url, username=username,
                                   issuer=msg.frm)
        self.log.debug("Plugin: Gitslackauthorizer, message: {}".format(str(user_request)))

        admin_command = "!gitbot grant {access} --url {url} --username {username}".format(
            access=user_request.access, url=user_request.repo_url, username=user_request.username
        )
        admin_message = "Requested " + str(user_request) + " Issued by {}".format(user_request.issuer)

        self.__notify_admins(admin_message+"\n"+admin_command, msg.frm)
        return "Requested " + str(user_request)

    @arg_botcmd('access', type=str, choices=["pull", "push", "admin"],
                help="Access to Grant to the User")
    @arg_botcmd('--url', type=str, dest='url', required=True,
                help="Github/BitBucket Repository URL")
    @arg_botcmd('--username', type=str, dest='username', required=True,
                help="Github/Bitbcuket Username who needs the access")
    def gitbot_grant(self, msg, access, url, username):

        user_request = UserRequest(access=access, repo_url=url, username=username, grantee=msg.frm)

        port = ExternalPort(user_request, token=self.config["GITHUB_ACCESS_TOKEN"])
        try:
            port.execute()
            admin_notification = "Granted " + str(user_request) + " Approved by admin: {}".format(user_request.grantee)
        except UserNotInOrganization:
            admin_notification = "The Git User {} is not part your organization. Access grant denied".format(
                username
            )
        self.__notify_admins(admin_notification, msg.frm)
        return "Granted" + str(user_request)


class UserRequest:
    """Represent a request raised from the end user"""
    def __init__(self, access, repo_url, username, issuer=None, grantee=None):
        self.access = access
        self.repo_url = repo_url
        self.username = username
        self.issuer = issuer
        self.grantee = grantee

    def __str__(self):
        return "{access} Access for git user {username} on repo {repo_url}.".format(
            access=self.access, username=self.username,
            repo_url=self.repo_url, issuer=self.issuer)


class ExternalPort:
    available_adapters = {
        "github": GitHubAdapter,
        "bitbucket": BitbucketAdapter
    }

    def __init__(self, user_request: UserRequest, token: str):
        self.url = user_request.repo_url
        self.access_type = user_request.access
        self.username = user_request.username
        self.adapter = self.__parse_provider()(token)

    def __parse_provider(self):
        domain_name = self.url.split("/")[2].split(".")[0]
        return self.available_adapters[domain_name]

    def execute(self):
        self.adapter.execute(self.access_type, self.url, self.username)
