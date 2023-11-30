import numpy as np
import heartpy as hp
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
import itertools


def plotter(working_data, measures, show=True, figsize=None,
            title='Heart Rate Signal Peak Detection', moving_average=True):  # pragma: no cover
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
    ax.plot(plotx, working_data['hr'], color=colorpalette[0], label='heart rate signal', zorder=-10)
    ax.set_xlabel('Time (s)')

    if moving_average:
        ax.plot(plotx, working_data['rolling_mean'], color='gray', alpha=0.5)

    for i in range(0, len(peaklist)-1):
        ax.scatter(peaklist[i]/fs, ybeat[i], color=colorpalette[1], picker=True) # pickradius = 5

    for j in range(0, len(rejectedpeaks)-1):
        ax.scatter(rejectedpeaks[j]/fs, rejectedpeaks_y[j], color=colorpalette[2], label='rejected peaks', picker=True)

    #ax.scatter(np.asarray(peaklist) / fs, ybeat, color=colorpalette[1], label='BPM:%.2f' % (measures['bpm']), picker=True)  # pickradius = 5
    #ax.scatter(rejectedpeaks / fs, rejectedpeaks_y, color=colorpalette[2], label='rejected peaks', picker=True)
    # just another way to generate scatter plot
    #ax.plot(np.asarray(peaklist) / fs, ybeat, 'o',  color=colorpalette[1], label='BPM:%.2f' % (measures['bpm']), picker=True)  # pickradius = 5
    #ax.plot(rejectedpeaks / fs, rejectedpeaks_y, 'o', color=colorpalette[2], label='rejected peaks', picker=True)

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
        return fig

## false green peaks can be set to red and false marked red peaks can be marked green with click
def onpick(event):
    print("Pick handler is called")
    if event.mouseevent.button == 2 and isinstance(event.artist, Artist):
        artist = event.artist
        print(f'artist color just right start:{artist.get_edgecolor()}')
        #print(f'props: {artist.props}')
        #edgecol = artist.get_edgecolor
        artist_edgecolor = np.round(artist.get_edgecolor(), 8)
        print(f'artist_edgecolor: {artist_edgecolor}')
        print(f'artist_edgecolor[0][1]: {artist_edgecolor[0][1]}')
        #artist_edgecolor = '%.8f'% artist.get_edgecolor
        if artist_edgecolor[0][1] == 0.50196078: # color is green #[[0., 0.50196078, 0., 1.]]: #artist.get_edgecolor != [[1., 0., 0., 1.]]:
            props = {"color": "red"}
            print(f'artist color:{artist.get_edgecolor()}')
            print(f'artist:{Artist}')
            print(f'artist:{artist.properties()}')

            Artist.update(artist, props)
            print(f'artist:{artist.properties()}')
            print(f'artist color:{artist.get_edgecolor()}')
            print(f'artist type of edgecolor:{type(artist.get_edgecolor())}')
            #print(f'artist color:{artist.get_facecolor()}')
            print(artist.get_offsets())
            plt.draw()
        elif artist_edgecolor[0][1] != 0.50196078:
            print(f'artist color:{artist.get_edgecolor()}')
            props = {"color": "green"}
            Artist.update(artist, props)
            plt.draw()
    else:
        return

# sample_rate in Hz
sample_rate = 200

# get choosen hr-data sequences
merged_hr = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/file_50.csv', column_name='uV')

merged_hr_hpfiltered = hp.filter_signal(merged_hr, cutoff=5, sample_rate=sample_rate, order=3, filtertype='highpass')
wd_merged, meas_merged = hp.process(merged_hr_hpfiltered, sample_rate=sample_rate)

#pklist_time = wd_merged['peaklist']/sample_rate
heartrate = wd_merged['hr']
peaklist = wd_merged['peaklist']
rolmean = wd_merged['rolling_mean']

fig, ax = plt.subplots(figsize=(16,5))
a = plt.plot(range(len(heartrate)), heartrate, color = 'lightblue')[0]  # [0] in order to use func get_data()later on
# to have single scatterpoints to click (when we use the onpick function)
#for i in range(0,len(b_input)-1):
#    b = plt.scatter(b_input[i], a_input[b_input[i]], color = 'green', s = 50, picker = True, pickradius = 10, zorder = 5)
b = plt.scatter(peaklist, heartrate[peaklist], color = 'green', s = 50, picker = True, pickradius = 10, zorder = 5)
c = plt.plot(range(len(rolmean)), rolmean, color = 'gray', alpha = 0.5)

def add_or_remove_point(event):
    global a
    xydata_a = np.stack(a.get_data(),axis=1)
    print(f'xydata_a: {xydata_a}')
    xdata_a = a.get_xdata()
    print(f'xdata_a: {xdata_a}')
    global b
    xydata_b = b.get_offsets()
    print(f'xydata_b: {xydata_b}')
    xdata_b = b.get_offsets()[:,0]
    print(f'xdata_b: {xdata_b}')

    #click x-value
    xdata_click = event.xdata
    ##index of nearest x-value in a
    # we only accept points on curve
    xdata_nearest_index_a = (np.abs(xdata_a-xdata_click)).argmin()
    #new scatter point x-value
    new_xdata_point_b = xdata_a[xdata_nearest_index_a]
    #new scatter point [x-value, y-value]
    new_xydata_point_b = xydata_a[new_xdata_point_b,:]

    if event.button == 1:
        if new_xdata_point_b not in xdata_b:

            print(f'new_xdata_point_b: {new_xdata_point_b}')
            #insert new scatter point into b
            new_xydata_b = np.insert(xydata_b,0,new_xydata_point_b,axis=0)
            #sort b based on x-axis values
            new_xydata_b = new_xydata_b[np.argsort(new_xydata_b[:,0])]
            #update b
            b.set_offsets(new_xydata_b)
            plt.draw()
    elif event.button == 3:
        if new_xdata_point_b in xdata_b:
            #remove xdata point b
            new_xydata_b = np.delete(xydata_b,np.where(xdata_b==new_xdata_point_b),axis=0)
            print(new_xdata_point_b)
            #update b
            b.set_offsets(new_xydata_b)
        plt.draw()

fig1 = plotter(wd_merged, meas_merged, figsize=(20,5), title = 'Processed HR Sequences', show=False)
print(type(fig1))
#fig.canvas.mpl_connect('pick_event', onpick)
fig.canvas.mpl_connect('button_press_event', add_or_remove_point)
plt.show()

#plt.show()

## Poincare Plot
#hp.plot_poincare(wd_merged, meas_merged, figsize = (20,5), title='Poincare Plot')
#plt.show()