from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS
import os
import json
import subprocess
import sys
from queue import Queue, Empty
from threading import Thread
from twisted.python import log
from twisted.internet import reactor


class DarcMailConvert(WebSocketServerProtocol):
    WS_FOLDER_LIST = 1
    WS_RECV_PACKAGE = 2
    WS_PROG_ON = 4
    WS_PROG_OFF = 5
    WS_SEND = 3

    def __init__(self):
        super().__init__()
        self.server_name = "DarcMailConverter"
        self.on_posix = 'posix' in sys.builtin_module_names
        self.cur_folder = None
        self.stitch = None
        self.chunk = None
        self.chunk_size = None
        self.from_eml = None
        self.transfer_name = None
        self.build_opts = []
        self.production = True
        self.file_tree = []
        if self.production:
            self.dm_exec = '/usr/src/app/docker_dmc/DarcMailCLI.py'
            self.base_package_location = "/home/tomes/data"
        else:
            self.dm_exec = 'D:\\Development\\Python\\DockerComposeStruct\\devel\\tomes_docker_app\\Servers\\darcm_server\\docker_dmc\\DarcMailCLI.py'
            self.base_package_location = 'E:\\RESOURCES\\TEST_RESOURCES\\tomes\\data'

    def onConnect(self, request):
        print("{}: Connected".format(self.server_name))
        headers = {'Access-Control-Allow-Origin': '*'}
        return None, headers

    def onOpen(self):
        s = self._get_folder_tree()
        self.sendMessage(self.get_message_for_sending(DarcMailConvert.WS_FOLDER_LIST, s))
        self.sendMessage(self.get_message_for_sending(DarcMailConvert.WS_SEND, 'Client connected!'))

    def _get_folder_tree(self):
        children = os.listdir(os.path.join(self.base_package_location, 'mboxes'))
        nc = []
        for c in children:
            nc.append({'name': c})
        self.file_tree.append({'name': "Mime Sources", 'children': nc})
        return json.dumps(self.file_tree)

    def onMessage(self, payload, isBinary):
        payload = json.loads(bytes.decode(payload, encoding='utf-8'))
        if isBinary:
            pass
        else:
            if payload['o'] == DarcMailConvert.WS_RECV_PACKAGE:
                self.cur_folder = payload['data']['fldr']
                self.stitch = payload['data']['stitch']
                self.chunk = payload['data']['chunk']
                self.chunk_size = payload['data']['chunk_size']
                self.from_eml = payload['data']['from_eml']
                self.transfer_name = payload['data']['trans_name']
                self.build_convert_opts()
                # callInThread necessary to prevent blocking
                reactor.callInThread(self.convert)
            if payload['o'] == 5:
                self.get(payload['data']['fldr'])

    def find_folder(self, folder):
        for root, dirs, files in os.walk(self.base_package_location):
            for d in dirs:
                #self.sendMessage(self.get_message_for_sending(2, "Fldrs: {}".format(d)))
                if d == folder:
                    return os.path.join(root, d)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def get(self, fldr) -> str:
        # Get a suggested transfer_name
        #self.sendMessage(self.get_message_for_sending(2, "Base package is {}".format(self.base_package_location)))
        for root, dirs, files in os.walk(self.base_package_location):
            for d in dirs:
                if d == fldr:
                    root_split = root.split(os.path.sep)
                    i = root_split.index('data') + 2
                    final = root_split[i:] + [d]
                    final = '_'.join(final)
                    final = final.replace(" ", "_")
                    self.sendMessage(self.get_message_for_sending(5, final))

    def build_convert_opts(self):
        self.build_opts = ['python', self.dm_exec]
        package_location = self.find_folder(self.cur_folder)

        # BEGIN REQUIRED These are required
        self.build_opts.append('-a')
        self.build_opts.append(self.transfer_name)
        self.build_opts.append("-d")
        self.build_opts.append(package_location)
        self.build_opts.append("-tt")
        # End REQUIRED

        # BEGIN NOT REQUIRED These are NOT Required but recommended
        self.build_opts.append('-c')
        if self.chunk:
            self.build_opts.append('{}'.format(self.chunk_size))
        else:
            self.build_opts.append('{}'.format(0))

        if self.stitch:
            self.build_opts.append('-st')
        # END NOT REQUIRED

        # BEGIN OPTIONS: These are options
        if self.from_eml:
            # Requested Structure is EML
            self.build_opts.append('-fe')

        # END OPTIONS

        for i in range(len(self.build_opts)):
            self.build_opts[i] = str(self.build_opts[i])

    def enqueue_out(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def get_message_for_sending(self, router, message):
        l = json.dumps({'router': router, 'data': message})
        return l.encode('utf-8')

    def convert(self):
        p = subprocess.Popen(self.build_opts, stdout=subprocess.PIPE, bufsize=1, close_fds=self.on_posix)
        q = Queue()
        t = Thread(target=self.enqueue_out, args=(p.stdout, q))
        t.daemon = True
        self.sendMessage(self.get_message_for_sending(DarcMailConvert.WS_SEND, "Processing: {}".format(self.cur_folder)))
        t.start()
        line = None
        self.sendMessage(self.get_message_for_sending(DarcMailConvert.WS_PROG_ON, ''))
        while t.is_alive():
            try:
                # Wait for a line to be generated.
                line = q.get_nowait()
            except Empty:
                # if the queue is empty but not complete continue
                pass
            else:
                l = bytes.decode(line, encoding='utf-8')
                sender = json.dumps({'router': DarcMailConvert.WS_SEND, 'data': l.strip()})
                self.sendMessage(sender.encode('utf-8'))

        self.sendMessage(self.get_message_for_sending(DarcMailConvert.WS_SEND, "Complete"))
        self.sendMessage(self.get_message_for_sending(DarcMailConvert.WS_PROG_OFF, ''))


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory()
    factory.protocol = DarcMailConvert
    reactor.listenTCP(9001, factory)
    reactor.run()