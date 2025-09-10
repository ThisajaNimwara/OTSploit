#!/usr/bin/env python3

from __future__ import print_function
import os
import sys
import itertools
import traceback
import atexit
from collections import Counter
import queue
import threading

try:
    if sys.platform == "darwin":
        import gnureadline as readline
    elif sys.platform == "win32":
        try:
            import pyreadline3 as readline
        except ImportError:
            try:
                import readline
            except ImportError:
                # Fallback for Windows without readline
                class DummyReadline:
                    def read_history_file(self, *args): pass
                    def write_history_file(self, *args): pass
                    def set_history_length(self, *args): pass
                    def parse_and_bind(self, *args): pass
                    def set_completer(self, *args): pass
                    def set_completer_delims(self, *args): pass
                    def get_line_buffer(self): return ""
                    def get_begidx(self): return 0
                    def get_endidx(self): return 0
                readline = DummyReadline()
    else:
        import readline
except ImportError:
    # Fallback for systems without readline
    class DummyReadline:
        def read_history_file(self, *args): pass
        def write_history_file(self, *args): pass
        def set_history_length(self, *args): pass
        def parse_and_bind(self, *args): pass
        def set_completer(self, *args): pass
        def set_completer_delims(self, *args): pass
        def get_line_buffer(self): return ""
        def get_begidx(self): return 0
        def get_endidx(self): return 0
    readline = DummyReadline()

from OTSploit.utils import print_info, print_error, print_status, OTSploitException
from OTSploit.exploits import GLOBAL_OPTS
from OTSploit import utils

# Define a basic PrinterThread since it was not provided
printer_queue = queue.Queue()

class PrinterThread(threading.Thread):
    """Thread to handle printing from the printer queue."""
    def run(self):
        while True:
            try:
                message = printer_queue.get()
                if message is None:
                    break
                print(message)
                printer_queue.task_done()
            except Exception as e:
                print_error(f"PrinterThread error: {str(e)}")

class BaseInterpreter:
    history_file = os.path.expanduser("~/.history")
    history_length = 100
    global_help = ""

    def __init__(self):
        self.setup()
        self.banner = ""

    def setup(self):
        """Initialize third-party libraries, setting interpreter history and completer."""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'a+'):
                pass

        readline.read_history_file(self.history_file)
        readline.set_history_length(self.history_length)
        atexit.register(readline.write_history_file, self.history_file)

        readline.parse_and_bind('set enable-keypad on')
        readline.set_completer(self.complete)
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")

    def parse_line(self, line):
        """Split line into command and argument."""
        command, _, arg = line.strip().partition(" ")
        return command, arg.strip()

    @property
    def prompt(self):
        """Returns prompt string."""
        return ">>>"

    def get_command_handler(self, command):
        """Parse command and return appropriate handler."""
        try:
            command_handler = getattr(self, f"command_{command}")
        except AttributeError:
            try:
                command_handler = getattr(self.current_module, f"command_{command}")
            except AttributeError:
                raise OTSploitException(f"Unknown command: '{command}'")
        return command_handler

    def start(self):
        """OTSploit main entry point. Starting interpreter loop."""
        print_info(self.banner)
        printer_queue.join()
        while True:
            try:
                command, args = self.parse_line(input(self.prompt))
                if not command:
                    continue
                command_handler = self.get_command_handler(command)
                command_handler(args)
            except OTSploitException as err:
                print_error(str(err))
            except EOFError:
                print_info()
                print_status("OTSploit stopped")
                break
            except KeyboardInterrupt:
                print_info()
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
                print_error(traceback.format_exc())
            finally:
                printer_queue.join()

    def complete(self, text, state):
        """Return the next possible completion for 'text'."""
        if state == 0:
            original_line = readline.get_line_buffer()
            line = original_line.lstrip()
            stripped = len(original_line) - len(line)
            start_index = readline.get_begidx() - stripped
            end_index = readline.get_endidx() - stripped

            if start_index > 0:
                cmd, args = self.parse_line(line)
                if cmd == '':
                    complete_function = self.default_completer
                else:
                    try:
                        complete_function = getattr(self, f'complete_{cmd}')
                    except AttributeError:
                        complete_function = self.default_completer
            else:
                complete_function = self.raw_command_completer

            self.completion_matches = complete_function(text, line, start_index, end_index)

        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def commands(self, *ignored):
        """Returns full list of interpreter commands."""
        return [command.rsplit("_").pop() for command in dir(self) if command.startswith("command_")]

    def raw_command_completer(self, text, line, start_index, end_index):
        """Complete command w/o any argument."""
        return [cmd for cmd in self.suggested_commands() if cmd.startswith(text)]

    def default_completer(self, *ignored):
        return []

    def suggested_commands(self):
        """Entry point for intelligent tab completion."""
        return self.commands()

