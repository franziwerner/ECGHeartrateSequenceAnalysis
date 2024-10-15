import heartpy as hp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from scipy.interpolate import CubicSpline
from tftb.processing.cohen import PseudoWignerVilleDistribution
import csv


# sample_rate in Hz
sample_rate = 200

# get raw data (header and data)
hrdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/singleSequences/fifthEpi010.csv', column_name='uV')
timerdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/singleSequences/fifthEpi010.csv', column_name='dt')

# plot without processing
plt.plot(hrdata_3rd)
plt.show()

# without filtering
wd_nbp_filtered, m_nbp_filtered = hp.process(hrdata_3rd,sample_rate = sample_rate)
plot_nbp = hp.plotter(wd_nbp_filtered, m_nbp_filtered, figsize=(20,5), title = 'without filtering')
plt.show()

# bandpass filter given by heartpy
bp_filtered = hp.filter_signal(hrdata_3rd, cutoff=[7,21], sample_rate=sample_rate, order=3, filtertype='bandpass')
plt.plot(bp_filtered)
plt.show()

wd_bp_filtered, m_bp_filtered = hp.process(bp_filtered, sample_rate = sample_rate)
plot_bp = hp.plotter(wd_bp_filtered, m_bp_filtered, figsize=(20,5), title = 'bandpass-filtered')
plt.show()






# with open('/Users/franziskawerner/Documents/ISN/DFGProjekt/EKG/csvEKG/vp046/MDC_ECG_LEAD_II.csv') as csvdatei:
#     line = 0
#     csv_reader_object = csv.reader(csvdatei, delimiter=',')
#     print(csv_reader_object)
#     for row in csv_reader_object:
#         print(row)
#         line += 1
#     print(f'Processed {line} lines.')


# example for SPWVD
# wvd = WignerVilleDistribution(mod_signal)
# wvd.run()
# wvd.plot(kind='contour')


#sample_rate = 250

#data = hp.get_data("/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/data.csv")

#wd, m = hp.process(data, sample_rate)
#hp.plotter(wd, m)
#plt.show()


#hrdata = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/data2.csv', column_name='hr')
#timerdata = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/data2.csv', column_name='timer')

#print(hrdata)
#print(timerdata)

#working_data2, measures2 = hp.process(hrdata, hp.get_samplerate_mstimer(timerdata))

#print(working_data2)
#print(measures2)

## plot with different title
#hp.plotter(working_data2, measures2, title='Heart Beat Detection on Noisy Signal')
#plt.show()

## own data proband 034

#mstimer_data = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/data2.csv', column_name='timer')
#fs = hp.get_samplerate_mstimer(mstimer_data)
#print(fs)

## kommt 200000 raus, sollte doch aber 200Abtastwerte/s rauskommen (alle 5ms einen Wert -> macht pro Sekunde 200 Abtastwerte)
#mstimer_EKG = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/MDC_ECG_LEAD_II.csv', column_name='dt')
#fs1 = hp.get_samplerate_mstimer(mstimer_EKG)
#print(fs1)

# # sample_rate in Hz
# sample_rate = 200
#
# #hrdata034 = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/MDC_ECG_LEAD_II.csv', column_name='uV')
# #timerdata034 = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/MDC_ECG_LEAD_II.csv', column_name='dt')
#
# hrdata034 = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/file_00.csv', column_name='uV')
# timerdata034 = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/file_00.csv', column_name='dt')
#
# print(hrdata034)
# print(timerdata034)
#
# ## print(timerdata034)
# working_data034, measures034 = hp.process(hrdata034, sample_rate = sample_rate) #hp.get_samplerate_mstimer(timerdata034)) #sample_rate = sample_rate) #hp.get_samplerate_mstimer(timerdata034))
# print(working_data034)
# print(measures034)
#
# print(working_data034['peaklist'][0:len(working_data034['peaklist'])])
# print(len(working_data034['peaklist']))
#
# def butter_highpass(cutoff, fs, order=5):
#     nyq = 0.5 * fs
#     normal_cutoff = cutoff / nyq
#     b, a = signal.butter(order, normal_cutoff, btype = "high", analog = False)
#     return b, a
#
# def butter_highpass_filter(data, cutoff, fs, order=5):
#     b, a = butter_highpass(cutoff, fs, order=order)
#     y = signal.filtfilt(b, a, data)
#     return y
#
# fps = 200
#
# ## plotting
# hp.plotter(working_data034, measures034, figsize=(20,5), title = 'Heart Beat Detection ECG Signal with superimposed breathing')
# plt.show()
#
# # high-pass filtering
# filtered_ecg = butter_highpass_filter(hrdata034, 7, fps)
#
# working_data034f, measures034f = hp.process(filtered_ecg, sample_rate = sample_rate) #hp.get_samplerate_mstimer(timerdata034)) #sample_rate = sample_rate) #hp.get_samplerate_mstimer(timerdata034))
# print(working_data034f)
# print(measures034f)
#
# print('%.3f' %measures034f['bpm'])
# print('%.3f' %measures034f['rmssd'])
# print('%.3f' %measures034f['breathingrate'])
#
# print(working_data034f['peaklist'][0:len(working_data034f['peaklist'])])
# print(working_data034f['peaklist'])
# print(working_data034f['RR_list'][0:len(working_data034f['RR_list'])])
#
# ### plot instantaneous HR
# actualHR = 60/(working_data034f['RR_list']/1000)
# instantaneousHR = actualHR/60
# print('Instantaneous HR:' + str(actualHR))
# print('kumRRList:' + str(working_data034f['RR_list']/1000))
# print('kumRRList_0:' + str(working_data034f['RR_list'][0]/1000))
#
# ## generate cumulative RR-list in order to be able to plot the instantanoeus heartrate against time in seconds
# xTime = [0] * 42
# sum = 0
# for i in range(len(working_data034f['RR_list'])):
#     sum = sum + (working_data034f['RR_list'][i]/1000)
#     xTime[i] = sum
#
# print('xTime:' + str(xTime))
#
# spl = CubicSpline(xTime, instantaneousHR)
#
# plt.plot(figsize=(5, 7))
# #xnew = np.linspace(0, 10, num=1001)
# plt.plot(xTime, spl(xTime))
# plt.plot(xTime, instantaneousHR, 'o', label='data')

