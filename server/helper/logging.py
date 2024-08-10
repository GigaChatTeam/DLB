from psycopg2 import Error as DBSQLError

from server.helper.CHOperator import log_query
from server.views import forms
from server.views.exceptions import AccessDenied


def log_request(handler):
    def wrapper(form: forms.RequestForm):
        success: bool = True
        error: bool = False
        try:
            return handler(form)
        except DBSQLError as db_error:
            success = False
            error = True

            raise db_error
        except AccessDenied as exception:
            success = False
            error = False

            raise exception
        finally:
            if form.headers.authorize is None:
                client = 0
            else:
                client = form.headers.authorize.client
            log_query(
                user=client,
                agent=form.headers.agent,
                success=success,
                error=error,
                addr=form.headers.addr
            )

    return wrapper