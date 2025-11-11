#! /bin/env python3

''' Extract a metric and print its average for a specific time range '''

# pylint: disable=too-many-locals,too-many-branches

import argparse
import numpy as np

def parse_start_time(line):
    ''' parse the start time ine first line '''
    line = line.replace('# start_time: ', '').replace('\n', '')
    start_time = int(line)
    print(f"Start time was {start_time}")
    return start_time

def extract_metric(path, metric, start_time, end_time):
    ''' Get the average of the specified metric in the specified time interval '''

    names = ['cpu_usage', 'compute_utilization',
             'active_transactions', 'running_jobs',
             'blocked_jobs', 'ready_jobs',
             'total_objects', 'job_runtime']
    num_metrics = len(names)

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

    value = extract_metric(args.path, args.metric, args.start_time, args.end_time)
    print(str(value))

if __name__ == "__main__":
    _main()
