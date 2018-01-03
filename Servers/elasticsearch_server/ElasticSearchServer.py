from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS
import os
import json
import subprocess
import sys
from elasticsearch import Elasticsearch
from queue import Queue, Empty
from threading import Thread
from twisted.python import log
from twisted.internet import reactor
#TODO: Remove this from production
import platform


class ElasticServer(WebSocketServerProtocol):
    #STANDARD_COMMANDS
    SEND_STD_OUT = 1
    SEND_PROG_ON = 2
    SEND_PROG_OFF = 3

    # SIGNALS OUT
    START_ELASTIC = 100
    STOP_ELASTIC = 101
    ACCOUNT_FOUND = 201
    ACCOUNT_NOT_FOUND = 202

    # SIGNALS IN
    ACCOUNT_SELECTED = 200
    INCOMING_QUERY = 203



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
        self.message_buffer = []
        self.container_id = None
        self.working_account = None

    def onConnect(self, request):
        print("In Connect")
        headers = {'Access-Control-Allow-Origin': '*'}
        return None, headers

    def onOpen(self):
        print('Client connected!')

    def enqueue_out(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def get_message_for_sending(self, router, message):
        l = json.dumps({'router': router, 'data': message})
        return l.encode('utf-8')

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def onMessage(self, payload, isBinary):
        payload = json.loads(bytes.decode(payload, encoding='utf-8'))
        if payload["o"] == ElasticServer.START_ELASTIC:
            if self.container_id is None:
                reactor.callInThread(self.start_elastic)

        if payload["o"] == ElasticServer.STOP_ELASTIC:
            if self.container_id is not None:
                reactor.callInThread(self.stop_elastic)

        if payload["o"] == ElasticServer.ACCOUNT_SELECTED:
            reactor.callInThread(self.find_file_in_path(payload["data"]))

        if payload["o"] == ElasticServer.INCOMING_QUERY:
            reactor.callInThread(self.query_server(payload["data"]))

    def build_opts(self):
        pass

    def query_server(self, query):
        es = Elasticsearch([{'host': '192.168.99.100'}])

    def find_file_in_path(self, account):
        self.working_account = account
        self.start_es = ['docker', 'run', '-p', '9200:9200', '-p', '9300:9300',
                         '-d',
                         '-v', '/mnt/data/eaxs/{}/elastic/data:/usr/share/elasticsearch/data'.format(account),
                         '-e', 'discovery.type=single-node',
                         'docker.elastic.co/elasticsearch/elasticsearch:6.0.0']
        self.sendMessage(self.get_message_for_sending(self.ACCOUNT_FOUND, ""))

    def start_elastic(self):
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


class ElasticQueryBuilder:
    def __init__(self, index: str, type: str) -> None:
        super().__init__()
        self.index = index
        self.type = type
        self.terms = {}
        self.query = {}

    def add_term(self, term: str, value: str):
        self.terms[term] = value

    def do_query(self, es: Elasticsearch):
        pass


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory()
    factory.protocol = ElasticServer
    reactor.listenTCP(9004, factory)
    reactor.run()