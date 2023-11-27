# cpupower-set

A python script to set the power usage of Intel CPUs that support intel_pstate.
For example, to turn only cores 0,4,5,6, use `powersave` governor, `balance_power` as energy performance preference, and 1.5GHz of max frequency use below command:

```
sudo python startup-script.py -cpus 0 4 5 6 -governor powersave -energy_preference balance_power -max_freq 1.5
```