#### when I need more plots at once 
#fig, ax = plt.subplots(2, 1, figsize=(5, 7))
#ax[0].plot(xTime, spl(xTime))
#ax[0].plot(xTime, instantaneousHR, 'o', label='data')
#plt.show()



plt.plot(instantaneousHR)
plt.show()

peaksInTime = working_data034f['peaklist'] * 0.005
print(peaksInTime)

fig, ax1 = plt.subplots(figsize=(10, 6))
x = timerdata034
ax1.plot(x, filtered_ecg, color = "blue")
ax1.set_ylabel(r"uV", fontsize = 16, color = "blue")
for label in ax1.get_yticklabels():
    label.set_color("blue")

plt.yticks([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])

print(len(x))
print(timerdata034[working_data034f['peaklist']])


x1 = timerdata034[working_data034f['peaklist']]
x1mod = np.delete(x1, [0])
print(len(x1mod))

ax2 = ax1.twinx()
ax2.plot(x1mod, actualHR, color = "darkgreen")
ax2.plot(x1mod, actualHR, "o", color = "darkgreen")
ax2.set_ylabel(r"heart rate", fontsize = 16, color = "darkgreen")
for label in ax2.get_yticklabels():
    label.set_color("darkgreen")

plt.yticks([90, 95, 100, 105, 110, 115])
plt.show()

print('RR Liste:' + str(working_data034f['RR_list']))
print(len(working_data034f['RR_list'])) # is of length len(peaks) - 1 # 42
print(len(working_data034f['peaklist'])) # 43
print(working_data034f['hr'])

##plt.figure(figsize= (20, 10))
##plt.subplot(211)
##plt.plot(timerdata034, hrdata034)
##plt.title("ECG raw signal with breathing")
##plt.subplot(212)
###plt.plot(range(len(filtered_ecg)), filtered_ecg)
##plt.plot(timerdata034, filtered_ecg)
##plt.ylim(-6, 4)
##plt.title("High-Pass-Filtered ECG Signal")
##plt.show()

## plot with different title
#hp.plotter(working_data034f, measures034f, figsize=(20,5), title='Heart Beat Detection on High-Pass-Filtered Signal')
#plt.ylim(-6,4)
#plt.show()

## plot RR_list (greater distances between RR peaks -> smaller HR)
#plt.plot(working_data034f['RR_list'])
#plt.plot(working_data034f['RR_list'], "ob")
#plt.show()

#print(working_data034f['hr'])
#print(len(working_data034f['hr']))

## calculate HRV RMSSD



## plotting segmentwise
#working_data034sw, measures034sw = hp.process_segmentwise(hrdata034, sample_rate=200.0, segment_width = 2, segment_overlap = 0.0, mode='full')

#hp.segment_plotter(working_data034sw, measures034sw, figsize=(20, 5), path='/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data')
#plt.show()

#hrdata = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/data2.csv', column_name='hr')
#timerdata = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/data2.csv', column_name='timer')

#working_data, measures = hp.process(hrdata, hp.get_samplerate_mstimer(timerdata))

#print(working_data)
#print(measures)

#plot with different title
#plotEX = hp.plotter(working_data, measures, show=False, title='Heart Beat Detection on Noisy Signal')
