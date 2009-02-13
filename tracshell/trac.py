import os, sys
import cmd
import subprocess
import tempfile
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
        self._server = self._connect()
        self._editor = self._find_editor()

        # set up shell options
        cmd.Cmd.__init__(self)
        self.prompt = "trac->> "
        self.ruler = '-'
        self.intro = "Welcome to TracShell!\nType `help` for a list of commands"

    def _connect(self):
        """
        Return an xmlrpc.ServerProxy instance
        """
        conn_str = "http://%s:%s@%s:%s%s" % (self._username,
                                             self._password,
                                             self._host,
                                             self._port,
                                             self._rpc_path)
        return xmlrpclib.ServerProxy(conn_str)

    def _find_editor(self):
        """
        Try to find the users' editor by testing
        the $EDITOR environment variable, warn the
        user if one isn't found and return None.
        """
        try:
            return os.environ['EDITOR']
        except KeyError:
            print "Warning: No editor found, see `help editors`"
            return None

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

        tint->> create My Important Ticket Summary

        IMPLEMENTED BUT BUGGY

        Arguments:
        - `summary`: Title of the ticket
        """
        try:
            fname = tempfile.mktemp()
            fh = open(fname, "w")
            template_lines = ["summary=%s\n" % param_str,
                              "reporter=\n",
                              "description=\n",
                              "type=\n",
                              "priority=\n",
                              "component=\n",
                              "milestone=\n",
                              "version=\n",
                              "keywords=\n"]
            fh.writelines(template_lines)
            fh.close()
            subprocess.call([self._editor, fname])
            try:
                data = self.parse_ticket_file(open(fname))
            except ValueError:
                print "Something went wrong or the file was formatted"
                print "wrong. Please try submitting the ticket again"
                print "or file a bug report with the TracShell devs."
                return False
            try:
                id = self._server.ticket.create(data.pop("summary"),
                                                data.pop("description"),
                                                data)
            except Exception, e:
                print "A problem has occurred communicating with Trac."
                print "Error: %s" % e
                print "Please file a bug report with the TracShell devs."
                return False
            if id:
                print "Created ticket %s: %s" % (id, param_str)
        except Exception, e:
            print e
            print "Try `help create` for more info"
            pass

    def do_edit(self, param_str):
        """
        Edit a ticket in Trac

        tint->> edit 123

        IMPLEMENTED BUT BUGGY

        Arguments:
        - `ticket_id`: Returns None if empty
        """
        try:
            (id, created, modified, data) = self._server.ticket.get(param_str)
        except Exception, e:
            print "A problem has occurred communicating with Trac."
            print "Error: %s" % e
            print "Please file a bug report with the TracShell devs."
            return False
        data['comment'] = "Your comment here"
        tmp_lines = ["%s=%s\n" % (k, v) for k, v in data.iteritems()]
        fname = tempfile.mktemp()
        fh = open(fname, "w")
        fh.writelines(tmp_lines)
        fh.close()
        subprocess.call([self._editor, fname])
        try:
            data = self.parse_ticket_file(open(fname))
        except ValueError:
            print "Something went wrong or the file was formatted"
            print "wrong. Please try submitting the ticket again"
            print "or file a bug report with the TracShell devs."
            return False
        try:
            (new_id,
             new_created,
             new_modified,
             new_data) = self._server.ticket.update(id,
                                                    data.pop('comment'),
                                                    data)
        except Exception, e:
            print "A problem has occurred communicating with Trac."
            print "Error: %s" % e
            print "Please file a bug report with the TracShell devs."
            return False
        print "Updated Details for Ticket: %s" % id
        print " "
        for k, v in data.iteritems():
            print "%15s: %s" % (k, v)

    # option setter funcs
    # see `do_set`

    def set_editor(self, editor):
        """
        Set the path to the editor to invoke for manipulating
        tickets, comments, etc.
        
        Arguments:
        - `editor`: the path to an editor
        """
        if os.path.exists(editor):
            self._editor = editor
        else:
            raise ValueError, "Not a valid path to an editor"

    # misc support funcs

    def do_set(self, query_str):
        """
        Set an option using a query string.

        Valid options are:

        - `editor`: A valid path to your favorite editor

        See `help queries` for more information.
        
        Arguments:
        - `query_str`: A query string of options to set
        """
        try:
            data = self.parse_query_str(query_str)
        except ValueError:
            print "Warning: Invalid query string for `set`"
            print "Try fixing %s" % query_str
            print "See `help queries` for more information."
            pass

        for k, v in data.iteritems():
            if hasattr(self, 'set_%s' % k):
                try:
                    getattr(self, 'set_%s' % k)(v)
                except Exception, e:
                    print e
                    pass
        
    def parse_query_str(self, string):
        """
        Parse a query string
        
        Arguments:
        - `string`: A string in the form of field=val
                    and seperated by &.
        """
        pairs = string.split('&')
        data = dict([item.split('=') for item in pairs])
        return data

    def parse_ticket_file(self, fh):
        """
        Parses a file with field=val bits on each line.
        Returns a dictionary of key: val pairs.
        
        Arguments:
        - `fh`: a python file object to parse
        """
        lines = fh.readlines()
        data = dict([line.split('=') for line in lines])
        return data

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
        Query strings take the form of:

           field=value

        Multiple queries can be stringed together
        by an ampersand:

           field1=value1&field2=value2

        Don't be afraid of spaces in the values. Everything
        is handled and interpreted correctly. Just make sure
        that there's one '=' between field and value and one
        '&' between field/value pairs.
        """
        print text

    def help_editors(self):
        text = """
        TracShell uses your preferred text editor for
        editing and creating tickets, comments, and so
        forth. It tries to find your preferred editor
        by looking for it in the $EDITOR environment
        variable.

        If not set, you may get a warning. In this case,
        see the `help set` command for setting up options
        inside the TracShell.
        """
        print text
