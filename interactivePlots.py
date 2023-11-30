import numpy as np
import heartpy as hp
import matplotlib.pyplot as plt
from matplotlib.artist import Artist


#### this script connects figure from plotter with event routine

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
    ax.set_xlabel('sampling points')

    if moving_average:
        #ax.plot(plotx, working_data['rolling_mean'], color='gray', alpha=0.5)
        plt.plot(range(len(working_data['rolling_mean'])), working_data['rolling_mean'], color='gray', alpha=0.5)

    for i in range(0, len(peaklist) - 1):
        #ax.scatter(peaklist[i] / fs, ybeat[i], color=colorpalette[1], picker=True)  # pickradius = 5
        b = plt.scatter(peaklist[i], ybeat[i], color=colorpalette[1], picker=True)

    for j in range(0, len(rejectedpeaks) - 1):
        ax.scatter(rejectedpeaks[j] / fs, rejectedpeaks_y[j], color=colorpalette[2], label='rejected peaks', picker=True)

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

# sample_rate in Hz
sample_rate = 200

# get choosen hr-data sequence
merged_hr = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/file_50.csv', column_name='uV')

merged_hr_hpfiltered = hp.filter_signal(merged_hr, cutoff=5, sample_rate=sample_rate, order=3, filtertype='highpass')
wd_merged, meas_merged = hp.process(merged_hr_hpfiltered, sample_rate=sample_rate)

### the following variables I just need when I do not use plotter-function
#heartrate = wd_merged['hr']
peaklist = wd_merged['peaklist']
print(f'peaklist: {peaklist}')
print(f'length peaklist: {len(peaklist)}')
print(f'type of peaklist: {type(peaklist)}')
masklist = wd_merged['RR_masklist']
print(f'masklist: {masklist}')
print(f'length of masklist: {len(masklist)}')
print(f'removed beats: {wd_merged["removed_beats"]}')
#rolmean = wd_merged['rolling_mean']

#fig, ax = plt.subplots(figsize=(16, 5))
#a = plt.plot(range(len(heartrate)), heartrate, color='lightblue')[0]  # [0] in order to use func get_data()later on
## to have single scatterpoints to click (when we use the onpick function)
## for i in range(0,len(b_input)-1):
##    b = plt.scatter(b_input[i], a_input[b_input[i]], color = 'green', s = 50, picker = True, pickradius = 10, zorder = 5)
#b = plt.scatter(peaklist, heartrate[peaklist], color='green', s=50, picker=True, pickradius=10, zorder=5)
#c = plt.plot(range(len(rolmean)), rolmean, color='gray', alpha=0.5)

