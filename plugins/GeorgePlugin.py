from disco.bot import Bot, Plugin

from utils import jsonstorage
from utils.constants import Constants
from utils.migrationhelper import MigrationHelper

from datetime import datetime
import re
import pdb

class GeorgePlugin(Plugin):
    def initialize(self, event):
        migrationhelper = MigrationHelper(self.get_server_id(event))
        migrationhelper.check_for_updates()

    @Plugin.command('help')
    def help(self, event):
        helptext = "``` \n"
        helptext += "help output: \n"
        helptext +=" \n"
        helptext += "@GeorgePlugin outputchannel #channelname | Sets the channel in which GeorgePlugin will send its messages \n"
        helptext += "@GeorgePlugin adminonlycontrol true/false | to allow or disallow non-admin members of the discord to use @GeorgePlugin commands \n"
        helptext += "```"
        event.msg.reply(helptext)

    def command_set_adminonlycontrol(self, event):
        if not self.is_allowed(event):
            return
        value = event.msg.content.split('adminonlycontrol')[1].lower().strip()
        if value in ['true', 'false']:
            jsonstorage.add(self.get_server_id(event), Constants.adminonlycontrol.fget(), value)
            event.msg.reply('Admin-only-control set to: {}'.format(value))
        else:
            event.msg.reply('Received: {}, only accepts true/false'.format(value))

    def command_set_urloutputchannel(self, event):
        if not self.is_allowed(event):
            return
        if '#' in event.message.content:
            value = re.sub("[^0-9]", " ", event.message.content.split('#')[1]).split(' ')[0]
            if self.is_valid_server_channel_id(value):
                if not self.has_outputchannel(self.get_server_id(event)):
                    jsonstorage.initialize_dict(self.get_server_id(event), Constants.output_channel.fget())
                jsonstorage.add(self.get_server_id(event), Constants.output_channel.fget(), value)
                event.message.reply('Set {} as outputchannel'.format(self.get_channel_name(value)))
            else:
                event.message.reply('Channel-name not recognized')
        else:
            event.message.reply('No channel detected')

    def handle_keywords(self, event):
        msg = event.message.content
        if msg.split(' ')[0] == '/outputchannel':
            self.command_set_urloutputchannel(event)
            return True
        if msg.split(' ')[0] == '/adminonlycontrol':
            self.command_set_adminonlycontrol(event)
            return True
        if msg.split(' ')[0] == '/record'
            self.add_time(event)
        return False

    def add_time(self, event, time):
        if self.is_numbered_channel(event):
            record = msg.split(' ')[1]
            time = datetime.strptime(record, '%H:%M:%S')
	        import pdb
	        pdb.set_trace()

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.initialize(event)
        if self.is_bot(event):
            return
        if self.handle_keywords(event):
            return
        if self.has_outputchannel(self.get_server_id(event)):
            output_channel_id = int(jsonstorage.get(self.get_server_id(event), Constants.output_channel.fget()))
            output_channel = self.bot.client.state.channels.get(output_channel_id)
            if self.is_valid_server_channel_id(output_channel_id):
                if(self.is_numbered_channel(event)):
                    if str(event.message.content).startswith('add'):
                        self.add_time(event, str(event.message.content).split('add')[1])
        else:
            event.reply("No outputchannel has been set")

    def get_server_id(self, event):
        return event._guild.id

    def get_server_channel_list(self):
        return self.bot.client.state.channels.values()

    def is_valid_server_channel_id(self, channel_id):
        return (next((channel for channel in self.get_server_channel_list() if channel.id == int(channel_id)), None) is not None)

    def get_channel_name(self, channel_id):
        for channel in self.get_server_channel_list():
            if channel.id == int(channel_id):
                return '#{}'.format(channel.name)
        return ''

    def is_numbered_channel(self, event):
        channel_id = event.raw_data['message']['channel_id']
        return self.get_channel_name(channel_id).strip('#')[:1].isdigit()

    def is_bot(self, event):
        return (self.bot.client.state.me.id == int(event.raw_data['message']['author']['id']))

    def is_allowed(self, event):
        if self.is_admin_only_control(self.get_server_id(event)) and not self.is_admin(event):
            event.msg.reply('Sorry, you lack the required permissions to program my behaviour')
            return False
        return True

    def is_admin(self, event):
        return event.member.permissions.to_dict()['administrator']

    def is_admin_only_control(self, server_id):
        try:
            value = jsonstorage.get(server_id, Constants.adminonlycontrol.fget())
        except:
            value = None
        if value in ['True', 'true']:
            return True
        else:
            return False

    def has_outputchannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.output_channel.fget())
            return True
        except Exception:
            return False
