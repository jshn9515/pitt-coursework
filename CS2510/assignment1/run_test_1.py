import logging
import subprocess
import sys
import time

PORT = '9000'
PYTHON = sys.executable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('test.log', mode='a'),
        logging.StreamHandler(sys.stdout),
    ],
)

logging.info('[TEST1] Starting server...')
server = subprocess.Popen([PYTHON, 'server.py', '-client_ids', '1,2,3', '-port', PORT])

time.sleep(3)

logging.info('[TEST1] Starting Alice (Client 1)...')
alice = subprocess.Popen(
    [PYTHON, 'client.py', '-client_id', '1', '-server_ip', '127.0.0.1', '-port', PORT],
    stdin=subprocess.PIPE,
)

time.sleep(2)

assert alice.stdin is not None
alice.stdin.write(b'Hello from Alice\n')
alice.stdin.flush()

time.sleep(5)

logging.info('[TEST1] Starting Bob (Client 2)...')
bob = subprocess.Popen(
    [PYTHON, 'client.py', '-client_id', '2', '-server_ip', '127.0.0.1', '-port', PORT],
    stdin=subprocess.PIPE,
)

time.sleep(2)

logging.info('[TEST1] Starting Chad (Client 3)...')
chad = subprocess.Popen(
    [PYTHON, 'client.py', '-client_id', '3', '-server_ip', '127.0.0.1', '-port', PORT],
    stdin=subprocess.PIPE,
)

time.sleep(3)

logging.info('[TEST1] Test1 finished.')

for p in [alice, bob, chad, server]:
    p.terminate()