def add_or_remove_point(event):
    # first part of this function runs on every click (even the 1)
    global a
    xydata_a = np.stack(a.get_data(), axis=1)
    print(f'xydata_a: {xydata_a}')
    xdata_a = a.get_xdata()
    print(f'xdata_a: {xdata_a}')
    global b
    xydata_b = b.get_offsets()
    print(f'xydata_b: {xydata_b}')
    xdata_b = b.get_offsets()[:, 0]
    xdata_b = np.delete(xdata_b, len(xdata_b)-1)
    print(f'xdata_b: {xdata_b}')
    print(f'length xdata_b: {len(xdata_b)}')

    # click x-value
    xdata_click = event.xdata
    ##index of nearest x-value in a
    # we only accept points on curve
    xdata_nearest_index_a = (np.abs(xdata_a - xdata_click)).argmin()
    print(f'xdata_nearest_index_a: {xdata_nearest_index_a}')
    # new scatter point x-value
    new_xdata_point_b = xdata_a[xdata_nearest_index_a]
    print(f'new_xdata_point_b: {new_xdata_point_b}')
    # new scatter point [x-value, y-value]
    new_xydata_point_b = xydata_a[new_xdata_point_b, :]
    print(f'new_xydata_point_b: {new_xydata_point_b}')

    if event.button == 2:
        if new_xdata_point_b not in xdata_b:
            # insert new scatter point into b
            new_xydata_b = np.insert(xydata_b, 0, new_xydata_point_b, axis=0)
            print(f'new_xydata_b unsorted: {new_xydata_b}')
            # sort b based on x-axis values (here: last peak from sequence is still listed)
            new_xydata_b = new_xydata_b[np.argsort(new_xydata_b[:, 0])]
            print(f'new_xydata_b sorted: {new_xydata_b}')
            # update b
            b.set_offsets(new_xydata_b)
            ### the newly selected peaks (must be integrated in peaklist)
            new_xdata_peaks = np.delete(new_xydata_b[:,0], len(new_xydata_b[:,0])-1)
            print(f'new_xdata_peaks: {new_xdata_peaks}')
            all_peaks = np.concatenate((peaklist, (new_xdata_peaks.astype(int))), axis = None)
            # sort entries of updatet peaklist
            all_peaks = all_peaks[np.argsort(all_peaks)]
            print(f'all_peaks: {all_peaks}')
            plt.draw()
    elif event.button == 3:
        if new_xdata_point_b in xdata_b:
            # remove xdata point b
            new_xydata_b = np.delete(xydata_b, np.where(xdata_b == new_xdata_point_b), axis=0)
            print(f'new_xdata_point_b: {new_xdata_point_b}')
            print(f'new_xydata_b: {new_xydata_b}')
            # update b (in order to plot updates)
            b.set_offsets(new_xydata_b)
            ### the newly rejected peaks (must be integrated in peaklist)
            new_xdata_peaks = np.delete(new_xydata_b[:,0], len(new_xydata_b[:,0])-1)
            print(f'new_xdata_peaks: {new_xdata_peaks}')
            all_peaks = np.concatenate((peaklist, (new_xdata_peaks.astype(int))), axis=None)
            # sort entries of updatet peaklist (that final peaklist (when saving respective sequence plot) needs to be used for calculating RR-distances)
            all_peaks = all_peaks[np.argsort(all_peaks)]
            print(f'all_peaks: {all_peaks}')
            plt.draw()

## false green peaks can be set to red and false marked red peaks can be marked green with click
def onpick(event):
    if event.mouseevent.button == 1 and isinstance(event.artist, Artist):
        artist = event.artist
        print(f'artist.get_offsets: {artist.get_offsets()}')
        sel_peak = (artist.get_offsets()[:, 0]).astype(int)
        print(f'type sel_peak: {type(sel_peak)}')
        print(f'sel_peak: {sel_peak}')
        print(f'peaklist: {peaklist}')
        print(f'RR_masklist: {masklist}')
        artist_edgecolor = np.round(artist.get_edgecolor(), 8)
        if artist_edgecolor[0][1] == 0.50196078: # peak is green
            props = {"color": "red"}
            # get index from red marked peak
            peak_ind = np.where(peaklist == sel_peak[0])[0][0]
            print(f'peak_ind: {peak_ind}')
            # set index and index-1 in masklist to 1 (1 means that this peak is not considered later on)
            print(f'masklist: {masklist}')
            if peak_ind == 0:
                masklist[peak_ind] = 1
            else:
                masklist[peak_ind] = 1
                masklist[peak_ind-1] = 1
            print(f'masklist: {masklist}')
            print(f'type of peak_ind: {type(peak_ind)}')
            Artist.update(artist, props)
            plt.draw()
        elif artist_edgecolor[0][1] != 0.50196078:
            props = {"color": "green"}
            # get index from green marked peak
            peak_ind = np.where(peaklist == sel_peak[0])[0][0]
            print(f'peak_ind: {peak_ind}')
            # set index and index-1 in masklist to 0 (0 means that this peak is not considered later on)
            print(f'masklist: {masklist}')
            if peak_ind == 0:
                masklist[peak_ind] = 0
            else:
                masklist[peak_ind] = 0
                masklist[peak_ind - 1] = 0
            print(f'masklist: {masklist}')
            Artist.update(artist, props)
            plt.draw()
    else:
        return

fig1, a, b = plotter(wd_merged, meas_merged, figsize=(20,5), title = 'Processed HR Sequences', show=False)
fig1.canvas.mpl_connect('button_press_event', add_or_remove_point)
fig1.canvas.mpl_connect('pick_event', onpick)
plt.show()
