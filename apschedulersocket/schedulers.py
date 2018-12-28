import logging
import socket
import threading
import json
from datetime import date
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import dateutil.parser

logger = logging.getLogger()

DEFAULT_PORT = 1033
DEFAULT_ADDR = "127.0.0.1"
MSG_MAX_LENGTH = 1024
DEBUG = False

def echo(msg):
    """
    Show more information in debug mode.
    """
    if DEBUG:
        print(msg)


class SchedulerClient():
    """
    Client to communicate with the server and retrieve information about the scheduled jobs.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT):
        self.addr = addr
        self.port = port

    def _read_msg(self, conn):
        msg = conn.recv(MSG_MAX_LENGTH).decode("utf-8")
        msg = json.loads(msg)

        # Check if it is a ISO-date
        if type(msg) == str:
            try:
                msg = dateutil.parser.parse(msg)
            except ValueError:
                pass
        echo("  :: C - %s" % msg)
        return msg

    def _send_msg(self, msg):
        """
        Send a message/request to the server and wait/return the answer.
        """
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.addr, self.port))
        msg = json.dumps(msg)
        msg = bytes(msg, 'utf-8')

        echo("C => S - %s" % msg)
        conn.sendall(msg)
        return conn

    def is_server_running(self):
        """
        Check if the server is running
        """
        try:
            return self.call(["BackgroundScheduler", "state"]) == 1
        except ConnectionRefusedError:
            return False

    def is_server_running(self):
        """
        Check if the server is running
        """
        try:
            return self.call(["BackgroundScheduler", "state"]) == 1
        except ConnectionRefusedError:
            return False

    def send_shutdown(self):
        """
        Stop the server.
        """
        return self.call(["shutdown"])

    def call(self, call_array):
        conn = ret = self._send_msg(call_array)
        ret = self._read_msg(conn)
        return ret


class BackgroundSchedulerAdjusted(BackgroundScheduler):
    """
    A BackgroundScheduler object adjusted to return json Serialization values.
    """

    def orig_get_jobs(self, jobstore=None, pending=None):
        return super(BackgroundSchedulerAdjusted, self).get_jobs(jobstore, pending)

    def get_jobs(self, jobstore=None, pending=None):
        """
        Return just the id of the jobs
        """
        jobs = super(BackgroundSchedulerAdjusted, self).get_jobs(jobstore, pending)
        return [job.id for job in jobs]


class SchedulerServer():
    """
    Integration between BackgroundScheduler and a Client-Server.
    """

    background_scheduler = BackgroundSchedulerAdjusted()

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT, daemon=True):
        self.addr = addr
        self.port = port
        self.daemon = daemon
        self.client = SchedulerClient(addr, port)

    def add_job(self, func, id, **args):
        self.background_scheduler.add_job(func=func, id=id, **args)



    def _read_msg(self, conn):
        msg = conn.recv(MSG_MAX_LENGTH).decode("utf-8")
        msg = json.loads(msg)
        echo("  :: S - %s" % msg)
        return msg

    def _send_msg(self, conn, msg):
        """
        Send a message/request to the server and wait/return the answer.
        """
        try:
            msg = json.dumps(msg)
        except TypeError:
            msg = json.dumps("The result '%s' is not JSON serializable!" % repr(msg))
        echo("S => C - %s" % msg)
        msg = bytes(msg, 'utf-8')
        conn.sendall(msg)

    def _start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.addr, self.port))
        server_socket.listen()
        while True:
            print()
            conn, addr = server_socket.accept()
            try:
                print("Connection accepted from " + repr(addr[1]))
                msg = self._read_msg(conn)
                if msg[0] == 'shutdown':
                    self._send_msg(conn, True)
                    self._stop_scheduler()
                    server_socket.close()
                    return True
                elif msg[0] == 'BackgroundScheduler':
                    attrib = getattr(self.background_scheduler, msg[1], None)
                else:
                    job = self.background_scheduler.get_job(msg[0], None)
                    if not job:
                        raise Exception("There is no job with id '%s' (The valid options are: shutdown, "
                                        "BackgroundScheduler or [job_id])." % msg[0])
                    attrib = getattr(job, msg[1])
                if callable(attrib):
                    # There are arguments informed
                    if len(msg) > 2:
                        args = msg[3:]
                        ret = attrib(*args)
                    else:
                        ret = attrib()
                else:
                    ret = attrib

                # Handle datetime in json
                if isinstance(ret, (datetime, date)):
                    ret = ret.isoformat()

                self._send_msg(conn, ret)

            except Exception as detail:
                self._send_msg(conn, {"error": "%s" % detail})
                logger.error("SchedulerServer error: %s" % detail)
            finally:
                conn.close()

    def _stop_scheduler(self):
        # Start the background scheduler
        if self.background_scheduler.running:
            self.background_scheduler.shutdown()

    def start(self, *args, **kwargs):
        # Start the server in a thread
        threading.Thread(target=self._start_server, daemon=self.daemon).start()
        # Start the background scheduler
        self.background_scheduler.start(*args, **kwargs)

    def shutdown(self):
        # Stop the thread
        self.client.send_shutdown()
        self._stop_scheduler()
        print("Stopped")
