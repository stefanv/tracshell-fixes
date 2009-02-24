import sys
import traceback
import xmlrpclib

def catch_errors(fn):
    """
    A decorator to catch typical xmlrpclib exceptions
    """
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except xmlrpclib.ProtocolError, e:
            print "There was a problem communicating with the server."
            print "URL: %s" % e.url
            print "Headers: %s" % e.headers
            print "Error code: %d" % e.errcode
            print "Error message: %s" % e.errmsg
            print "Please file a report with the TracShell developers."
            pass
        except xmlrpclib.Fault, e:
            print "A fault ocurred"
            print "Fault code: %d" % e.faultCode
            print "Fault string: %s" % e.faultString
            print "If you think this message is the result of an error,"
            print "please file a report with the TracShell developers."
            pass
        except:
            (type, value, trace) = sys.exc_info()
            print "SOMETHING BLEW UP: %s %s" % (type, value)
            print traceback.format_tb(trace)
    return wrapped

class Trac(object):
    """
    Provides a transparent interface to a remote Trac instance via
    XML-RPC which requires the Trac XML-RPC plugin to be installed and
    available.
    """

    def __init__(self, user, passwd, host, port, path):
        """
        Initialize a server proxy object
        
        Arguments:
        - `user`:
        - `passwd`:
        - `host`:
        - `port`:
        - `path`:
        """
        self._user = user
        self._passwd = passwd
        self._host = host
        self._port = port
        self._path = path
        self._server = self._connect()

    def _connect(self):
        """
        Return an xmlrpc.ServerProxy instance
        """
        conn_str = "http://%s:%s@%s:%s%s" % (self._user,
                                             self._passwd,
                                             self._host,
                                             self._port,
                                             self._path)
        return xmlrpclib.ServerProxy(conn_str)

    @catch_errors
    def query_tickets(self, query):
        """
        Query the Trac ticket database
        """
        multicall = xmlrpclib.MultiCall(self._server)
        for ticket in self._server.ticket.query(query):
            multicall.ticket.get(ticket)

        return [ticket for ticket in multicall()]

    @catch_errors
    def get_ticket(self, id):
        """
        Get a ticket from the Trac database
        """
        ticket = self._server.ticket.get(id)
        return ticket

    def get_ticket_changelog(self, id):
        """
        Get the comments for a ticket
        """
        changes = self._server.ticket.changeLog(id)
        return changes

    @catch_errors
    def create_ticket(self, summary, description, data):
        """
        Save a ticket to the Trac database and return the ID of the
        newly created ticket
        """
        id = self._server.ticket.create(summary,
                                        description,
                                        data)
        return id

    @catch_errors
    def update_ticket(self, id, comment, data):
        """
        Update a ticket in the Trac database
        """
        self._server.ticket.update(id, comment, data)
