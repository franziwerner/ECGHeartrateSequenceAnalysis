import heartpy as hp
from heartpy.visualizeutils import segment_plotter
from heartpy.datautils import rolling_mean
from heartpy.peakdetection import detect_peaks
from heartpy.analysis import calc_fd_measures
from heartpy.preprocessing import enhance_ecg_peaks
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from matplotlib.widgets import Button, RadioButtons, CheckButtons

### needed functions
def sequence_plotter(working_data, measures, title='Heart Rate Signal Peak Detection',
                    figsize=(6, 6), path='', start=0, end=None, step=1):

    # sanity check
    assert 0 < step < len(working_data['hr']), 'step must be larger than zero and smaller than total number of segments'

    # set endpoint if not explicitly defined
    if end == None:
        end = len(working_data['hr'])
    else:
        # make sure it is defined within boundary conditions
        assert end <= len(working_data['hr']), 'defined "end" endpoint is larger than number of segments'

    # add trailing path slash if user omitted it
    if not (path.endswith('/') or path.endswith('\\')) and len(path) > 0:
        path += '/'
        # create path if it doesn't exist
        if not os.path.isdir(path):
            os.makedirs(path)

    # make plots
    filenum = 0
    for i in range(start, end, step):
        wd_segment = {}
        m_segment = {}
        # assign values to sub-object for plotting purposes
        wd_segment['peaklist'] = working_data['peaklist'][i]
        wd_segment['ybeat'] = working_data['ybeat'][i]
        wd_segment['removed_beats'] = working_data['removed_beats'][i]
        wd_segment['removed_beats_y'] = working_data['removed_beats_y'][i]
        wd_segment['hr'] = working_data['hr'][i]
        wd_segment['rolling_mean'] = working_data['rolling_mean'][i]
        wd_segment['sample_rate'] = working_data['sample_rate'][i]
        m_segment['bpm'] = measures['bpm'][i]
        try:
            wd_segment['rejected_segments'] = working_data['rejected_segments'][i]
        except:
            pass

        ## plot it using built-in plotter
        # removed from my side (just the following line)
        # plt.figure(figsize = figsize)
        p = hp.plotter(wd_segment, m_segment, show=False)
        # added from my side
        plt.subplots_adjust(bottom=0.25)
        ax_button = plt.axes([0.25, 0.1, 0.08, 0.05])
        save_button = Button(ax_button, 'Save', color='white', hovercolor='grey')

        # saving figure
        def savefct(val):  # val is the value of the button
            p.savefig('%s%i.png' % (path, filenum))
        save_button.on_clicked(savefct)
        plt.show()
        plt.close('all')
        filenum += 1

# sample_rate in Hz
sample_rate = 200
#windowsize = 0.2
#ma_perc = 10

# get raw data (header and data)
hrdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi03.csv', column_name='uV')
timerdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi03.csv', column_name='dt')

print(f'timerdata: {timerdata_3rd}')
print(f'hr data: {hrdata_3rd}')

## bandpass filter given by heartpy
bp_filtered = hp.filter_signal(hrdata_3rd, cutoff=[7,21], sample_rate=sample_rate, order=3, filtertype='bandpass')
wd_bp_filtered, m_bp_filtered = hp.process(bp_filtered, sample_rate = sample_rate)
#print(f'wd_bp_filtered: {wd_bp_filtered}')
#print(f'm_bp_filtered: {m_bp_filtered}')
hp.plotter(wd_bp_filtered, m_bp_filtered, figsize=(20,5), title = 'bandpass-filtered with heartpy')
# Button
# properties of the button
plt.subplots_adjust(bottom=0.25)
ax_button = plt.axes([0.25, 0.1, 0.08, 0.05])
save_button = Button(ax_button, 'Save', color='white', hovercolor='grey')
# saving figure
def savefct(val): # val is the value of the button
    plt.savefig('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/segmentwise_plotting/test.png')
save_button.on_clicked(savefct)
plt.show()

# how to get values
# '%.3f' %m['bpm']

# get user input and convert text to number
seq_width = int(input("Sequence with: "))

print(seq_width)

work_data, meas = hp.process_segmentwise(bp_filtered, sample_rate=sample_rate, segment_width=seq_width)
print(f'work_data: {work_data}')
#print(f'meas: {meas}')
print(len(work_data['hr']))
sequence_plotter(work_data, meas, path='/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/segmentwise_plotting/')
#plt.show()

## get values from dict
#x_freq_bp = wd_bp_filtered['frq']
#y_psd_bp = wd_bp_filtered['psd']
#y_psd_s2_bp = [i*10**-6 for i in y_psd_bp]

