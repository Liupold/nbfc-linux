#!/usr/bin/python3

import sys, os, time, argparse, json

CONFIG_DIR  = '/etc/nbfc'
CONFIGS_DIR = '/etc/nbfc/configs'
CONFIG_FILE = '/etc/nbfc/nbfc.json'
STATE_FILE  = '/var/run/nbfc_service.state.json'
PID_FILE    = '/var/run/nbfc_service.pid'

def get_service_pid():
    with open(PID_FILE) as fh:
        return int(fh.read())

def json_loadf(path):
    with open(path, 'r') as fh:
        return json.load(fh)

def json_dumpf(obj, path):
    with open(path, 'w') as fh:
        json.dump(obj, fh)
        

def dmidecode_system_product():
    import dmidecode
    r = dmidecode.system()
    def find_product(d):
        if type(d) is dict:
            for key, value in d.items():
                if key == 'Product Name':
                    return str(value, encoding='UTF-8')
                r = find_product(value)
                if r:
                    return r
        else:
            return None
    return find_product(r)

def subprocess_system_product():
    import subprocess
    proc = subprocess.Popen(['dmidecode', '-s', 'system-product-name'], stdout=subprocess.PIPE)
    return str(proc.communicate()[0], encoding='UTF-8')

def find_recommended():
    def word_difference(a, b):
        a = a.lower()
        b = b.lower()
        if a == b: return 0
        diff = 0
        for a_c, b_c in zip(a, b):
            diff += abs(ord(a_c) - ord(b_c))
        return diff

    def words_difference(a, b):
        A = a.lower().split()
        B = b.lower().split()
        l = len(max(A, B))
        diff = 0
        for a, b in zip(A, B):
            diff += word_difference(a, b)
        diff /= l
        return diff

    product = None
    try:
        product = dmidecode_system_product()
    except:
        product = subprocess_system_product()

    if not product:
        raise Exception('Could not get product name')

    files = os.listdir(CONFIGS_DIR)
    files = [os.path.splitext(f)[0] for f in files]
    files = [(f, words_difference(product, f)) for f in files]
    files.sort(key=lambda f: f[1])
    return files

def config(opts):
    try:    cfg = json_loadf(CONFIG_FILE)
    except: cfg = {}

    if opts.list:
        files = os.listdir(CONFIGS_DIR)
        for f in files:
            print(os.path.splitext(f)[0])

    elif opts.recommend:
        files = find_recommended()
        if len(files) and files[0][1] == 0:
            print(files[0][0])
        else:
            for f in files[:15]:
                print(f[0])

    elif opts.set:
        if opts.set == 'auto':
            files = find_recommended()
            if len(files) and files[0][1] == 0:
                opts.set = files[0][0]
            else:
                raise Exception("Try `nbfc config -r` for recommended configs")

        cfg['SelectedConfigId'] = opts.set
        json_dumpf(cfg, CONFIG_FILE)

    elif opts.apply:
        if opts.apply == 'auto':
            files = find_recommended()
            if len(files) and files[0][1] == 0:
                opts.apply = files[0][0]
            else:
                raise Exception("Try `nbfc config -r` for recommended configs")

        cfg['SelectedConfigId'] = opts.apply
        json_dumpf(cfg, CONFIG_FILE)
        start(None)

def set(opts):
    cfg = json_loadf(CONFIG_FILE)
    if 'TargetFanSpeeds' not in cfg:
        cfg['TargetFanSpeeds'] = []
    targetFanSpeeds = cfg['TargetFanSpeeds']
    while True:
        try:
            targetFanSpeeds[opts.fan] = opts.speed
            break
        except IndexError:
            targetFanSpeeds.append(-1)
    json_dumpf(cfg, CONFIG_FILE)
    restart(None)

