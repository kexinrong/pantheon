#!/usr/bin/env python

import os
import re
import sys
import math
import json
import pantheon_helpers
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.markers as markers
import matplotlib.ticker as ticker
from os import path
from time import strftime
from datetime import datetime
from helpers.pantheon_help import check_output, get_friendly_names, Popen, PIPE
from helpers.parse_arguments import parse_arguments


class Export:
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        analyze_dir = path.dirname(__file__)
        self.src_dir = path.abspath(path.join(analyze_dir, '../src'))

        # load pantheon_metadata.json as a dictionary
        metadata_fname = path.join(self.data_dir, 'pantheon_metadata.json')
        try:
            with open(metadata_fname) as metadata_file:
                metadata_dict = json.load(metadata_file)
        except:
            print "No metadata"
            exit(0)

        self.metadata_dict = metadata_dict

        self.run_times = self.metadata_dict['run_times']
        self.runtime = metadata_dict['runtime']
        self.cc_schemes = "copa pcc verus koho_cc taova webrtc scream default_tcp vegas sprout ledbat quic".split()
        self.flows = int(metadata_dict['flows'])
        self.timezone = None

    def parse_logs(self, stats_logname, datalink_logname):
        stats_log = open(stats_logname)

        start_time = None
        end_time = None
        throughput = None
        delay = None
        loss_rate = None
        worst_abs_ofst = None

        for line in stats_log:
            ret = re.match(r'Start at: (.*)', line)
            if ret:
                start_time = ret.group(1).rsplit(' ', 1)
                if not self.timezone:
                    self.timezone = start_time[1]
                start_time = start_time[0]
                continue

            ret = re.match(r'End at: (.*)', line)
            if ret:
                end_time = ret.group(1).rsplit(' ', 1)[0]
                continue

            ret = re.match(r'Worst absolute clock offset: (.*?) ms', line)
            if ret:
                worst_abs_ofst = float(ret.group(1))
                continue

        stats_log.close()

        cmd = ['mm-tunnel-throughput', '500', datalink_logname]
        proc = Popen(cmd, stdout=DEVNULL, stderr=PIPE)
        results = proc.communicate()[1]
        assert proc.returncode == 0

        ret = re.search(r'Average throughput: (.*?) Mbit/s', results)

        assert ret
        if not throughput:
            throughput = float(ret.group(1))


        ret = re.search(r'Loss rate: (.*?)%', results)
        assert ret
        if not loss_rate:
            loss_rate = float(ret.group(1))

        cmd = ['mm-tunnel-delay', datalink_logname]
        proc = Popen(cmd, stdout=DEVNULL, stderr=PIPE)
        results = proc.communicate()[1]
        assert proc.returncode == 0

        ret = re.search(r'95th percentile per-packet one-way delay: '
                        '(.*?) ms', results)
        assert ret
        if not delay:
            delay = float(ret.group(1))

        return (start_time, end_time, throughput, delay, worst_abs_ofst, loss_rate)

    def generate_data(self):
        self.data = {}
        self.runtimes = {}
        self.worst_abs_ofst = None
        time_format = '%a, %d %b %Y %H:%M:%S'

        if self.flows > 0:
            datalink_fmt_str = '%s_datalink_run%s.log'
        else:
            datalink_fmt_str = '%s_mm_datalink_run%s.log'

        for cc in self.cc_schemes:
            self.data[cc] = []
            self.runtimes[cc] = []
            cc_name = self.friendly_names[cc]

            for run_id in xrange(1, 1 + self.run_times):
                stats_log = path.join(
                    self.data_dir, '%s_stats_run%s.log' % (cc, run_id))
                datalink_log = path.join(
                    self.data_dir, datalink_fmt_str % (cc, run_id))
                try:
                    (start_t, end_t, tput, delay, ofst, loss) = self.parse_logs(
                                                          stats_log, datalink_log)
                except:
                    continue

                self.data[cc].append((tput, delay, loss))
                self.runtimes[cc].append((start_t, end_t))
                if ofst:
                    if not self.worst_abs_ofst or ofst > self.worst_abs_ofst:
                        self.worst_abs_ofst = ofst


    def output_to_file(self):
        f = open("pantheon_logs.csv", "a")
        # Get hashes
        git_hash = {"vegas":"default", "default_tcp": "default", 
            "ledbat": "default", "mahimahi": "default", "libutp": "default",
            "sourdough":"default", "taova": "default", "copa": "default"}
        master_hash = "default"
        if "git_information" in self.metadata_dict:
            lines = self.metadata_dict["git_information"].split("\n")

            for line in lines:
                if "master" in line:
                    i = line.find("@")
                    master_hash = line[i + 2 : -1]
                elif "third_party" in line and "@" in line:
                    i = line.find("@")
                    j = line.find("/")
                    if "quic" in line:
                        git_hash["quic"] = line[i + 2 : -1]
                    else:
                        git_hash[line[j + 1 : i - 1]] = line[i + 2 : -1]
        else:
            for cc in self.cc_schemes:
                git_hash[cc] = "default"

        for cc in self.data:
            if not cc in self.runtimes or len(self.runtimes[cc]) == 0:
                continue
            is_cellular = 0
            if "remote_interface" in self.metadata_dict and \
               self.metadata_dict["remote_interface"] == "ppp0":
               is_cellular = 1
            for i in range(len(self.data[cc])):
                start_t = "N/A"
                end_t = "N/A"
                DOW = "N/A"
                if self.runtimes[cc][i][0]:
                    idx = self.runtimes[cc][i][0].find(",")
                    DOW = self.runtimes[cc][i][0][:idx]
                    start_t = self.runtimes[cc][i][0][idx + 1:]
                    end_t = self.runtimes[cc][i][1][idx + 1:]
                f.write("%s,%f,%f,%f,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s\n"
                    %(cc, self.data[cc][i][0], self.data[cc][i][1],
                      self.data[cc][i][2],
                      git_hash[cc], master_hash, git_hash["mahimahi"],
                      git_hash["libutp"], git_hash["sourdough"],
                      DOW, start_t, end_t,
                      self.runtime,
                      is_cellular,
                      self.metadata_dict["local_information"],
                      self.metadata_dict["local_address"],
                      self.metadata_dict["remote_information"],
                      self.metadata_dict["remote_address"]))
        f.close()

    def gen_table(self):
        self.friendly_names = get_friendly_names(self.cc_schemes)
        self.generate_data()
        self.output_to_file()


def main():
    args = parse_arguments(path.basename(__file__))

    gen_table = Export(args)
    gen_table.gen_table()


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
