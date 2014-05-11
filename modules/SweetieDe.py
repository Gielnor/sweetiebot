from utils import logerrors
from jabberbot import botcmd
from datetime import datetime
import logging
import random
import json

log = logging.getLogger(__name__)

class SweetieDe(object):
    kick_owl_delay = 7200
    last_owl_kick = 0

    def __init__(self, bot, admin, mq):
        bot.load_commands_from(self)
        self.admin = admin
        self.mq = mq

    @botcmd
    @logerrors
    def deowl(self, mess, args):
        speaker = mess.getFrom()
        '''Only kicks :owl, long cooldown'''
        if self.last_owl_kick:
            if (datetime.now() - self.last_owl_kick).seconds < self.kick_owl_delay:
                self.log_deowl(speaker, False)
                return "I'm tired. Maybe another time?"
        log.debug("trying to kick owl ...")
        self.admin.kick(':owl', ':sweetiestare:',
                        on_success=self.deowl_success_handler(speaker),
                        on_failure=self.deowl_failure_handler(speaker))
        return

    def deowl_success_handler(self, speaker):
        def handler():
            log.debug('deowl success')
            self.last_owl_kick = datetime.now()
            self.kick_owl_delay = random.gauss(2*60*60, 20*60)
            self.log_deowl(speaker, True)
        return handler

    def deowl_failure_handler(self, speaker):
        def handler():
            log.debug('deowl failure')
            self.log_deowl(speaker, False)
        return handler

    @logerrors
    def log_deowl(self, speaker, success):
        timestamp = datetime.utcnow()
        mq_message = {
            'deowl':True,
            'room':speaker.getNode(),
            'server':speaker.getDomain(),
            'speaker': speaker.getResource(),
            'timestamp': timestamp.isoformat(' '),
            'success': success,
            }

        self.mq.send(json.dumps(mq_message))

    @botcmd
    def deoctavia(self, mess, args):
        self.detavi(mess, args)

    @botcmd
    @logerrors
    def detavi(self, mess, args):
        speaker = mess.getFrom().getResource()
        log.debug("trying to kick "+speaker)
        target = 'Octavia' if self.admin.nick_is_mod(speaker) else speaker
        self.admin.kick(target, ':lyraahem:')
        return