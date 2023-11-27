#!/usr/bin/python

import os,sys,re,argparse

SYS_DIR = "/sys/devices/system/cpu/"
def sys_cpu_dir(cpu, f):
    return os.path.join(SYS_DIR, f"cpu{cpu}", f)

#Set a CPU on/off
def cpu_online(cpu, online):
    assert online in [0, 1]
    with open(sys_cpu_dir(cpu, "online"), "w") as f:
        f.write(str(online))

#Set a CPU governor
def set_governor(cpu, governor):
    with open(sys_cpu_dir(cpu, "cpufreq/scaling_governor"), "w") as f:
        f.write(governor)

#Set energy performance
def set_energy_performance(cpu, energy):
    with open(sys_cpu_dir(cpu, "cpufreq/energy_performance_preference"), "w") as f:
        f.write(energy)

#Set maximum frequency
def set_scaling_max_freq(cpu, freq):
    with open(sys_cpu_dir(cpu, "cpufreq/scaling_max_freq"), "w") as f:
        f.write(str(freq))

#Set minimum frequency
def set_scaling_min_freq(cpu, freq):
    assert freq in [0, 1]
    with open(sys_cpu_dir(cpu, "cpufreq/scaling_min_freq"), "w") as f:
        f.write(str(freq))

def get_available_governors():
    with open(sys_cpu_dir(0, "cpufreq/scaling_available_governors"), "r") as f:
        return f.read().strip().split(' ')

def get_energy_performances():
    with open(sys_cpu_dir(0, "cpufreq/energy_performance_available_preferences"), "r") as f:
        return f.read().strip().split(' ')

def get_all_cpus():
    all_cpus = []
    
    for d in os.listdir(SYS_DIR):
        if re.findall(r'cpu(\d+)', d) != []:
            all_cpus += [int(c) for c in re.findall(r'cpu(\d+)', d)]
    return sorted(all_cpus)

def get_max_freq():
    with open(sys_cpu_dir(0, "cpufreq/cpuinfo_max_freq"), "r") as f:
        return int(f.read())

def main(online_cpus, governor, energy, max_freq):
    all_cpus = get_all_cpus()
    governors = get_available_governors()
    energy_performances = get_energy_performances()
    scaling_max_frequency = get_max_freq()
    
    if governor not in governors:
        print(f"Error invalid governor {governor}. Available governors {governors}")
        return
    
    if energy not in energy_performances:
        print(f"Error invalid energy preference {energy}. Available preferences {energy_performances}")
        return

    if max_freq > scaling_max_frequency:
        print(f"Error invalid max freq {max_freq} KHz. Available max frequency is {scaling_max_frequency} KHz")

    def other_cpus(all_cpus, cpus):
        return sorted(list(set(all_cpus) - set(cpus)))

    #Set only online CPUs
    for cpu in online_cpus:
        if cpu == 0:
            continue
        cpu_online(cpu, 1)

    #Set all other CPUs (except 0) to offline
    for cpu in other_cpus(all_cpus, online_cpus):
        if cpu == 0:
            continue
        cpu_online(cpu, 0)
    
    for cpu in online_cpus:
        set_governor(cpu, governor)
        set_energy_performance(cpu, energy)
        set_scaling_max_freq(cpu, max_freq)

if "__main__" == __name__:
    parser = argparse.ArgumentParser(prog='CPU Power Set', description='', epilog='')
    parser.add_argument('-cpus', nargs="+", required=True, action='append', type=int, help=f"Available CPUs {get_all_cpus()}")
    parser.add_argument('-governor', required=True, type=str, help=f"Should be one of {get_available_governors()}")
    parser.add_argument('-energy_preference', required=True, type=str, help=f"Should be one of {get_energy_performances()}")
    parser.add_argument('-max_freq', required=True, type=float,help=f"Max frequency in GHz. Must be less than {get_max_freq()/1e6} GHz")

    args = parser.parse_args()
    main(args.cpus[0], args.governor, args.energy_preference, int(args.max_freq * 1e6))