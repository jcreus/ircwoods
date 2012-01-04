# -*- coding: utf-8 -*-

import socket, time, re
from datetime import datetime

class TextFileLogger:
    def __init__(self, outfile="{chan}log{date}.txt"):
        self.filename = outfile

    def _makeFile(self, timestamp, channel):
        return self.filename.replace("{date}",datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')).replace("{chan}", channel)

    def addEntry(self, channel, text, timestamp):
        f = open(self._makeFile(timestamp, channel),'a')
        f.write(text)
        f.close()

    def close(self):
        self.file.close()

class IRCBot:
    def __init__(self, config):
        self.host = config.get("host",None)
        self.port = config.get("port",6667)
        self.nick = config.get("nick","testbota")
        self.user = config.get("user","testbotb")
        self.logger = config.get("logger",None)
        self.channels = config.get("channels",[])
       
    def _getUser(self,user):
        return user.split("!")[0]

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.host,self.port))
        self.sock.send('NICK %s\n' % self.nick)
        self.sock.send('USER %s %s just : atest\n' % (self.user, self.host))
        for channel in self.channels:
            self.joinChannel(channel)
        while True:
            recv = self.sock.recv(1024)
            print recv
            if "PING" in recv:
                print "Ponging"
                self.sock.send("PONG %s\n"%recv.split(" ")[1]+"\n")
            elif "JOIN" in recv:
                recv = recv.rstrip()
                parts = recv.split(":")[1].split(" ")
                uname = parts[0]
                chan = parts[2]
                timestamp = time.time()
                self.logger.addEntry(chan, "%s has joined %s\n" % (uname,chan), timestamp)
            elif "PART" in recv:
                recv = recv.rstrip()
                parts = recv.split(":")[1].split(" ")
                uname = parts[0]
                chan = parts[2]
                timestamp = time.time()
                self.logger.addEntry(chan, "%s has left %s\n" % (uname,chan), timestamp)
            elif "PRIVMSG" in recv:
                recv = recv.rstrip()
                parts = recv.split(":")
                tmp = parts[1].split(" ")
                user = tmp[0]
                chan = tmp[2]                
                msg = ' '.join(parts[2:])
                timestamp = time.time()
                self.logger.addEntry(chan, "<%s> %s\n" % (self._getUser(user),msg), timestamp)
                if "!pull" in msg:
                   for pull in re.findall("\!pull (\d+)",msg):
                      self.sock.send("PRIVMSG "+chan+" :https://github.com/sympy/sympy/pull/"+pull+"\n")#self.sock.send("PRIVMSG 

    def disconnect(self):
        self.sock.close()

    def joinChannel(self, channel):
        print "Joining #%s" % channel
        self.sock.send('JOIN #%s\n' % channel)

l = TextFileLogger()
# Channels without #, unless you want a two-# channel. For example, sympy for channel #sympy, but #justatest for channel ##justatest.
i = IRCBot({"host":"irc.freenode.net","channels":["#justatest"],"logger":l})
try:
    i.connect()
except KeyboardInterrupt:
    i.disconnect()
