import pandas as pd 
import json 
import argparse
import re




def read_step_timestamps(step_event_list):
    step_timestamps = []
    steps = []

    for event in step_event_list:
        step_timestamps.append(event["miliseconds_since_start"]/1000)
        steps.append(event["step_number"])

    return step_timestamps,steps

def read_time_timestamps(eyetrakcing_event_list):

    totalcount =  eyetrakcing_event_list[-1]['event_id']
    totallooktime = 0
    prev_timestamp = 0
    prev_started = False
    timestamps = totalcount * [0,]
    totallooktime_for_each_timestamp = totalcount * [0,]

    for event in eyetrakcing_event_list:
        current_timestamp = event['miliseconds_since_start']
        timestamps.append(current_timestamp/1000)
            
        if prev_started and not event['has_started_looking']:
            totallooktime += current_timestamp - prev_timestamp
            totallooktime_for_each_timestamp.append(totallooktime/1000)
        else:
            totallooktime_for_each_timestamp.append(totallooktime/1000)

            

        prev_timestamp = current_timestamp
        prev_started = event['has_started_looking']
    return timestamps,totallooktime_for_each_timestamp

def calculate_time_looking_per_step(timestamps,totallooktime_for_each_timestamp,step_timestamps,steps):

    time_spent_at_step_switch = []

    for t,step in zip(step_timestamps,steps):
        

        i = 0
        while timestamps[i] < t:
            if i >= len(timestamps)-1:
                break
            i += 1

        tt0 = totallooktime_for_each_timestamp[i-1]
        tt1 = totallooktime_for_each_timestamp[i]

        t0 = timestamps[i-1]
        t1 = timestamps[i]

        interpolated_time = tt0 + (t-t0)*(tt1-tt0)/(t1-t0)
        time_spent_at_step_switch.append((step,interpolated_time))

        time_spent_step = []
        prev_time = time_spent_at_step_switch[0][1]

    for step,time in time_spent_at_step_switch :
        
        time_spent_step.append((step,time - prev_time))
        prev_time = time

    time_spent_per_step = {}

    for step,time in time_spent_step:
        if step not in time_spent_per_step:
            time_spent_per_step[step] = time
        else:
            time_spent_per_step[step] += time

    return time_spent_per_step

def calculate_time_spent_per_step(step_timestamps, steps):
    
    time_spent = []
    prev_time = step_timestamps[0]
    for timestamp,istep in zip(step_timestamps[1:],steps[:-1]):
        
        time_spent.append((istep,timestamp - prev_time))
        prev_time = timestamp


    time_per_step = {}
    for step,time in time_spent:
        if step not in time_per_step:
            time_per_step[step] = time
        else:
            time_per_step[step] += time

    return time_per_step


def sort_event_list(event_list):
    return sorted(event_list,key = lambda x : x["event_id"])

def get_date_from_path(path):
    match = re.search(".*//(.*).txt", path)
    
    return match.group(1) if match != None else "date not found"
parser = argparse.ArgumentParser("convert data to csv")
parser.add_argument("files", help="paths to .txt file with data", type=argparse.FileType('r'),nargs="+")
parser.add_argument("out", help="output flie", type=argparse.FileType('w'),nargs=1)
args = parser.parse_args()


column_names = ["time","mode"]
column_names += [f"t_step_{x}" for x in range(1,16)]
column_names += [f"t_look_step_{x}" for x in range(1,16)]
df = pd.DataFrame(columns=column_names)
for file in args.files:
    data_json = json.load(file)

    event_step_data = sort_event_list(data_json["step_switches"])
    
    eyetracking_event_data = sort_event_list(data_json["eye_tracking_data"]["Image"])

    step_timestamps,steps = read_step_timestamps(event_step_data)
    timestamps,totallooktime_for_each_timestamp = read_time_timestamps(eyetracking_event_data)

    time_spent_per_step = calculate_time_spent_per_step(step_timestamps,steps)
    time_looking_per_step = calculate_time_looking_per_step(timestamps,totallooktime_for_each_timestamp,step_timestamps,steps)
    time_s = [0]+[time_spent_per_step[x] for x in time_spent_per_step]
    time_l = [time_looking_per_step[x] for x in time_looking_per_step]

    date = get_date_from_path(file.name)

    data = [date,""] + time_s + time_l
    data_df = pd.DataFrame([data],columns=column_names)
    df = pd.concat([df,data_df])


df.to_csv(args.out[0],header=True)
    