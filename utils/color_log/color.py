import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message: str, use_color: bool=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    # 'INFO': WHITE,
    'INFO': GREEN,
    'DEBUG': BLUE,
    # 'CRITICAL': YELLOW,
    'CRITICAL': CYAN,
    'ERROR': RED,
    'VERBOSE': MAGENTA,
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

### for convenience calling
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
VERBOSE = DEBUG+1
NOTSET = 0


# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):
    # FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    # FORMAT = "[$BOLD%(name)s$RESET][%(levelname)s] %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    FORMAT = "[%(levelname)s] %(message)s ($BOLD%(pathname)s$RESET:%(lineno)d)"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    def __init__(self, name: str, level: int=logging.INFO):
        logging.Logger.__init__(self, name, level=level)
        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return
    # Custom log level
    logging.addLevelName(VERBOSE, "VERBOSE")
    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(VERBOSE):
            # Yes, logger takes its '*args' as 'args'.
            self._log(VERBOSE, message, args, **kws) 
    logging.Logger.verbose = verbose


def setup(
  name: str='Main',
  level=logging.DEBUG,
  ):
  '''
  Quick setup for the color logger.
  '''
  logging.setLoggerClass(ColoredLogger)
  _color_logger = logging.getLogger(name)
  _color_logger.setLevel(level)
  return _color_logger

def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30, 38):
            s1 = ''
            for bg in range(40, 48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')

# https://www.geeksforgeeks.org/print-colors-python-terminal/
def bg_black(skk):
    return "\033[40m{}\033[00m" .format(skk)
def bg_red(skk):
    return "\033[41m{}\033[00m" .format(skk)
def bg_green(skk):
    return "\033[42m{}\033[00m" .format(skk)
def bg_yellow(skk):
    return "\033[43m{}\033[00m" .format(skk)
def bg_blue(skk):
    return "\033[44m{}\033[00m" .format(skk)
def bg_purple(skk):
    return "\033[45m{}\033[00m" .format(skk)
def bg_cyan(skk):
    return "\033[46m{}\033[00m" .format(skk)
def bg_lightgrey(skk):
    return "\033[47m{}\033[00m" .format(skk)

def tt_red(skk):
    return "\033[91m{}\033[00m" .format(skk)
def tt_green(skk):
    return "\033[92m{}\033[00m" .format(skk)
def tt_yellow(skk):
    return "\033[93m{}\033[00m" .format(skk)
def tt_lightpurple(skk):
    return "\033[94m{}\033[00m" .format(skk)
def tt_purple(skk):
    return "\033[95m{}\033[00m" .format(skk)
def tt_cyan(skk):
    return "\033[96m{}\033[00m" .format(skk)
def tt_lightgray(skk):
    return "\033[97m{}\033[00m" .format(skk)
def tt_black(skk):
    return "\033[98m{}\033[00m" .format(skk)





if __name__ == "__main__":
  logging.setLoggerClass(ColoredLogger)
#   color_log = logging.getLogger("Sniffer")
#   color_log.setLevel(logging.DEBUG)

#   color_log.debug("test")
#   color_log.info("test")
#   color_log.warning("test")
#   color_log.error("test")
#   color_log.critical("test")
  
#   print_format_table()
  print(bg_yellow('test quick setup: '))

  color_logger = setup(name=__name__, level=INFO)
#   color_logger = setup(name=__name__, level=DEBUG)
#   color_logger = setup(name=__name__, level=ERROR)
  color_logger.debug('Demo log ==> "debug"')
  color_logger.info('Demo log ==> "info"')
  color_logger.warning('Demo log ==> "warning"')
  color_logger.error('Demo log ==> "error"')
  color_logger.critical('Demo log ==> "critical"')
  color_logger.verbose('Demo log ==> "verbose"')
  
  print(bg_black('bg_black'))
  print(bg_red('bg_red'))
  print(bg_green('bg_green'))
  print(bg_yellow('bg_yellow'))
  print(bg_blue('bg_blue'))
  print(bg_purple('bg_purple'))
  print(bg_cyan('bg_cyan'))
  print(bg_lightgrey('bg_lightgrey'))
  print(tt_red('tt_red'))
  print(tt_green('tt_green'))
  print(tt_yellow('tt_yellow'))
  print(tt_lightpurple('tt_lightpurple'))
  print(tt_purple('tt_purple'))
  print(tt_cyan('tt_cyan'))
  print(tt_lightgray('tt_lightgray'))
  print(tt_black('tt_black'))