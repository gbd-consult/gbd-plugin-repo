from flask_login import login_required
from flask_xmlrpcre.xmlrpcre import XMLRPCHandler


class HTTPAuthXMLRPCHandler(XMLRPCHandler):
    """XMLRPCHandler class with HTTP Auth enabled."""

    @login_required
    def handle_request(self):
        """Requires Login for all requests."""
        return XMLRPCHandler.handle_request(self)


class RPCError(Exception):
    """Exception to throw when the RPC failes."""

    pass
