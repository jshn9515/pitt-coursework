import logging
import subprocess
import sys
import time

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

logging.info('===== Running Test 1 =====')
subprocess.run([PYTHON, 'run_test_1.py'])

time.sleep(2)

logging.info('===== Running Test 2 =====')
subprocess.run([PYTHON, 'run_test_2.py'])

logging.info('===== All tests finished =====')
