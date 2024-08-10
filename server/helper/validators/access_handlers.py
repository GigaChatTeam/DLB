from abc import abstractmethod

from server.helper import SQLOperator
from server.views import forms
from bcrypt import checkpw


class Special:
    @staticmethod
    @abstractmethod
    def validate_from_form(form: forms.RequestForm) -> bool:
        pass


class ValidateToken(Special):
    @staticmethod
    def validate_from_form(form: forms.RequestForm) -> bool:
        if form.headers.authorize is None:
            return False

        for token in SQLOperator.get_user_tokens(
                connection=form.sql_connection,
                client=form.headers.authorize.client):
            if checkpw(form.headers.authorize.token.encode("UTF-8"), token.encode("UTF-8")):
                return True

        return False


class Channels:
    class Meta:
        class IsChannelPublic(Special):
            @staticmethod
            def validate_from_form(form: forms.Channels.SuperPatternChannel) -> bool:
                return SQLOperator.Channels.Meta.is_channel_public(
                    connection=form.sql_connection,
                    channel_id=form.channel) or False

    class ValidateUserSelfPresence(Special):
        @staticmethod
        def validate_from_form(form: forms.Channels.SuperPatternChannel) -> bool:
            return SQLOperator.Channels.Users.Permissions.validate_presence(
                connection=form.sql_connection,
                user=form.headers.authorize.client,
                channel=form.channel)