## define figure
#plt.figure(figsize= (10, 5))
#plt.plot(x_freq_bp, y_psd_s2_bp)
#plt.show()

#print(wd_bp_filtered)
#print(m_bp_filtered)

## Poincare Plot
#hp.plot_poincare(wd_bp_filtered, m_bp_filtered, figsize = (20,5), title='Poincare Plot')
#plt.show()

#hp.plot_breathing(wd_3rd, m_3rd)

## scale hrdata (can be left out)
#hrdata_scaled = filtered_raw * 5
#hrdata_squared = np.square(hrdata_scaled)

## square scaled under consideration of the sign
#for ind in range(len(hrdata_scaled)):
#    if hrdata_scaled[ind] >= 0:
#        hrdata_squared[ind] = np.square(hrdata_scaled[ind])
#    elif hrdata_scaled[ind] < 0:
#        hrdata_squared[ind] = -(np.square(hrdata_scaled[ind])) #hrdata_scaled[ind]

## scale bandpass-filtered data
#bpfiltered_scaled = bp_filtered * 1
#bpfil_scaled_squared = np.square(bpfiltered_scaled)

## square under consideration of the sign
#for ind in range(len(bpfiltered_scaled)):
#    if bpfiltered_scaled[ind] >= 0:
#        bpfil_scaled_squared[ind] = np.square(bpfiltered_scaled[ind])
#    elif bpfiltered_scaled[ind] < 0:
#        bpfil_scaled_squared[ind] = -(np.square(bpfiltered_scaled[ind]))

#bpfil_scaled_squared2 = np.square(bpfil_scaled_squared)

## square under consideration of the sign
#for ind in range(len(bpfiltered_scaled)):
#    if bpfiltered_scaled[ind] >= 0:
#        bpfil_scaled_squared2[ind] = np.square(bpfil_scaled_squared[ind])
#    elif bpfiltered_scaled[ind] < 0:
#        bpfil_scaled_squared2[ind] = -(np.square(bpfil_scaled_squared[ind]))

## smooth signal
#smoothed = hp.smooth_signal(bpfil_scaled_squared2, sample_rate=sample_rate)
#wd_smoothed, m_smoothed = hp.process(smoothed, sample_rate = sample_rate, windowsize=0.75)
#hp.plotter(wd_smoothed, m_smoothed, figsize=(20,5), title = 'bpfiltered, double squared and smoothed with heartpy')
#plt.show()

#print(hrdata_3rd)
#print(hrdata_scaled)
#print(hrdata_squared)

## plotting high-pass filtered, scaled and squared signal
#wd_squared, m_squared = hp.process(hrdata_squared, sample_rate = sample_rate)
#hp.plotter(wd_squared, m_squared, figsize=(20,5), title = 'highpass-filtered and squared signal')
#plt.show()

## plotting bandpassfiltered and squared signal
#wd_bp_scaled_squared, m_bp_scaled_squared = hp.process(bpfil_scaled_squared2, sample_rate = sample_rate, windowsize=0.75)
#hp.plotter(wd_bp_scaled_squared, m_bp_scaled_squared, figsize=(20,5), title = 'bandpassfiltered and squared signal')
#plt.show()

## high-pass filtering with own implemented filter
#filtered_ecg = butter_highpass_filter(hrdata_3rd, 7, sample_rate)
#wd_3rd_hp, m_3rd_hp = hp.process(filtered_ecg, sample_rate = sample_rate)

## enhance peaks
#filtered_data = enhance_ecg_peaks(filtered_ecg, sample_rate, iterations = 1)
#wd_3rdfd, m_3rdfd = hp.process(filtered_data, sample_rate = sample_rate)
## plotting with enhanced ecg
#hp.plotter(wd_3rdfd, m_3rdfd, figsize=(20,5), title = 'Heart Beat Detection ECG Signal high-pass filtered and enhanced peaks')
#plt.show()

# using filter given by heartpy
#filtered = hp.filter_signal(hrdata_3rd, cutoff=7, sample_rate=sample_rate, order=3, filtertype='highpass')
#wd_filtered, m_filtered = hp.process(filtered, sample_rate = sample_rate, windowsize=0.75)
#hp.plotter(wd_filtered, m_filtered, figsize=(20,5), title = 'high-pass filtered with heartpy')
#plt.show()

