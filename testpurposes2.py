import numpy as np
import heartpy as hp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import itertools
import os
from matplotlib.artist import Artist

def plotter(working_data, measures, show=True, figsize=None, title='Heart Rate Signal Peak Detection', moving_average=True):
    print("Hello")

    # get color palette
    colorpalette = hp.config.get_colorpalette_plotter()

    # create plot x-var
    fs = working_data['sample_rate']
    plotx = np.arange(0, len(working_data['hr']) / fs, 1 / fs)
    # check if there's a rounding error causing differing lengths of plotx and signal
    diff = len(plotx) - len(working_data['hr'])
    if diff < 0:
        # add to linspace
        plotx = np.append(plotx, plotx[-1] + (plotx[-2] - plotx[-1]))
    elif diff > 0:
        # trim linspace
        plotx = plotx[0:-diff]

    peaklist = working_data['peaklist']
    ybeat = working_data['ybeat']
    rejectedpeaks = working_data['removed_beats']
    rejectedpeaks_y = working_data['removed_beats_y']

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(title)
    print(f'plotx: {plotx}')
    #ax.plot(plotx, working_data['hr'], color=colorpalette[0], label='heart rate signal', zorder=-10)
    a = plt.plot(range(len(working_data['hr'])), working_data['hr'], color=colorpalette[0], label='heart rate signal', zorder=-10)[0]
    print(f'a: {a}')
    ax.set_xlabel('sampling points')

    if moving_average:
        #ax.plot(plotx, working_data['rolling_mean'], color='gray', alpha=0.5)
        plt.plot(range(len(working_data['rolling_mean'])), working_data['rolling_mean'], color='gray', alpha=0.5)

    for i in range(0, len(peaklist) - 1):
        #ax.scatter(peaklist[i] / fs, ybeat[i], color=colorpalette[1], picker=True)  # pickradius = 5
        b = plt.scatter(peaklist[i], ybeat[i], color=colorpalette[1], picker=True)

    for j in range(0, len(rejectedpeaks) - 1):
        plt.scatter(rejectedpeaks[j], rejectedpeaks_y[j], color=colorpalette[2], picker=True)

    # check if rejected segment detection is on and has rejected segments
    try:
        if len(working_data['rejected_segments']) >= 1:
            for segment in working_data['rejected_segments']:
                ax.axvspan(segment[0], segment[1], facecolor='red', alpha=0.5)
    except:
        pass

    ax.legend(loc=4, framealpha=0.6)

    if show:
        fig.show()
    else:
        return fig, a, b


### needed function
def sequence_plotter(working_data, measures, title='Heart Rate Signal Peak Detection', figsize=(6, 6), path='', subject='', start=0, end=None, step=1):

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
        print(f'peaklist: {wd_segment["peaklist"]}')
        wd_segment['ybeat'] = working_data['ybeat'][i]
        wd_segment['removed_beats'] = working_data['removed_beats'][i]
        print(f'removed beats: {wd_segment["removed_beats"]}')
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
        fig1, a, b = plotter(wd_segment, m_segment, show=False)

        def add_or_remove_point(event):
            xydata_a = np.stack(a.get_data(), axis=1)
            print(f'xydata_a: {xydata_a}')
            xdata_a = a.get_xdata()
            print(f'xdata_a: {xdata_a}')
            xydata_b = b.get_offsets()
            print(f'xydata_b: {xydata_b}')
            xdata_b = b.get_offsets()[:, 0]
            print(f'xdata_b: {xdata_b}')

            # click x-value
            xdata_click = event.xdata
            ##index of nearest x-value in a
            # we only accept points on curve
            xdata_nearest_index_a = (np.abs(xdata_a - xdata_click)).argmin()
            # new scatter point x-value
            new_xdata_point_b = xdata_a[xdata_nearest_index_a]
            # new scatter point [x-value, y-value]
            new_xydata_point_b = xydata_a[new_xdata_point_b, :]

            if event.button == 1:
                if new_xdata_point_b not in xdata_b:
                    print(f'new_xdata_point_b: {new_xdata_point_b}')
                    # insert new scatter point into b
                    new_xydata_b = np.insert(xydata_b, 0, new_xydata_point_b, axis=0)
                    # sort b based on x-axis values
                    new_xydata_b = new_xydata_b[np.argsort(new_xydata_b[:, 0])]
                    # update b
                    b.set_offsets(new_xydata_b)
                    plt.draw()
            elif event.button == 3:
                if new_xdata_point_b in xdata_b:
                    # remove xdata point b
                    new_xydata_b = np.delete(xydata_b, np.where(xdata_b == new_xdata_point_b), axis=0)
                    print(new_xdata_point_b)
                    # update b
                    b.set_offsets(new_xydata_b)
                    plt.draw()

        ## false green peaks can be set to red and false marked red peaks can be marked green with click
        def onpick(event):
            print("Pick handler is called")
            if event.mouseevent.button == 2 and isinstance(event.artist, Artist):
                artist = event.artist
                artist_edgecolor = np.round(artist.get_edgecolor(), 8)
                if artist_edgecolor[0][1] == 0.50196078:
                    props = {"color": "red"}
                    Artist.update(artist, props)
                    plt.draw()
                elif artist_edgecolor[0][1] != 0.50196078:
                    props = {"color": "green"}
                    Artist.update(artist, props)
                    plt.draw()
            else:
                return

        fig1.canvas.mpl_connect('button_press_event', add_or_remove_point)
        fig1.canvas.mpl_connect('pick_event', onpick)
        #plt.show()
        # added from my side
        plt.subplots_adjust(bottom=0.25)
        ax_button = plt.axes([0.25, 0.1, 0.08, 0.05])
        save_button = Button(ax_button, 'Save', color='white', hovercolor='grey')
        ax_button2 = plt.axes([0.15, 0.1, 0.09, 0.05])
        discard_button = Button(ax_button2, 'Discard', color='white', hovercolor='grey')

        # saving/discarding figure
        def savefct(val):  # val is the value of the button
            fig1.savefig('%s%s%i.png' % (path, subject, filenum))
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
seq_width = int(input("Sequence width: "))

# process segmentwise
work_data, meas = hp.process_segmentwise(bp_filtered, sample_rate=sample_rate, segment_width=seq_width)
print(f'RR_masklist seg.wise: {work_data["RR_masklist"][0]}')
print(f'RR_list seg.wise: {work_data["RR_list"][0]}')
print(f'Length RR_list seg.wise: {len(work_data["RR_list"])}')
print(f'Length RR_masklist seg.wise: {len(work_data["RR_masklist"])}')

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