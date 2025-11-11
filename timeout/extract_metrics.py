#! /bin/env python3

''' Extract a metric and print its average for a specific time range '''

# pylint: disable=too-many-locals,too-many-branches

import argparse
import numpy as np

def parse_start_time(line):
    ''' parse the start time ine first line '''
    line = line.replace('# start_time: ', '').replace('\n', '')
    return int(line)

def extract_metric(path, metric, start_time, end_time):
    ''' Get the average of the specified metric in the specified time interval '''

    names = [
        'cpu-usage', 'compute-utilization', 'active-transactions',
        'running-jobs', 'blocked-jobs', 'ready-jobs',
         'num-objects', 'throughput', 'abort-rate', 'job-runtime',
    ]
    global_names = [
        'total-job-runtime', 'total-throughput', 'num-full-replicas',
        'num-light-replicas', 'num-shards'
    ]

    num_metrics = len(names)
    num_global_metrics = len(global_names)

    metric_idx = None
    for (idx, name) in enumerate(names):
        if metric == name:
            metric_idx = idx
            break
    if metric_idx is None:
        raise RuntimeError(f"No such metric {metric}")

    data = []
    measure_start_time = None

    with open(path, 'r', encoding='utf-8') as infile:
        for (line_no, line) in enumerate(infile.readlines()):
            if line_no == 0:
                measure_start_time = parse_start_time(line)
                continue

            time = measure_start_time + (line_no-1) * 100
            if start_time <= time <= end_time:
                entries = [float(v) for v in line.replace('\n', '').split(',')]
                entries = entries[:-num_global_metrics]

                assert len(entries) % num_metrics == 0
                num_nodes = int(len(entries) / num_metrics)

                for node_idx in range(num_nodes):
                    pos = node_idx * num_metrics + metric_idx
                    data.append(entries[pos])

    if len(data) == 0:
        raise RuntimeError("No data found in this time range")

    return np.mean(data)

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str)
    parser.add_argument('metric', type=str)
    parser.add_argument('start_time', type=int)
    parser.add_argument('end_time', type=int)
    args = parser.parse_args()

    extract_metric(args.path, args.metric, args.start_time,
                   args.end_time)

if __name__ == "__main__":
    _main()