def status(opts):
    def print_service_status(status):
        #print('Service enabled         :', status['enabled'])
        print('Read-only               :', status['readonly'])
        print('Selected config name    :', status['config'])
        print('Temperature             :', status['temperature'])

    def print_fan_status(fan):
        print('Fan display name        :', fan['name'])
        print('Auto control enabled    :', fan['automode'])
        print('Critical mode enabled   :', fan['critical'])
        print('Current fan speed       :', fan['current_speed'])
        print('Target fan speed        :', fan['target_speed'])
        print('Fan speed steps         :', fan['speed_steps'])

    while True:
        try:
            if not os.path.exists(STATE_FILE):
                raise Exception('Service not running')

            with open(STATE_FILE) as fh:
                status = json.load(fh)

            print_service_status(status)
            for fan in status['fans']:
                print()
                print_fan_status(fan)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print('Error:', e)
        finally:
            if opts.watch is None:
                return

            try:   time.sleep(opts.watch)
            except KeyboardInterrupt: return
            print()


def start(opts):
    try:
        pid = get_service_pid()
        print('Service already running:', pid)
    except:
        if not opts:
            sys.exit(os.system('nbfc_service -f'))
        elif opts.readonly:
            sys.exit(os.system('nbfc_service -f -r'))
        else:
            sys.exit(os.system('nbfc_service -f'))

def stop(opts):
    import signal
    os.kill(get_service_pid(), signal.SIGINT)

def restart(opts):
    try:
        stop(opts)
    except:
        pass
    time.sleep(1)
    start(opts)


argp = argparse.ArgumentParser(prog='nbfc', description='NoteBook FanControl CLI Client')
subp = argp.add_subparsers(description='commands')

cmdp = subp.add_parser('start',       help='Start the service')
cmdp.add_argument('-e', '--enabled',  help='Start in enabled mode (default)', action='store_true')
cmdp.add_argument('-r', '--readonly', help='Start in read-only mode',         action='store_true')
cmdp.set_defaults(cmd=start)

cmdp = subp.add_parser('stop',        help='Stop the service')
cmdp.set_defaults(cmd=stop)

cmdp = subp.add_parser('restart',     help='Restart the service')
cmdp.add_argument('-e', '--enabled',  help='Restart in enabled mode (default)', action='store_true')
cmdp.add_argument('-r', '--readonly', help='Restart in read-only mode',         action='store_true')
cmdp.set_defaults(cmd=restart)

cmdp = subp.add_parser('status',      help='Show the service status')
agrp = cmdp.add_mutually_exclusive_group(required=True)
agrp.add_argument('-a', '--all',      help='Show service and fan status (default)', action='store_true')
agrp.add_argument('-s', '--service',  help='Show service status', action='store_true')
agrp.add_argument('-f', '--fan',      help='Show fan status',          type=int,   metavar='FAN INDEX')
cmdp.add_argument('-w', '--watch',    help='Show status periodically', type=float, metavar='SECONDS')
cmdp.set_defaults(cmd=status)

cmdp = subp.add_parser('config',        help='List or apply configs')
agrp = cmdp.add_mutually_exclusive_group(required=True)
agrp.add_argument('-l', '--list',       help='List all available configs (default)', action='store_true')
agrp.add_argument('-s', '--set',        help='Set a config', metavar='config')
agrp.add_argument('-a', '--apply',      help='Set a config and enable fan control', metavar='config')
agrp.add_argument('-r', '--recommend',  help='List configs which may work for your device', action='store_true')
cmdp.set_defaults(cmd=config)

cmdp = subp.add_parser('set',                  help='Control fan speed')
agrp = cmdp.add_mutually_exclusive_group(required=True)
agrp.add_argument('-a', '--auto',              help='Set fan speed to \'auto\'', action='store_const', dest='speed', const=-1)
agrp.add_argument('-s', '--speed', type=float, help='Set fan speed to <value>', dest='speed', metavar='PERCENT')
cmdp.add_argument('-f', '--fan',   type=int,   help='Fan index (zero based)',   metavar='FAN INDEX', default=0)
cmdp.set_defaults(cmd=set, speed=-1)

def show_help(opts):
    argp.print_help()
cmdp = subp.add_parser('help', help='Show help')
cmdp.set_defaults(cmd=show_help)
argp.set_defaults(cmd=show_help)

if __name__ == '__main__':
    if not sys.argv[0].startswith('/'):
        os.environ['PATH'] += ':.'
        os.environ['PATH'] += ':./src'

    if not os.path.isdir(CONFIG_DIR):
        os.path.mkdir(CONFIG_DIR)

    opts = argp.parse_args()
    opts.cmd(opts)
