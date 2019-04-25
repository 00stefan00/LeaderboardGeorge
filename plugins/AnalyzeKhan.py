from disco.bot import Bot, Plugin

from utils import jsonstorage
from utils.constants import Constants
from utils.migrationhelper import MigrationHelper

import re
import pdb

class AnalyzeKhanPlugin(Plugin):
    def initialize(self, event):
        migrationhelper = MigrationHelper(self.get_server_id(event))
        migrationhelper.check_for_updates()

    @Plugin.command('help')
    def help(self, event):
        helptext = "``` \n"
        helptext += "help output: \n"
        helptext +=" \n"
        helptext += "@AnalyzeKhan logchannel #channelname | Sets the channel which should be scanned by AnalyzeKhan \n"
        helptext += "@AnalyzeKhan outputchannel #channelname | Sets the channel in which AnalyzeKhan will send its messages \n"
        helptext += "@AnalyzeKhan addkeyword <keyword> <response> | Will set a certain response for the specified keyword \n"
        helptext += "@AnalyzeKhan removekeyword <keyword> | will remove a certain keyword including its response \n"
        helptext += "@AnalyzeKhan showkeywords | will show the current list of keywords \n"
        helptext += "@AnalyzeKhan adminonlycontrol true/false | to allow or disallow non-admin members of the discord to use @AnalyzeKhan commands \n"
        helptext += "```"
        event.msg.reply(helptext)

    @Plugin.command('adminonlycontrol')
    def command_set_adminonlycontrol(self, event):
        if not self.is_allowed(event):
            return
        value = event.msg.content.split('adminonlycontrol')[1].lower().strip()
        if value in ['true', 'false']:
            jsonstorage.add(self.get_server_id(event), Constants.adminonlycontrol.fget(), value)
            event.msg.reply('Admin-only-control set to: {}'.format(value))
        else:
            event.msg.reply('Received: {}, only accepts true/false'.format(value))

    @Plugin.command('logchannel')
    def command_set_urlinputchannel(self, event):
        if not self.is_allowed(event):
            return
        if '#' in event.msg.content:
            value = re.sub("[^0-9]", " ", event.msg.content.split('#')[1]).split(' ')[0]
            if self.is_valid_server_channel_id(value):
                jsonstorage.add(self.get_server_id(event), Constants.input_channel.fget(), value)
                event.msg.reply('Scanning channel: {}'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.command('outputchannel')
    def command_set_urloutputchannel(self, event):
        if not self.is_allowed(event):
            return
        if '#' in event.msg.content:
            value = re.sub("[^0-9]", " ", event.msg.content.split('#')[1]).split(' ')[0]
            if self.is_valid_server_channel_id(value):
                jsonstorage.add(self.get_server_id(event), Constants.output_channel.fget(), value)
                event.msg.reply('Set {} as outputchannel'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.initialize(event)

        if self.is_bot(event):
            return
        if self.has_inputchannel(self.get_server_id(event)):
            input_channel_id = jsonstorage.get(self.get_server_id(event), Constants.input_channel.fget())
            if event.raw_data['message']['channel_id'] != input_channel_id:
                return

        if self.has_outputchannel(self.get_server_id(event)):
            output_channel_id = int(jsonstorage.get(self.get_server_id(event), Constants.output_channel.fget()))
            output_channel = self.bot.client.state.channels.get(output_channel_id)
            if self.is_valid_server_channel_id(output_channel_id):
                keywords = self.get_triggered_keywords(self.get_server_id(event), event.message.content)
                for word in event.message.content.split(' '):
                    if word in keywords:
                        response = self.get_triggered_response(self.get_server_id(event), word)
                        event.reply(response)
        else:
            event.reply("No outputchannel has been set")

    def get_triggered_keywords(self, server_id, text):
        keywordlist = jsonstorage.get(server_id, Constants.keyword_list.fget())
        return [x for x in keywordlist]

    def get_triggered_response(self, server_id, key):
        keywordlist = jsonstorage.get(server_id, Constants.keyword_list.fget())
        return keywordlist[key]

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

    def has_inputchannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.input_channel.fget())
            return True
        except Exception:
            return False

    def has_outputchannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.output_channel.fget())
            return True
        except Exception:
            return False

    @Plugin.command('showkeywords')
    def command_set_showkeywords(self, event):
        if not self.is_allowed(event):
            return
        keywordlist = jsonstorage.get(self.get_server_id(event), Constants.keyword_list.fget())
        event.msg.reply("Keywords: {}".format(keywordlist.items()))

    @Plugin.command('addkeyword')
    def command_set_keywordsadd(self, event):
        if not self.is_allowed(event):
            return
        details = event.msg.content.split("addkeyword")[1].strip()
        key = details.split(" ")[0]
        response = details.strip(key)
        if (len(response) < 1):
            event.msg.reply("No response given")
            return
        if not self.has_keywords(self.get_server_id(event)):
            jsonstorage.initialize_dict(self.get_server_id(event), Constants.keyword_list.fget())
        jsonstorage.add_to_dict(self.get_server_id(event), Constants.keyword_list.fget(), key, response)
        event.msg.reply("Added to the keyword list: {} with response: {}".format(key, response))

    @Plugin.command('removekeyword')
    def command_set_removekeywords(self, event):
        if not self.is_allowed(event):
            return
        details = event.msg.content.split("removekeyword")[1].strip()
        name = details.split(" ")[0]
        jsonstorage.remove_from_dict(self.get_server_id(event), Constants.keyword_list.fget(), str(name))
        event.msg.reply("Removed from the keyword list: {}".format(name))

    def has_keywords(self, server_id):
        try:
            keylist = jsonstorage.get(server_id, Constants.keyword_list.fget())
            return True 
        except Exception:
            return False