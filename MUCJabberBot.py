from jabberbot import JabberBot
import utils
import re
import xmpp
import logging

class MUCJabberBot(JabberBot):

    flood_protection = 0
    flood_delay = 5
    PING_FREQUENCY = 60
    nicks_to_jids = {}

    def __init__(self, nickname, *args, **kwargs):
        ''' Initialize variables. '''

        # answer only direct messages or not?
        self.nickname = nickname
        self.only_direct = kwargs.get('only_direct', False)

        try:
            del kwargs['only_direct']
        except KeyError:
            pass

        # initialize jabberbot
        super(MUCJabberBot, self).__init__(*args, **kwargs)

        # create a regex to check if a message is a direct message
        user, domain = str(self.jid).split('@')
        self.direct_message_re = re.compile('^%s(@%s)?[^\w]? '
                                            % (user, domain))

        self.unknown_command_callback = None


    def callback_message(self, conn, mess):
        ''' Changes the behaviour of the JabberBot in order to allow
        it to answer direct messages. This is used often when it is
        connected in MUCs (multiple users chatroom). '''
        # fuck you unicode
        message = mess.getBody()
        props = mess.getProperties()
        jid = mess.getFrom()
        try:
            if self.direct_message_re.match(message):
                mess.setBody(' '.join(message.split(' ', 1)[1:]))
                super(MUCJabberBot, self).callback_message(conn, mess)
        except TypeError:
            return
        if not message:
            return
        if xmpp.NS_DELAY in props:
            return
        if self.jid.bareMatch(jid):
            return
        if utils.is_ping(self.nickname, message):
            np_message = self.fix_ping(message)
        else:
            np_message = message
        if ' ' in np_message:
            command, args = np_message.split(' ', 1)
        else:
            command, args = np_message, ''

        if mess.getSubject():
            logging.debug('ignoring subject..')
            return

        cmd = command.lower()
        if cmd in self.commands:
            if utils.is_ping(self.nickname, message):
                mess.setBody(np_message)
                super(MUCJabberBot, self).callback_message(conn, mess)
            else:
                return
        else:
            reply = self.unknown_command(mess, cmd, args)
            if reply is None:
                return
            if reply:
                self.send_simple_reply(mess, reply)
        return

    def callback_presence(self, conn, presence):
        super(MUCJabberBot, self).callback_presence(conn, presence)
        nick = presence.getFrom().getResource()
        if presence.getJid() is not None:
            self.nicks_to_jids[nick] = xmpp.JID(presence.getJid()).getStripped()

    def get_jid_from_nick(self, nick):
        if self.nicks_to_jids.has_key(nick): return self.nicks_to_jids[nick]

    def load_commands_from(self, target):
        import inspect
        for name, value in inspect.getmembers(target, inspect.ismethod):
            if getattr(value, '_jabberbot_command', False):
                name = getattr(value, '_jabberbot_command_name')
                self.log.info('Registered command: %s' % name)
                self.commands[name] = value

    def fix_ping(self, message):
        message = message.replace(self.nickname+": ", "")
        message = message.replace(self.nickname.lower()+": ", "")
        return message

    def unknown_command(self, mess, cmd, args):
        if self.unknown_command_callback is not None:
            return self.unknown_command_callback(self, mess, cmd, args)
    def on_ping_timeout(self):
        print("PING TIMEOUT")
        logging.info('WARNING: ping timeout.')
        # self.quit(1)