#print('Peaklist including rejected peaks:' + str(wd_3rdf['peaklist'][0:len(wd_3rdf['peaklist'])]))
#print('Peaklist length (including red marked rejected peaks):' + str(len(wd_3rdf['peaklist'])))
#print('Removed beats:' + str(wd_3rdf['removed_beats']))
#print('RR-list with red peaks:' + str(wd_3rdf['RR_list'][0:len(wd_3rdf['RR_list'])]))
#print('Length RR-list:' + str(len(wd_3rdf['RR_list'])))
## corrected RR-list (leave out red marked peaks)
#print('corrected RR-list:' + str(wd_3rdf['RR_list_cor'][0:len(wd_3rdf['RR_list_cor'])]))
#print('length of corrected RR-list:' + str(len(wd_3rdf['RR_list_cor'])))
#print('best ma_perc:' + str(wd_3rdf['best']))

# Test: reine erste Peakdetection ohne Peakrejection
#rol_meanT = rolling_mean(filtered_ecg, windowsize = 0.75, sample_rate = 200.0)
#wd = detect_peaks(filtered_ecg, rol_meanT, ma_perc = 20, sample_rate = 200.0)
#print(wd['peaklist'][0:len(wd['peaklist'])])
#print(len(wd['peaklist']))

#print('%.3f' %m_034f_3rd['bpm'])
#print('%.3f' %m_034f_3rd['rmssd'])
#print('%.3f' %m_034f_3rd['breathingrate'])

#print(len(wd_034f_3rd['RR_list'])) # is of length len(peaks) - 1
#print(len(wd_034f_3rd['peaklist']))

#plt.figure(figsize= (30, 20))
#plt.subplot(311)
#plt.plot(timerdata_3rd, hrdata_3rd)
#plt.title("ECG raw signal with breathing")
#plt.subplot(312)
##plt.plot(range(len(filtered_ecg)), filtered_ecg)
#plt.plot(timerdata_3rd, filtered_ecg)
#plt.ylim(-6, 4)
#plt.title("High-Pass-Filtered ECG Signal")
#plt.show()
#plt.subplot(312)
#plt.plot(timerdata_3rd, filtered_scaled)
#plt.ylim(-6, 4)
#plt.title("scaled and filtered")
#plt.show()


## plot with different title
#hp.plotter(wd_3rd_hp, m_3rd_hp, figsize=(20,5), title='Heart Beat Detection on High-Pass-Filtered Signal')
#plt.ylim(-6,4)
#plt.show()




# Ausrangiertes (was ich getestet habe)

## smooth signal
#smoothed = hp.smooth_signal(hrdata_3rd, sample_rate=sample_rate)
#wd_smoothed, m_smoothed = hp.process(smoothed, sample_rate = sample_rate)
#hp.plotter(wd_smoothed, m_smoothed, figsize=(20,5), title = 'smoothed with heartpy')
#plt.show()

#sm_filtered = hp.filter_signal(smoothed, cutoff=5, sample_rate=sample_rate, order=3, filtertype='highpass')
#wd_sm_filtered, m_sm_filtered = hp.process(sm_filtered, sample_rate = sample_rate)
#hp.plotter(wd_sm_filtered, m_sm_filtered, figsize=(20,5), title = 'smoothed and filtered with heartpy')
#plt.show()

## tried to manually adjust ma_perc
#roll_mean = rolling_mean(hrdata_squared, windowsize=0.75, sample_rate=sample_rate)
#work_dir = detect_peaks(hrdata_squared, roll_mean, ma_perc = 20, sample_rate=sample_rate)


#wd_3rd, m_3rd = hp.process(hrdata_3rd, sample_rate = sample_rate)

#wd_3rd, m_3rd = calc_fd_measures(method='welch', measures=m_3rd, working_data=wd_3rd)
#print(wd_3rd)
#print(m_3rd)

# get values from dict
#x_freq = wd_3rd['frq']
#y_psd = wd_3rd['psd']
#y_psd_s2 = [i*10**-6 for i in y_psd]

#print(x_freq)
#print(y_psd_s2)

# define figure
#fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'}, figsize=figsize)
#plt.figure(figsize= (10, 5))
#plt.plot(x_freq, y_psd_s2)


#print(wd_3rd['peaklist'][0:len(wd_3rd['peaklist'])])
#print(len(wd_3rd['peaklist']))

# define filter
def butter_highpass(cutoff, fs, order = 3):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype = "high", analog = False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order = 3):
    b, a = butter_highpass(cutoff, fs, order = order)
    y = signal.filtfilt(b, a, data)
    return y

## plotting ECG raw data with detected peaks and without filtering (includes breathing)
#hp.plotter(wd_3rd, m_3rd, figsize=(20,5), title = 'Heart Beat Detection ECG Signal with superimposed breathing')
#plt.show()

## filtering raw signal
#filtered_raw = butter_highpass_filter(hrdata_3rd, 7, sample_rate)