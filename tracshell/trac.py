import os, sys
import cmd
import xmlrpclib

VERSION = 0.1

class TracShell(cmd.Cmd):
    """
    TracShell is a shell interface to a Trac instance.
    
    It uses and XML-RPC interface to Trac provided by:

        http://trac-hacks.org/wiki/XmlRpcPlugin#DownloadandSource
    """

    def __init__(self, username, password, host, port=80, rpc_path='/login/xmlrpc'):
        """
        Initialize the XML-RPC interface to a Trac instance
        
        Arguments:
        - `username`: the user to authenticate as
        - `password`: a valid password
        - `host`: the host name serving the Trac instance
        - `port`: defaults to 80
        - `rpc_path`: the path to the XML-RPC interface of the Trac interface
        """
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._rpc_path = rpc_path
        self._server = self._setup()

        # set up shell options
        cmd.Cmd.__init__(self)
        self.prompt = "tint->> "
        self.ruler = '-'
        self.intro = "Welcome to Tint!\nType `help` for a list of commands"

    def _setup(self):
        """
        Return an xmlrpc.ServerProxy instance
        """
        conn_str = "http://%s:%s@%s:%s%s" % (self._username,
                                             self._password,
                                             self._host,
                                             self._port,
                                             self._rpc_path)
        return xmlrpclib.ServerProxy(conn_str)

    def do_query(self, query):
        """
        Query for tickets in Trac

        Arguments:
        - `query`: A Trac query string (see `help queries` for more info)
        """
        try:
            multicall = xmlrpclib.MultiCall(self._server)
            for ticket in self._server.ticket.query(query):
                multicall.ticket.get(ticket)

            for ticket in multicall():
                (id, date, last_mod, data) = ticket
                print "%5s: [%s] %s" % (id,
                                        data['status'].center(8),
                                        data['summary'])
        except Exception, e:
            if hasattr(e, 'faultString'):
                print e.faultString
            else:
                print "I don't understand. Try `help query`"
            pass

    def do_view(self, ticket_id):
        """
        View a specific ticket in trac

        Arguments:
        - `ticket_id`: An integer id of the ticket to view
        """
        try:
            (id, created, last_mod, data) = self._server.ticket.get(int(ticket_id))
            data['created'] = created
            data['last_modified'] = last_mod
            print "Details for Ticket: %s" % id
            print " "
            for k, v in data.iteritems():
                print "%15s: %s" % (k, v)
        except Exception, e:
            if hasattr(e, 'faultString'):
                print e.faultString
            else:
                print "I don't understand. Try `help view`"
            pass

    def do_create(self, param_str):
        """
        Create and submit a new ticket to Trac instance

        tint->> create `title` `desc` `type` ...

        NOT YET IMPLEMENTED

        Arguments:
        - `title`: Title of the ticket
        - `desc`: Ticket description
        - `type`: Type of the ticket
        - `priority`: Ticket priority
        - `component`: The component this ticket applies to
        - `version`: The version this ticket applies to
        """
        # would like to launch a blank template tmp file
        # and parse the returned file
        try:
            (title,
             desc,
             type,
             priority,
             component,
             version) = param_str.split(' ')
            print "`create` not implemented"
        except Exception, e:
            print e
            print "Try `help create` for more info"
            pass

    def do_edit(self, param_str):
        """
        Edit a ticket in Trac

        tint->> edit `ticket_id` `field_query`

        NOT YET IMPLEMENTED

        Arguments:
        - `ticket_id`: Returns None if empty
        - `field_query`: A query string of values to update.
                         (See `help queries` for more info.)
        """
        # would like to launch users' editor
        # and populate a tmp file with the ticket info
        # and parse the returned tmp file, submitting
        # the changed fields
        try:
            (ticket_id, field_query) = param_str.split(' ')
            print "`edit` not implemented"
        except Exception, e:
            print e
            print "Try `help edit` for more info"
            pass

    def do_quit(self, _):
        """
        Quit the program
        """
        # cmd.Cmd passes an arg no matter what
        # which we don't care about here.
        # possible bug?
        print "Goodbye!"
        sys.exit()

    # misc help functions

    def help_queries(self):
        text = """
        The argument to pass to the `query` command
        is a special Trac query string.

        Query strings take the form of:

           field=value

        Multiple queries can be stringed together
        by an ampersand:

           field1=value1&field2=value2

        Don't be afraid of spaces in the values. Everything
        is handled and interpreted correctly.
        """
        print text
