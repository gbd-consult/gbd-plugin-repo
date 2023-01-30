from flask_xmlrpcre.xmlrpcre import XMLRPCHandler
from flask_login import login_required


class HTTPAuthXMLRPCHandler(XMLRPCHandler):
    @login_required
    def handle_request(self):
        return XMLRPCHandler.handle_request(self)


class RPCError(Exception):
    pass