# from .color import TTTT
from .color import setup, ColoredLogger
import logging
logging.setLoggerClass(ColoredLogger)