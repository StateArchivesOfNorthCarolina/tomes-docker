from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
import os
import json
import subprocess
import sys
from queue import Queue, Empty
from threading import Thread
from twisted.python import log
from twisted.internet import reactor
#TODO: Remove this from production
import platform
import re


class ElasticServer(WebSocketServerProtocol):
    #STANDARD_COMMANDS
    SEND_STD_OUT = 1
    SEND_PROG_ON = 2
    SEND_PROG_OFF = 3

    # SIGNALS OUT
    RECV_START_ELASTIC = 100
    RECV_STOP_ELASTIC = 101
    RECV_IS_ELASTIC_ON = 103
    RECV_LOAD_ACCOUNT = 104
    RECV_INDEX_ACCOUNT = 105

    #SIGNALS IN
    SND_ACCOUNT_FOUND = 201
    SND_ACCOUNT_NOT_FOUND = 202
    SND_ELASTIC_OFF = 203
    SND_ELASTIC_ON = 204
    SND_ACCOUNTS = 205
    SND_NO_ACCOUNTS = 206


    p = platform

    def __init__(self):
        super().__init__()
        self.on_posix = 'posix' in sys.builtin_module_names
        #TODO: Remove when we go into full production
        self.production = False
        if self.production:
            self.data_dir_base = os.path.abspath("/home/tomes/data/eaxs")
        else:
            self.data_dir_base = os.path.abspath("E:\RESOURCES\TEST_RESOURCES\\tomes\data\eaxs")
            os.environ["DOCKER_TLS_VERIFY"] = "1"
            os.environ["DOCKER_HOST"] = "tcp://192.168.99.100:2376"
            os.environ["DOCKER_CERT_PATH"] = "E:\\bin\\machines\\default"
            os.environ["DOCKER_MACHINE_NAME"] = "default"
            os.environ["COMPOSE_CONVERT_WINDOWS_PATHS"] = "true"

        self.start_es = []

        self.stop_es = ['docker', 'stop']
        self.directories_with_elastic = []
        self.directories_without_elastic = []
        self.message_buffer = []
        self.container_id = None
        self.container_ip = None
        self.working_account = None

    def onConnect(self, request):
        print("In Connect")
        headers = {'Access-Control-Allow-Origin': '*'}
        return None, headers

    def onOpen(self):
        print('Client connected!')
        self.sendMessage(self.get_message_for_sending(self.SEND_STD_OUT, "Server Connected."))
        self.find_accounts()

    def enqueue_out(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def get_message_for_sending(self, router, message):
        l = json.dumps({'router': router, 'data': message})
        return l.encode('utf-8')

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


    def is_on(self):
        res = subprocess.run(["docker", "ps"], stdout=subprocess.PIPE)
        lines = res.stdout.decode("utf-8").split("\n")
        is_on = False
        for l in lines:
            if re.match("^.*\.elastic", l):
                s = l.split(" ")
                self.container_id = s[0]
                is_on = True
                break
        if is_on:
            return True
        else:
            return False

    def onMessage(self, payload, isBinary):
        payload = json.loads(bytes.decode(payload, encoding='utf-8'))
        if payload["o"] == ElasticServer.RECV_IS_ELASTIC_ON:
            if self.is_on():
                self.sendMessage(self.get_message_for_sending(self.SND_ELASTIC_ON, ""))
            else:
                self.sendMessage(self.get_message_for_sending(self.SND_ELASTIC_OFF, ""))

        if payload["o"] == ElasticServer.RECV_START_ELASTIC:
            if self.container_id is None:
                reactor.callInThread(self.start_elastic)

        if payload["o"] == ElasticServer.RECV_STOP_ELASTIC:
            if self.container_id is not None:
                reactor.callInThread(self.stop_elastic)

        if payload["o"] == ElasticServer.RECV_LOAD_ACCOUNT:
            reactor.callInThread(self.handle_account_load(payload["data"]))

        if payload["o"] == ElasticServer.RECV_INDEX_ACCOUNT:
            reactor.callInThread(self.handle_elastic_start_preflight(payload['data']))
            reactor.callInThread(self.index_site(payload['data']))

    def get_index_command(self, account: str):
        cmd = ['python', 'eaxs_to_json.py', account, self.container_ip]
        return cmd

    def handle_account_load(self, location: str):
        path = location
        self.load_account(path)

    def handle_elastic_start_preflight(self, location: str):
        ep = location.split(os.path.sep)
        account_name = ep[:(len(ep) - 2)].pop()
        elastic_path = os.path.join(os.path.sep.join(ep[:(len(ep) - 2)]), "elastic{}data".format(os.path.sep))
        if not os.path.exists(elastic_path):
            os.makedirs(elastic_path)

        # start Elastic Server with the account's elastic path
        self.sendMessage(self.get_message_for_sending(self.SEND_STD_OUT, "Loading Account."))
        self.load_account(account_name)
        self.start_elastic()

    def _get_ip(self, id):
        command = ['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', id]
        res = subprocess.run(command, stdout=subprocess.PIPE)
        lines = res.stdout.decode("utf-8").split("\n")
        self.container_ip = lines[0]

    def build_opts(self):
        pass

    def find_accounts(self):
        for root, dirs, files in os.walk(self.data_dir_base):
            if "elastic" in dirs:
                self.directories_with_elastic.append(root)
            if "eaxs_xml" in dirs and "elastic" not in dirs:
                for root, dirs, files in os.walk(os.path.join(root, "eaxs_xml")):
                    for f in files:
                        if re.search("tagged", f):
                            self.directories_without_elastic.append(os.path.join(root, f))

        self.sendMessage(self.get_message_for_sending(self.SND_ACCOUNTS, json.dumps(self.directories_with_elastic)))
        self.sendMessage(self.get_message_for_sending(self.SND_NO_ACCOUNTS, json.dumps(self.directories_without_elastic)))

    def load_account(self, account):
        self.working_account = account
        self.start_es = ['docker', 'run', '-p', '9200:9200', '-p', '9300:9300',
                         '-d',
                         '-v', '/mnt/data/eaxs/{}/elastic/data:/usr/share/elasticsearch/data'.format(account),
                         '-e', 'discovery.type=single-node',
                         'govsanc/elasticsearch']

    def start_elastic(self):
        if self.container_id is None:
            p = self.get_sub_pointer(self.start_es)
            q = Queue()
            t = Thread(target=self.enqueue_out, args=(p.stdout, q))
            t.daemon = True
            self.sendMessage(self.get_message_for_sending(self.SEND_STD_OUT, "Bringing up Elasticsearch"))
            self.run_process(q, t)
            self.container_id = self.message_buffer.pop()

    def stop_elastic(self):
        self.stop_es.append(self.container_id)
        p = self.get_sub_pointer(self.stop_es)
        q = Queue()
        t = Thread(target=self.enqueue_out, args=(p.stdout, q))
        t.daemon = True
        self.sendMessage(self.get_message_for_sending(self.SEND_STD_OUT, "Stopping Elastic Container".format(self.container_id)))
        self.run_process(q, t)
        self.stop_es.pop()

    def get_sub_pointer(self, args):
        return subprocess.Popen(args, stdout=subprocess.PIPE,  bufsize=1, close_fds=self.on_posix)

    def index_site(self, location):
        p = subprocess.Popen(self.get_index_command(location), stdout=subprocess.PIPE, bufsize=1, close_fds=self.on_posix)
        q = Queue()
        t = Thread(target=self.enqueue_out, args=(p.stdout, q))
        t.daemon = True
        self.sendMessage(self.get_message_for_sending(self.SEND_STD_OUT, "Indexing: {}".format(location)))
        t.start()
        line = None
        # self.sendMessage(self.get_message_for_sending(self.SEND_PROG_ON, ''))
        while t.is_alive():
            try:
                # Wait for a line to be generated.
                line = q.get_nowait()
            except Empty:
                # if the queue is empty but not complete continue
                line = None

            if line is not None:
                l = bytes.decode(line, encoding='utf-8')
                sender = json.dumps({'router': self.SEND_STD_OUT, 'data': l.strip()})
                self.sendMessage(sender.encode('utf-8'))
        self.sendMessage(self.get_message_for_sending(self.SEND_STD_OUT, "Complete"))
        # self.sendMessage(self.get_message_for_sending(self.SEND_PROG_OFF, ''))

    def run_process(self, q, t):
        t.start()
        line = None
        while t.is_alive():
            try:
                # Wait for a line to be generated.
                line = q.get_nowait()
            except Empty:
                # if the queue is empty but not complete continue
                line = None

            if line is not None:
                l = bytes.decode(line, encoding='utf-8')
                self.message_buffer.append(l.strip())
                sender = json.dumps({'router': self.SEND_STD_OUT, 'data': l.strip()})
                self.sendMessage(sender.encode('utf-8'))


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory()
    factory.protocol = ElasticServer
    reactor.listenTCP(9004, factory)
    reactor.run()