class OTsploitInterpreter(BaseInterpreter):
    history_file = os.path.expanduser("~/.otsploit_history")
    global_help = """Global commands:
    help                        Print this help menu
    use <module>                Select a module for usage
    exec <shell command> <args> Execute a command in a shell
    search <search term>        Search for appropriate module
    exit                        Exit OTSploit"""

    module_help = """Module commands:
    run                                 Run the selected module with the given options
    back                                De-select the current module
    set <option name> <option value>    Set an option for the selected module
    setg <option name> <option value>   Set an option for all of the modules
    unsetg <option name>                Unset option that was set globally
    show [info|options|devices]         Print information, options, or target devices for a module
    check                               Check if a given target is vulnerable to a selected module's exploit"""

    def __init__(self, extra_package_path=None):
        super().__init__()
        PrinterThread().start()
        self.current_module = None
        self.raw_prompt_template = None
        self.module_prompt_template = None
        self.prompt_hostname = 'otsploit'
        self.show_sub_commands = (
            'info', 'options', 'devices', 'all', 'creds', 'exploits', 'scanners',
            'plcs_schneider', 'plcs_rockwell', 'plcs_omron', 'plcs_phoenix',
            'ics_software_realwin', 'ics_software_openplc'
        )
        self.global_commands = sorted(['use ', 'exec ', 'help', 'exit', 'show ', 'search '])
        self.module_commands = ['run', 'back', 'set ', 'setg ', 'check']
        self.module_commands.extend(self.global_commands)
        self.module_commands.sort()
        self.extra_modules_dir = None
        self.extra_modules_dirs = None
        self.extra_modules = []
        self.extra_package_path = extra_package_path
        self.import_extra_package()
        self.modules = utils.index_modules('OTSploit/modules')
        self.modules += self.extra_modules
        self.modules_count = Counter()
        for module in self.modules:
            self.modules_count.update(module.split('.'))
            if module.startswith('extra_exploits.plcs.schneider'):
                self.modules_count['plcs_schneider'] += 1
            elif module.startswith('extra_exploits.plcs.rockwell'):
                self.modules_count['plcs_rockwell'] += 1
            elif module.startswith('extra_exploits.plcs.omron'):
                self.modules_count['plcs_omron'] += 1
            elif module.startswith('extra_exploits.plcs.phoenix'):
                self.modules_count['plcs_phoenix'] += 1
            elif module.startswith('extra_exploits.ics_software.realwin'):
                self.modules_count['ics_software_realwin'] += 1
            elif module.startswith('extra_exploits.ics_software.openplc'):
                self.modules_count['ics_software_openplc'] += 1
        modules_dir = 'OTSploit/modules'
        self.main_modules_dirs = [module for module in os.listdir(modules_dir) if not module.startswith("__")]
        self.__parse_prompt()

        self.banner = """
                OT Exploitation Framework
Welcome ! Come Come
        """

    def __parse_prompt(self):
        raw_prompt_default_template = "\001\033[4m\002{host}\001\033[0m\002 > "
        raw_prompt_template = os.getenv("OTSPLOIT_RAW_PROMPT", raw_prompt_default_template).replace('\\033', '\033')
        self.raw_prompt_template = raw_prompt_template if '{host}' in raw_prompt_template else raw_prompt_default_template

        module_prompt_default_template = "\001\033[4m\002{host}\001\033[0m\002 (\001\033[91m\002{module}\001\033[0m\002) > "
        module_prompt_template = os.getenv("OTSPLOIT_MODULE_PROMPT", module_prompt_default_template).replace('\\033', '\033')
        self.module_prompt_template = module_prompt_template if all(
            map(lambda x: x in module_prompt_template, ['{host}', "{module}"])) else module_prompt_default_template

    @property
    def module_metadata(self):
        return getattr(self.current_module, f"_{self.current_module.__class__.__name__}__info__")

    @property
    def prompt(self):
        """Returns prompt string based on current_module attribute."""
        if self.current_module:
            try:
                return self.module_prompt_template.format(host=self.prompt_hostname,
                                                         module=self.module_metadata['name'])
            except (AttributeError, KeyError):
                return self.module_prompt_template.format(host=self.prompt_hostname, module="UnnamedModule")
        else:
            return self.raw_prompt_template.format(host=self.prompt_hostname)

    def import_extra_package(self):
        if self.extra_package_path:
            extra_modules_dir = os.path.join(self.extra_package_path, "extra_modules")
            try:
                if os.path.isdir(extra_modules_dir):
                    self.extra_modules_dir = extra_modules_dir
                    self.extra_modules_dirs = [module for module in os.listdir(self.extra_modules_dir) if
                                               not module.startswith("__")]
                    self.extra_modules = utils.index_extra_modules(modules_directory=self.extra_modules_dir)
                    print_info(f"Extra modules directory: {self.extra_modules_dir}")
                    sys.path.append(self.extra_package_path)
                    sys.path.append(self.extra_modules_dir)
                else:
                    print_error(f"Extra modules directory not found: {extra_modules_dir}")
            except Exception as e:
                print_error(f"Failed to import extra modules: {str(e)}")
        else:
            print_status("No extra package path provided")

    def available_modules_completion(self, text):
        """Looking for tab completion hints."""
        text = utils.pythonize_path(text)
        all_possible_matches = [module for module in self.modules if module.startswith(text)]
        matches = set()
        for match in all_possible_matches:
            head, sep, tail = match[len(text):].partition('.')
            if not tail:
                sep = ""
            matches.add("".join((text, head, sep)))
        return list(map(utils.humanize_path, matches))

    def suggested_commands(self):
        """Entry point for intelligent tab completion."""
        if self.current_module and GLOBAL_OPTS:
            return sorted(itertools.chain(self.module_commands, ('unsetg ',)))
        elif self.current_module:
            custom_commands = [command.rsplit("_").pop() for command in dir(self.current_module)
                               if command.startswith("command_")]
            self.module_commands.extend(custom_commands)
            return self.module_commands
        else:
            return self.global_commands

    def command_back(self, *args, **kwargs):
        self.current_module = None

    def command_use(self, module_path, *args, **kwargs):
        if module_path.startswith("extra_"):
            module_path = utils.pythonize_path(module_path)
        else:
            module_path = utils.pythonize_path(module_path)
            module_path = '.'.join(('OTSploit', 'modules', module_path))
        try:
            self.current_module = utils.import_exploit(module_path)()
        except OTSploitException as err:
            print_error(str(err))

    @utils.stop_after(2)
    def complete_use(self, text, *args, **kwargs):
        if text:
            return self.available_modules_completion(text)
        else:
            if self.extra_modules_dirs:
                extra_subdirs = []
                for module in self.extra_modules_dirs:
                    module_path = os.path.join(self.extra_modules_dir, module)
                    if os.path.isdir(module_path):
                        subdirs = [f"{module}/{sub}" for sub in os.listdir(module_path) if
                                   not sub.startswith("__") and os.path.isdir(os.path.join(module_path, sub))]
                        extra_subdirs.extend(subdirs)
                return self.main_modules_dirs + self.extra_modules_dirs + extra_subdirs
            else:
                return self.main_modules_dirs

    @utils.module_required
    def command_run(self, *args, **kwargs):
        print_status("Running module...")
        try:
            self.current_module.run()
        except KeyboardInterrupt:
            print_info()
            print_error("Operation cancelled by user")
        except Exception as e:
            print_error(f"Module execution failed: {str(e)}")
            print_error(traceback.format_exc())

    def command_exploit(self, *args, **kwargs):
        self.command_run()

    @utils.module_required
    def command_set(self, *args, **kwargs):
        key, _, value = args[0].partition(' ')
        if key in self.current_module.options:
            try:
                setattr(self.current_module, key, value)
                if kwargs.get("glob", False):
                    GLOBAL_OPTS[key] = value
                print_success({key: value})
            except ValueError as e:
                print_error(str(e))
        else:
            print_error(
                f"You can't set option '{key}'.\nAvailable options: {self.current_module.options}")

    @utils.stop_after(2)
    def complete_set(self, text, *args, **kwargs):
        if text:
            return [' '.join((attr, "")) for attr in self.current_module.options if attr.startswith(text)]
        else:
            return self.current_module.options

    @utils.module_required
    def command_setg(self, *args, **kwargs):
        kwargs['glob'] = True
        self.command_set(*args, **kwargs)

    @utils.stop_after(2)
    def complete_setg(self, text, *args, **kwargs):
        return self.complete_set(text, *args, **kwargs)

    @utils.module_required
    def command_unsetg(self, *args, **kwargs):
        key, _, value = args[0].partition(' ')
        try:
            del GLOBAL_OPTS[key]
            print_success({key: None})
        except KeyError:
            print_error(
                f"You can't unset global option '{key}'.\nAvailable global options: {GLOBAL_OPTS.keys()}")

    @utils.stop_after(2)
    def complete_unsetg(self, text, *args, **kwargs):
        if text:
            return [' '.join((attr, "")) for attr in GLOBAL_OPTS.keys() if attr.startswith(text)]
        else:
            return list(GLOBAL_OPTS.keys())

    @utils.module_required
    def get_opts(self, *args):
        """Generator returning module's Option attributes."""
        for opt_key in args:
            try:
                opt_description = self.current_module.exploit_attributes[opt_key]
                opt_value = getattr(self.current_module, opt_key)
            except (KeyError, AttributeError):
                pass
            else:
                yield opt_key, opt_value, opt_description

    @utils.module_required
    def _show_info(self, *args, **kwargs):
        utils.pprint_dict_in_order(
            self.module_metadata,
            ("name", "description", "devices", "authors", "references"),
        )
        print_info()

    @utils.module_required
    def _show_options(self, *args, **kwargs):
        target_opts = [opt for opt in self.current_module.options if opt in ['target', 'port']]
        module_opts = [opt for opt in self.current_module.options if opt not in ['target', 'port']]
        headers = ("Name", "Current settings", "Description")

        if target_opts:
            print_info('\nTarget options:')
            utils.print_table(headers, *self.get_opts(*target_opts))

        if module_opts:
            print_info('\nModule options:')
            utils.print_table(headers, *self.get_opts(*module_opts))

        print_info()

    @utils.module_required
    def _show_devices(self, *args, **kwargs):
        try:
            devices = self.module_metadata['devices']
            print_info("\nTarget devices:")
            for i, device in enumerate(devices):
                if isinstance(device, dict):
                    print_info(f"   {i} - {device['name']}")
                else:
                    print_info(f"   {i} - {device}")
            print_info()
        except KeyError:
            print_info("\nTarget devices are not defined")

    def __show_modules(self, root=''):
        for module in sorted([module for module in self.modules if module.startswith(root)]):
            print_info(module.replace('.', os.sep))

    def _show_all(self, *args, **kwargs):
        self.__show_modules()

    def _show_scanners(self, *args, **kwargs):
        self.__show_modules('scanners')

    def _show_exploits(self, *args, **kwargs):
        self.__show_modules('exploits')

    def _show_creds(self, *args, **kwargs):
        self.__show_modules('creds')

    def _show_plcs_schneider(self, *args, **kwargs):
        self.__show_modules('extra_exploits.plcs.schneider')

    def _show_plcs_rockwell(self, *args, **kwargs):
        self.__show_modules('extra_exploits.plcs.rockwell')

    def _show_plcs_omron(self, *args, **kwargs):
        self.__show_modules('extra_exploits.plcs.omron')

    def _show_plcs_phoenix(self, *args, **kwargs):
        self.__show_modules('extra_exploits.plcs.phoenix')

    def _show_ics_software_realwin(self, *args, **kwargs):
        self.__show_modules('extra_exploits.ics_software.realwin')

    def _show_ics_software_openplc(self, *args, **kwargs):
        self.__show_modules('extra_exploits.ics_software.openplc')

    def command_show(self, *args, **kwargs):
        sub_command = args[0] if args else ''
        try:
            getattr(self, f"_show_{sub_command}")(*args, **kwargs)
        except AttributeError:
            print_error(f"Unknown 'show' sub-command '{sub_command}'. "
                        f"What do you want to show?\nPossible choices are: {self.show_sub_commands}")

    @utils.stop_after(2)
    def complete_show(self, text, *args, **kwargs):
        if text:
            return [command for command in self.show_sub_commands if command.startswith(text)]
        else:
            return self.show_sub_commands

    @utils.module_required
    def command_check(self, *args, **kwargs):
        try:
            result = self.current_module.check()
        except Exception as e:
            print_error(f"Check failed: {str(e)}")
        else:
            if result is True:
                print_success("Target is vulnerable")
            elif result is False:
                print_error("Target is not vulnerable")
            else:
                print_status("Target could not be verified")

    def command_help(self, *args, **kwargs):
        print_info(self.global_help)
        if self.current_module:
            print_info("\n", self.module_help)

    def command_exec(self, *args, **kwargs):
        if args:
            os.system(args[0])
        else:
            print_error("No shell command provided")

    def command_search(self, *args, **kwargs):
        keyword = args[0] if args else ''
        if not keyword:
            print_error("Please specify search keyword. e.g. 'search plc'")
            return
        for module in sorted(self.modules):
            if keyword.lower() in module.lower():
                module = utils.humanize_path(module)
                print_info(
                    f"{module.partition(keyword.lower())[0]}\033[31m{keyword.lower()}\033[0m{module.partition(keyword.lower())[2]}"
                )

    def command_exit(self, *args, **kwargs):
        raise EOFError