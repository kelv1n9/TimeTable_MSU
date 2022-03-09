import sys
from loguru import logger

logger.remove()
logger.add(sys.stderr, format="<level>{message}</level>")
logger.add('log.txt', format='{time:YYYY-MM-DD at HH:mm:ss.SSSSSSZ} | {level} | {message}')
