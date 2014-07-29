import math
import matplotlib.pyplot as plt

def hex(s):
    return int(s, 16)

time_error = [0.0, 2.5, 0.2, 3.3]

top = 1 #the id of the top detector
bot = 3 #the id of the bottom detector
height = 7.0 #the height in ft
fs = [open("trial2data")] #the files to read

data = [[-1, -1]]

n_time = {}

popped = 0
unpopped = 0
i = 0

start_time = 0.0
end_time = 0.0
secs_from_days = 0.0

for f in fs:
    for line in f:
        if line[0:2] == "ST" or line[0:2] == "DS":
            continue
        if end_time > float(line[42:44])*3600.0 + float(line[44:46])*60.0 + float(line[46:52]):
            secs_from_days += 86400
        end_time = float(line[42:44])*3600.0 + float(line[44:46])*60.0 + float(line[46:52])
        if i == 0:
            start_time = end_time 
        if (hex(line[9:11]) >> 7) & 1:
            if -1 in data[i]:
                popped += 1
                print "pop at byte", f.tell()
                print data[i]
                data.pop()
                i -= 1
            else:
                unpopped += 1
            i += 1
            data.append([-1, -1])
            lines = []
        lines.append(line)
        #top detector
        if (hex(line[9+6*top:11+6*top]) >> 5) & 1 and data[i][0] == -1:
            data[i][0] = hex(line[0:8])*40.0 + 1.25*(hex(line[9+6*top:11+6*top]) & 0x1F) + time_error[top]
        #if (hex(line[9+3+6*top:11+3+6*top]) >> 5) & 1 and data[i][1] == -1:
        #    data[i][1] = hex(line[0:8])*40.0 + 1.25*(hex(line[9+3+6*top:11+3+6*top]) & 0x1F) + time_error[top]
        #bottom detector
        if (hex(line[9+6*bot:11+6*bot]) >> 5) & 1 and data[i][1] == -1:
            data[i][1] = hex(line[0:8])*40.0 + 1.25*(hex(line[9+6*bot:11+6*bot]) & 0x1F) + time_error[bot]

#finished reading data, start printing
of = open("speed data.txt", 'w')

print "bad signals (missing 1 or more edges) =", popped
print "good signals = ", unpopped

mean_time = 0
mean_speed = 0
time_num = 0
speed_num = 0
h = []

clock_time = 1.25

for mu in data:
    if(abs(mu[0]-mu[1]) > 100.0):
        print ">100ns:", mu[0], " ", mu[1], " ", mu[1]-mu[0]
    else:
        h.append((mu[1]-mu[0]))
        of.write(str(mu[1]-mu[0]))
        of.write("\n")
        time_num += 1
        mean_time += mu[1]-mu[0]
        if mu[1]-mu[0] != 0.0:
            mean_speed += height/(mu[1]-mu[0])
            speed_num += 1
        bucket = str(math.floor((mu[1]-mu[0])/clock_time)*clock_time)
        if bucket in n_time:
            n_time[bucket] += 1
        else:
            n_time[bucket] = 1

print n_time

n_mode = 0;
time_mode = 0.0;

xs = []
ys = []
xerrs = []
yerrs = []

for clocks in xrange(-40, 40):
    s = "{:6.2f} ns " .format(clock_time*clocks)
    if str(clock_time*clocks) in n_time:
        xs.append(clocks*clock_time)
        ys.append(n_time[str(clock_time*clocks)])
        xerrs.append(1.25/math.sqrt(12.0))
        yerrs.append(math.sqrt(n_time[str(clock_time*clocks)]))
        '''
        of.write(str(clock_time*clocks))
        of.write(" ")
        of.write(str(n_time[str(clock_time*clocks)]))
        of.write(" ")
        of.write(str(math.sqrt(n_time[str(clock_time*clocks)])))
        of.write("\n")
        '''
        if n_time[str(clock_time*clocks)] > n_mode:
            n_mode = n_time[str(clock_time*clocks)]
            time_mode = clock_time*clocks
        s += "x"*min(n_time[str(clock_time*clocks)]/1, 169)
    print s

print " mean time =", mean_time/time_num
if time_mode != 0.0:
    print "mode speed =", height/time_mode, "ft/ns"
print "mean speed =", mean_speed/speed_num, "ft/ns"
print "dist/mean time =", height*time_num/mean_time
print "         c =", .9789141486, "ft/ns"

print "from", start_time, "to", end_time
print "time = ", end_time-start_time+secs_from_days, "s"
print "rate =", i/(end_time-start_time+secs_from_days), "Hz"

#plt.figure()
#plt.hist(h, 50)
plt.axes(axisbg = "black")
plt.bar(xs, ys, color = [0.0, 0.0, 0.7], width = 1.25, xerr = xerrs, yerr = yerrs, ecolor = [0.7, 0.7, 0.7], capsize = 4)
plt.xlabel("time difference (ns)")
plt.ylabel("# muons")
plt.show()
