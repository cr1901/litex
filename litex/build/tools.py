import os
import struct
from distutils.version import StrictVersion
import re
import subprocess
import sys
import logging


def language_by_filename(name):
    extension = name.rsplit(".")[-1]
    if extension in ["v", "vh", "vo"]:
        return "verilog"
    if extension in ["vhd", "vhdl", "vho"]:
        return "vhdl"
    return None


def write_to_file(filename, contents, force_unix=False):
    newline = None
    if force_unix:
        newline = "\n"
    with open(filename, "w", newline=newline) as f:
        f.write(contents)


def arch_bits():
    return struct.calcsize("P")*8


def versions(path):
    for n in os.listdir(path):
        full = os.path.join(path, n)
        if not os.path.isdir(full):
            # logging.info("{} is not a directory.".format(full))
            continue
        try:
            # logging.info("Checking if dir {} is a StrictVersion.".format(n))
            yield StrictVersion(n)
        except ValueError:
            # logging.info("{} is not a candidate directory for tools.".format(full))
            continue


def sub_rules(line, rules, max_matches=1):
    for pattern, color in rules:
        line, matches = re.subn(pattern, color, line, max_matches)
        max_matches -= matches
        if not max_matches:
            break
    return line


def subprocess_call_filtered(command, rules, *, max_matches=1, **kwargs):
    with subprocess.Popen(command, stdout=subprocess.PIPE,
                          universal_newlines=True, bufsize=1,
                          **kwargs) as proc:
        with open(proc.stdout.fileno(), errors="ignore", closefd=False) as stdout:
            for line in stdout:
                print(sub_rules(line, rules, max_matches), end="")
        return proc.wait()
