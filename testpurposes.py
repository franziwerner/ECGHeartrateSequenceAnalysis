import numpy as np
import heartpy as hp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import itertools
import os

### needed function
def sequence_plotter(working_data, measures, title='Heart Rate Signal Peak Detection',
                    figsize=(6, 6), path='', subject='', start=0, end=None, step=1):

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

    # Array to store the selected sequences
    choosen_sequence = []
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
        p = hp.plotter(wd_segment, m_segment, show=False)
        # added from my side
        plt.subplots_adjust(bottom=0.25)
        ax_button = plt.axes([0.25, 0.1, 0.08, 0.05])
        save_button = Button(ax_button, 'Save', color='white', hovercolor='grey')
        ax_button2 = plt.axes([0.15, 0.1, 0.09, 0.05])
        discard_button = Button(ax_button2, 'Discard', color='white', hovercolor='grey')

        # saving/discarding figure
        def savefct(val):  # val is the value of the button
            p.savefig('%s%s%i.png' % (path, subject, filenum))
            choosen_sequence.append(1)
            plt.close('all')
        def discardfct(val):
            choosen_sequence.append(0)
            plt.close('all')
        save_button.on_clicked(savefct)
        discard_button.on_clicked(discardfct)

        plt.show()
        filenum += 1

    return choosen_sequence


# subject
subject = 'sub03_'

# sample_rate in Hz
sample_rate = 200

# get raw data (header and data)
hrdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi03.csv', column_name='uV')
timerdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi03.csv', column_name='dt')

# bandpass filter given by heartpy
bp_filtered = hp.filter_signal(hrdata_3rd, cutoff=[7,21], sample_rate=sample_rate, order=3, filtertype='bandpass')

# create working_data dict, in which we can integrate merged arrays later on (in order to enable poincare plot)
wd_whole_epi, meas_whole_epi = hp.process(bp_filtered, sample_rate=sample_rate)
print(f'RR_masklist whole epi at beginning: {wd_whole_epi["RR_masklist"]}')
print(f'RR_list whole epi at beginning: {wd_whole_epi["RR_list"]}')
print(f'RR_list_cor whole epi at beginning: {wd_whole_epi["RR_list_cor"]}')

# get user input and convert text to number
seq_width = int(input("Sequence with: "))

# process segmentwise
work_data, meas = hp.process_segmentwise(bp_filtered, sample_rate=sample_rate, segment_width=seq_width)
#print(f'RR_masklist: {work_data["RR_masklist"][0]}')
#print(f'RR_list: {work_data["RR_list"][0]}')
#print(f'Length RR_list: {len(work_data["RR_list"])}')
#print(f'Length RR_masklist: {len(work_data["RR_masklist"])}')

# Array to store selected hr data (we do not need for the moment!)
stitched_hr_data = []
# Array to store peaklists of single sequences
stitched_peaklists = []
# Array to store RR_marklists
stitched_RR_masklists = []
# Array to store RR_lists
stitched_RR_lists = []

choosen_seq = sequence_plotter(work_data, meas, path='/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/segmentwise_plotting/', subject=subject)
print(f'choosen_seq: {choosen_seq}')
print(f'work_data[peaklist][0]: {work_data["peaklist"][0]}')
print(f'work_data[peaklist][1]: {work_data["peaklist"][1]}')
print(f'work_data[peaklist][2]: {work_data["peaklist"][2]}')

# sequences selected by the user are stitched together
# peaklists need to be recalculated (because indexing starts anew with each sequence)
nr_samplepoints_per_seq = seq_width * sample_rate
print(f'nr_samplepoints_per_seq: {nr_samplepoints_per_seq}')

for j in range(0, len(choosen_seq)):
    if choosen_seq[j] == 1:
        stitched_peaklists.append(work_data['peaklist'][j] + (j * nr_samplepoints_per_seq))
        stitched_RR_masklists.append(work_data['RR_masklist'][j])
        stitched_RR_lists.append(work_data['RR_list'][j])
    else:
        print(f'sequence {j + 1} is not appended.')

# merges stitched lists to one big list
merged_peaklists = list(itertools.chain(*stitched_peaklists))
merged_RR_masklist = list(itertools.chain(*stitched_RR_masklists))
merged_RR_list = list(itertools.chain(*stitched_RR_lists))

### put merged lists in working_data dict of whole episode
wd_whole_epi['peaklist'] = merged_peaklists
wd_whole_epi['RR_masklist'] = merged_RR_masklist
wd_whole_epi['RR_list'] = merged_RR_list
print(f'RR_masklist whole epi final: {wd_whole_epi["RR_masklist"]}')
print(f'RR_list whole epi final: {wd_whole_epi["RR_list"]}')

## Poincare Plot
hp.plot_poincare(wd_whole_epi, meas_whole_epi, figsize = (20,5), title='Poincare Plot')
plt.show()












# save merged_peaklists to csv file (to enable loading of file later)
np.savetxt("/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/segmentwise_plotting/merged_peaklist.csv", merged_peaklists, fmt="%10.5f", header='Peaklist')

print(f'len stitched_peaklists: {len(stitched_peaklists)}')
print(f'stitched_peaklists[0]: {stitched_peaklists[0]}')
print(f'stitched_peaklists[1]: {stitched_peaklists[1]}')
print(f'stitched_peaklists[2]: {stitched_peaklists[2]}')

# hr einzeln abspeichern und dann eine lange hr kette ist problematisch, weil spätes aneinanderreihen ergibt sprünge.. warum eigentlich? ist doch vorher bp-gefiltert?
# weil: jede einzelne Sequenz erhält spezifische Skalierung (bl_val, der den HR-Daten hinzuaddiert wird; passiert in hp.process function)
for i in range(0, len(choosen_seq)):
    if choosen_seq[i] == 1:
        stitched_hr_data.append(work_data['hr'][i])
    else:
        continue

#print(f'stitched_hr_data: {stitched_hr_data}')
print(len(stitched_hr_data))
print(type(work_data['hr'][0]))
print(type(stitched_hr_data))

# merges stitched_hr_data to one big list
merged_hr_data = list(itertools.chain(*stitched_hr_data))
# save merged_hr_data to csv file (to enable loading of file later)
np.savetxt("/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/segmentwise_plotting/merged_hr.csv", merged_hr_data, fmt="%10.5f", header='Heartrate')

print(f'length merged_hr_data: {len(merged_hr_data)}')
print(f'merged_hr_data[0]: {merged_hr_data[0]}')
print(f'merged_hr_data[1]: {merged_hr_data[1]}')
print(len(stitched_hr_data[0]))

## Poincare Plot
#hp.plot_poincare(wd_merged, meas_merged, figsize = (20,5), title='Poincare Plot')
#plt.show()



## hand over merged_hr_data tp process function, many jumps inside graph -> high-pass filter??
## this is nonsense, because peaks are calculated anew and that is what we do not want
#wd_merged, meas_merged = hp.process(merged_hr_data, sample_rate=sample_rate)
#hp.plotter(wd_merged, meas_merged, figsize=(20,5), title = 'Processed HR Sequences')
#print(f'wd_merged: {wd_merged}')
#print(f'meas_merged: {meas_merged}')
#print(type(merged_hr_data))
#plt.show()

#new_seq = np.stack(stitched_hr_data) ## new_seq is type array
#print(f'new_seq: {new_seq}')
#print(type(new_seq))

#seq = np.concatenate(stitched_hr_data[0]:(len(stitched_hr_data)-1)


# is hrdata affeced by segmentwise processing? -> yes, because of specific bl_val, which is hrdata dependent and is added to hrdata (scalar)