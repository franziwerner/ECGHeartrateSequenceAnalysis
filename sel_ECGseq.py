import numpy as np
import heartpy as hp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import itertools
import os
from matplotlib.artist import Artist

def plotter(working_data, measures, show=True, figsize=None, title='Heart Rate Signal Peak Detection', moving_average=True):
    print("Hello")

    # inititalize Path.Collection in order to merge single scatterplots to a big one
    #d = matplotlib.collections.PathCollection
    #print(f'd: {type(d)}')

    # get color palette
    colorpalette = hp.config.get_colorpalette_plotter()
    print(f'colorpalette: {colorpalette}')

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
    print(f'peaklist: {peaklist}')
    ybeat = working_data['ybeat']
    rejectedpeaks = working_data['removed_beats']
    print(f'rejectedpeaks: {rejectedpeaks}')
    rejectedpeaks_y = working_data['removed_beats_y']

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(title)
    #print(f'plotx: {plotx}')
    #ax.plot(plotx, working_data['hr'], color=colorpalette[0], label='heart rate signal', zorder=-10)
    a = plt.plot(range(len(working_data['hr'])), working_data['hr'], color=colorpalette[0], label='heart rate signal', zorder=-10)[0]
    print(f'a: {a}')
    ax.set_xlabel('sampling points')

    if moving_average:
        #ax.plot(plotx, working_data['rolling_mean'], color='gray', alpha=0.5)
        plt.plot(range(len(working_data['rolling_mean'])), working_data['rolling_mean'], color='gray', alpha=0.5)

    for i in range(0, len(peaklist)): #changed from len(peaklist)-1
        ##ax.scatter(peaklist[i] / fs, ybeat[i], color=colorpalette[1], picker=True)  # pickradius = 5
        b = plt.scatter(peaklist[i], ybeat[i], color=colorpalette[1], picker=True)

    for j in range(0, len(rejectedpeaks)):
        c = plt.scatter(rejectedpeaks[j], rejectedpeaks_y[j], color=colorpalette[2], picker=True)

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
        if not rejectedpeaks.size:
            print("true: rejectedpeaks is empty")
            # TO DO: empty pathCollection (oder einfach nochmal b übergeben und letzten Wert rauslöschen??)
            c = plt.scatter(0,0, color=colorpalette[2])
            #print(f'offsets.shape: {c.offsets.shape}')
            #rejP = False
        #else:
            #rejP = True
        if not peaklist.size:
            print("Peaklist is empty")
            b = plt.scatter(0,0, color=colorpalette[1])

        return fig, a, b, c


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

    # Array to store selected sequences
    choosen_sequence = []
    # make plots
    filenum = 0
    for i in range(start, end, step):
        wd_segment = {}
        m_segment = {}
        mutable_object = {}
        mutable_object['RR_masklist'] = working_data['RR_masklist'][i]
        print(f'mutable_object: {mutable_object}')
        # assign values to sub-object for plotting purposes
        wd_segment['peaklist'] = working_data['peaklist'][i]
        peaklist = wd_segment['peaklist']
        print(f'peaklist: {peaklist}')
        wd_segment['RR_masklist'] = working_data['RR_masklist'][i]
        masklist = wd_segment['RR_masklist']
        print(f'1st masklist: {masklist}')
        print(f'type of masklist: {type(masklist)}')
        wd_segment['ybeat'] = working_data['ybeat'][i]
        wd_segment['removed_beats'] = working_data['removed_beats'][i]
        print(f'working_data[removed_beats][i]: {working_data["removed_beats"][i]}')
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
        fig1, a, b, c = plotter(wd_segment, m_segment, show=False)
        print(f'c.get_offsets: {c.get_offsets()}')

        def add_or_remove_point(event):
            #nonlocal rr_mask
            print(f'event.key: {event.key}')
            nr = 0
            xydata_a = np.stack(a.get_data(), axis=1)
            #print(f'xydata_a: {xydata_a}')
            xdata_a = a.get_xdata()
            #print(f'xdata_a: {xdata_a}')
            # get peak coordinates from automatic peak detection
            xydata_b = b.get_offsets()
            print(f'xydata_b: {xydata_b}')
            xdata_b = b.get_offsets()[:, 0]
            print(f'xdata_b: {xdata_b}')
            # get rejected peaks
            xy_rejPeaks = c.get_offsets()
            x_rejPeaks = c.get_offsets()[:, 0]
            print(f'xy_rejPeaks: {xy_rejPeaks}')
            print(f'x_rejPeaks: {x_rejPeaks}')

            # click x-value
            xdata_click = event.xdata
            ##index of nearest x-value in a
            # we only accept points on curve
            xdata_nearest_index_a = (np.abs(xdata_a - xdata_click)).argmin()
            # new scatter point x-value
            new_xdata_point_b = xdata_a[xdata_nearest_index_a]
            # new scatter point [x-value, y-value]
            new_xydata_point_b = xydata_a[new_xdata_point_b, :]

            if event.button == 2:
                # middle mouse button (set new peak)
                if new_xdata_point_b not in xdata_b:
                    print(f'new_xdata_point_b: {new_xdata_point_b}')
                    # insert new scatter point into b
                    new_xydata_b = np.insert(xydata_b, 0, new_xydata_point_b, axis=0)
                    print(f'new_xydata_b unsorted: {new_xydata_b}')
                    new_xdata_b = new_xydata_b[:,0]
                    print(f'new_xdata_b unsorted: {new_xdata_b}')
                    # sort b based on x-axis values (here: last peak from sequence is still listed)
                    new_xydata_b = new_xydata_b[np.argsort(new_xydata_b[:, 0])]
                    print(f'new_xydata_b sorted: {new_xydata_b}')
                    # update b (peaklist)
                    b.set_offsets(new_xydata_b)
                    ### the newly selected peaks (must be integrated in peaklist)
                    ## when the selected peak is the last in sequence
                    if new_xdata_b[0] == new_xdata_b.max():
                        print("True. Peak Index is max.")
                        new_xdata_peaks = np.delete(new_xydata_b[:, 0], len(new_xydata_b[:, 0]) - 2)
                    else:
                        print("Selected peak is not at max index.")
                        new_xdata_peaks = np.delete(new_xydata_b[:, 0], len(new_xydata_b[:, 0]) - 1)
                    print(f'new_xdata_peaks: {new_xdata_peaks}')
                    print(f'length of new_xdata_peaks: {len(new_xdata_peaks)}')
                    all_peaks = np.concatenate((peaklist, (new_xdata_peaks.astype(int))), axis=0)
                    print(f'all_peaks unsorted: {all_peaks}')
                    # sort entries of updatet peaklist
                    all_peaks = all_peaks[np.argsort(all_peaks)]
                    # update peaklist in dict
                    working_data['peaklist'][i] = all_peaks
                    print(f'all_peaks: {all_peaks}')
                    # update RR_list
                    wd = hp.analysis.calc_rr(working_data['peaklist'][i], sample_rate=200.0)
                    print(f'wd[RR_list]: {wd["RR_list"]}')
                    working_data['RR_list'][i] = wd["RR_list"]
                    print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                    print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                    # update masklist
                    # concatenate or insert in new np.array and then update wd_segment["RR_masklist"]
                    print(f'masklist: {masklist}')
                    # get peak index in all_peaks from newly set peak
                    print(f'new_xdata_b[nr]: {new_xdata_b[nr]}')
                    peakInd = np.where(all_peaks == new_xdata_b[nr])[0][0]
                    print(f'new_xdata_b[nr]: {new_xdata_b[nr]}')
                    print(f'peakInd: {peakInd}')
                    print(f'length all_peaks: {len(all_peaks)}')
                    ## when actual peak is the first in sequence (index = 0)
                    if peakInd == 0:
                        print("First peak in sequence")
                        print(f'length all_peak: {len(all_peaks)}')
                        if (all_peaks[peakInd+1] in xy_rejPeaks[:, 0].astype(int)) or (all_peaks[peakInd+1] in wd_segment['removed_beats']):
                            mutable_object['RR_masklist'] = [1]
                            # concatenate both masklists
                            new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                            print(f'new_mask_array: {new_mask_array}')
                            wd_segment['RR_masklist'] = new_mask_array
                            working_data['RR_masklist'][i] = new_mask_array
                            print(f'length of wd_segment[RR_masklist]: {len(wd_segment["RR_masklist"])}')
                        else:
                            mutable_object['RR_masklist'] = [0]
                            # concatenate both masklists
                            new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                            print(f'new_mask_array: {new_mask_array}')
                            #wd_segment['RR_masklist'] = np.resize(wd_segment['RR_masklist'],(1,13))
                            wd_segment['RR_masklist'] = new_mask_array
                            print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                            print(f'length of wd_segment[RR_masklist]: {len(wd_segment["RR_masklist"])}')
                            print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                            working_data['RR_masklist'][i] = new_mask_array
                    ## when actual peak is the last in sequence
                    elif peakInd == len(all_peaks)-1:
                        print("Last peak in sequence")
                        if (all_peaks[peakInd-1] in xy_rejPeaks[:, 0].astype(int)) or (all_peaks[peakInd-1] in wd_segment['removed_beats']):
                            mutable_object['RR_masklist'] = [1]
                            # concatenate both masklists
                            new_mask_array = np.concatenate((wd_segment["RR_masklist"], mutable_object["RR_masklist"]), axis = 0)
                            #new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                            print(f'new_mask_array: {new_mask_array}')
                            wd_segment["RR_masklist"] = new_mask_array
                            working_data['RR_masklist'][i] = new_mask_array
                        else:
                            mutable_object['RR_masklist'] = [0]
                            # concatenate both masklists
                            new_mask_array = np.concatenate((wd_segment["RR_masklist"], mutable_object["RR_masklist"]), axis=0)
                            #new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                            print(f'new_mask_array: {new_mask_array}')
                            wd_segment["RR_masklist"] = new_mask_array
                            working_data['RR_masklist'][i] = new_mask_array
                    ## when newly set peak is not first nor last peak in sequence
                    else:
                        if (all_peaks[peakInd-1] in xy_rejPeaks[:, 0].astype(int)) or (all_peaks[peakInd-1] in wd_segment['removed_beats']):
                            if (all_peaks[peakInd+1] in xy_rejPeaks[:, 0].astype(int)) or (all_peaks[peakInd+1] in wd_segment['removed_beats']):
                                print("Peaks before and after actual peak are red")
                                mutable_object['RR_masklist'] = [1,1]
                                print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                # concatenate both masklists
                                new_mask_array = np.insert(wd_segment["RR_masklist"],peakInd-1, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                new_mask_array = np.delete(new_mask_array, peakInd+1)
                                print(f'new_mask_array: {new_mask_array}')
                                # update wd_segment["RR_masklist"]
                                wd_segment["RR_masklist"] = new_mask_array
                                working_data['RR_masklist'][i] = new_mask_array
                            else:
                                print("Peak before actual peak is red and peak after actual peak is green")
                                mutable_object['RR_masklist'] = [1, 0]
                                print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd - 1, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                new_mask_array = np.delete(new_mask_array, peakInd + 1)
                                print(f'new_mask_array: {new_mask_array}')
                                # update wd_segment["RR_masklist"]
                                wd_segment["RR_masklist"] = new_mask_array
                                working_data['RR_masklist'][i] = new_mask_array
                        elif (all_peaks[peakInd-1] not in xy_rejPeaks[:, 0].astype(int)) or (all_peaks[peakInd-1] not in wd_segment['removed_beats']):
                            if (all_peaks[peakInd+1] in xy_rejPeaks[:, 0].astype(int)) or (all_peaks[peakInd+1] in wd_segment['removed_beats']):
                                print("Peak before actual peak is green and peak after actual peak is red")
                                mutable_object['RR_masklist'] = [0, 1]
                                print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd - 1, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                new_mask_array = np.delete(new_mask_array, peakInd + 1)
                                print(f'new_mask_array: {new_mask_array}')
                                # update wd_segment["RR_masklist"]
                                wd_segment["RR_masklist"] = new_mask_array
                                working_data['RR_masklist'][i] = new_mask_array
                            else:
                                print("Peak before actual peak is green and peak after actual peak is green")
                                mutable_object['RR_masklist'] = [0, 0]
                                print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd - 1, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                new_mask_array = np.delete(new_mask_array, peakInd + 1)
                                print(f'new_mask_array: {new_mask_array}')
                                # update wd_segment["RR_masklist"]
                                wd_segment["RR_masklist"] = new_mask_array
                                working_data['RR_masklist'][i] = new_mask_array

                    print(f'peakInd: {peakInd}')
                    plt.draw()
            elif event.button == 3:
                # right mouse button (delete only self-set points! (leave red-marked points that are correct)
                if new_xdata_point_b in xdata_b:
                    print(f'peaklist: {peaklist}')
                    # remove xdata point b
                    new_xydata_b = np.delete(xydata_b, np.where(xdata_b == new_xdata_point_b), axis=0)
                    print(f'new_xdata_point_b: {new_xdata_point_b}')
                    print(f'new_xydata_b: {new_xydata_b}')
                    print(f'type of new_xydata_b: {type(new_xydata_b)}')
                    # update b
                    b.set_offsets(new_xydata_b)
                    ### the newly rejected peaks (must be removed from peaklist) and the last peak in sequence
                    new_xdata_peaks = np.delete(new_xydata_b[:, 0], len(new_xydata_b[:, 0]) - 1)
                    print(f'new_xdata_peaks: {new_xdata_peaks}')
                    print(f'peaklist: {peaklist}')
                    all_peaks = np.concatenate((peaklist, (new_xdata_peaks.astype(int))), axis=None)
                    # sort entries of updatet peaklist (that final peaklist (when saving respective sequence plot) needs to be used for calculating RR-distances)
                    all_peaks = all_peaks[np.argsort(all_peaks)]
                    # update peaklist
                    working_data['peaklist'][i] = all_peaks
                    # calculate new RR-list
                    wd = hp.analysis.calc_rr(working_data['peaklist'][i], sample_rate=200.0)
                    print(f'wd[RR_list]: {wd["RR_list"]}')
                    # update RR_list
                    working_data['RR_list'][i] = wd["RR_list"]
                    print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                    print(f'all_peaks: {all_peaks}')
                    print(f'length all_peaks: {len(all_peaks)}')
                    peakI = len(np.where(peaklist < new_xdata_point_b)[0])
                    print(f'peakI: {peakI}')
                    ## Peak to delete is the first peak in sequence
                    if peakI == 0:
                        print("First peak in sequence")
                        print(f'length all_peak: {len(all_peaks)}')
                        # delete respective entry from masklist
                        new_mask_array = np.delete(wd_segment["RR_masklist"], peakI, axis=None)
                        print(f'new_mask_array: {new_mask_array}')
                        wd_segment["RR_masklist"] = new_mask_array
                        working_data['RR_masklist'][i] = new_mask_array
                    ## Peak to delete is the last in sequence, needs to be checked!!
                    elif peakI == (len(all_peaks)):
                        print("Last peak in sequence")
                        new_mask_array = np.delete(wd_segment["RR_masklist"], len(wd_segment["RR_masklist"])-1, axis=None)
                        print(f'new_mask_array: {new_mask_array}')
                        wd_segment["RR_masklist"] = new_mask_array
                        working_data['RR_masklist'][i] = new_mask_array
                    ## Peak to delete is somewhere inbetween
                    else:
                        print("Peak to delete is somewhere inbetween")
                        new_mask_array = np.delete(wd_segment["RR_masklist"], peakI-1, axis=None)
                        print(f'new_mask_array: {new_mask_array}')
                        wd_segment["RR_masklist"] = new_mask_array
                        working_data['RR_masklist'][i] = new_mask_array
                    plt.draw()

        ## false green peaks can be set to red and false marked red peaks can be marked green with click
        ## only meant for the peaks that are set by the program
        def onpick(event):
            xy_rejPeaks = c.get_offsets()
            x_rejPeaks = c.get_offsets()[:, 0]
            print(f'xy_rejPeaks: {xy_rejPeaks}')
            print(f'x_rejPeaks: {x_rejPeaks}')
            #artist = event.artist
            #sel_point = artist.get_offsets()
            #sel_peak = (artist.get_offsets()[:, 0]).astype(int)

            if event.mouseevent.button == 1 and isinstance(event.artist, Artist):
                artist = event.artist
                sel_point = artist.get_offsets()
                sel_peak = (artist.get_offsets()[:, 0]).astype(int)
                print(f'sel_peak: {sel_peak}')
                print(f'peaklist: {peaklist}')
                #print(f'path_collection sizes: {c.get_sizes()}')
                artist_edgecolor = np.round(artist.get_edgecolor(), 8)
                # peak is actually green and is set to red
                if artist_edgecolor[0][1] == 0.50196078:
                    props = {"color": "red"}
                    Artist.update(artist, props)
                    ## add sel_peak to array xy_rejPeaks and to wd_segment['removed_beats']
                    xy_rejPeaks = np.insert(xy_rejPeaks, 0, sel_point, axis = 0)
                    wd_segment['removed_beats'] = np.insert(wd_segment['removed_beats'], 0, sel_peak, axis=0)
                    working_data['removed_beats'][i] = np.insert(working_data['removed_beats'][i], 0, sel_peak, axis = 0)
                    print(f'working_data["removed_beats"][i]: {working_data["removed_beats"][i]}')
                    print(f'wd_segment["removed_beats"]: {wd_segment["removed_beats"]}')
                    print(f'xy_rejPeaks: {xy_rejPeaks}')
                    print(f'type of xy_rejPeaks: {type(xy_rejPeaks)}')
                    ## update c
                    c.set_offsets(xy_rejPeaks)
                    plt.draw()
                    # get index from red marked peak
                    peak_ind = np.where(peaklist == sel_peak[0])[0][0]
                    print(f'peak_ind: {peak_ind}')
                    # set index and index-1 in masklist to 1 (1 means that this peak is not considered later on)
                    print(f'masklist: {masklist}')
                    # peak is the first in sequence
                    if peak_ind == 0:
                        masklist[peak_ind] = 1
                    # peak is the last in sequence
                    elif peak_ind == len(peaklist)-1:
                        print("I am the last peak in this sequence plot")
                        masklist[peak_ind-1] = 1
                    # peak is within sequence
                    else:
                        print("Here I am right")
                        masklist[peak_ind] = 1
                        masklist[peak_ind-1] = 1
                    print(f'masklist: {masklist}')
                    print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
            elif event.mouseevent.button == 3 and isinstance(event.artist, Artist):
                artist = event.artist
                sel_peak = (artist.get_offsets()[:, 0]).astype(int)
                artist_edgecolor = np.round(artist.get_edgecolor(), 8)
                # peak is actually red (and is set to green)
                if artist_edgecolor[0][1] != 0.50196078:
                    props = {"color": "green"}
                    print(f'removedpeaks: {working_data["removed_beats"][i]}')
                    # delete sel_peak from xy_rejPeaks (only necessary, when last rejected peak in sequence is deleted) and from wd_segment['removed_beats']
                    xy_rejPeaks = np.delete(xy_rejPeaks, np.where(x_rejPeaks == sel_peak), axis=0) #np.delete(xy_rejPeaks, 0, sel_point, axis=0)
                    wd_segment['removed_beats'] = np.delete(wd_segment['removed_beats'], np.where(wd_segment['removed_beats'] == sel_peak), axis=0)
                    working_data['removed_beats'][i] = np.delete(working_data['removed_beats'][i], np.where(working_data['removed_beats'][i] == sel_peak), axis=0)
                    print(f'xy_rejPeaks after deleting: {xy_rejPeaks}')
                    print(f'wd_segment removed_beats after deleting: {wd_segment["removed_beats"]}')
                    print(f'working_data[removed_beats][i] removed_beats after deleting: {working_data["removed_beats"][i]}')
                    # update c
                    c.set_offsets(xy_rejPeaks)
                    # get x_rejPeaks
                    print(f'x_rejPeaks after deleting: {(xy_rejPeaks[:,0]).astype(int)}')
                    # get index from green marked peak
                    peak_ind = np.where(peaklist == sel_peak[0])[0][0]
                    print(f'peak_ind: {peak_ind}')
                    # set index and index-1 in masklist to 0 (0 means that this peak is considered later on)
                    print(f'masklist: {masklist}')
                    # adapt masklist for changed first peak in peaklist
                    if peak_ind == 0:
                        if (peaklist[peak_ind+1] in xy_rejPeaks[:,0].astype(int)) or (peaklist[peak_ind+1] in wd_segment['removed_beats']):
                            print("true")
                            masklist[peak_ind] = 1
                        else:
                            print("false")
                            masklist[peak_ind] = 0
                    # adapt masklist for changed last peak in peaklist
                    elif peak_ind == len(peaklist)-1:
                        print("I am the last peak in this plot")
                        if (peaklist[peak_ind-1] in xy_rejPeaks[:,0].astype(int)) or (peaklist[peak_ind-1] in wd_segment['removed_beats']):
                            masklist[peak_ind-1] = 1
                        else:
                            masklist[peak_ind-1] = 0
                    # adapt masklist for a changed peak in between
                    else:
                        if (peaklist[peak_ind-1] in xy_rejPeaks[:,0].astype(int)) or (peaklist[peak_ind-1] in wd_segment['removed_beats']):
                            if peaklist[peak_ind+1] in xy_rejPeaks[:,0].astype(int) or (peaklist[peak_ind+1] in wd_segment['removed_beats']):
                                print("I am in 1 and 1")
                                masklist[peak_ind-1] = 1
                                masklist[peak_ind] = 1
                            else:
                                print("I am in 1 and 0")
                                masklist[peak_ind-1] = 1
                                masklist[peak_ind] = 0
                        elif (peaklist[peak_ind-1] not in xy_rejPeaks[:,0].astype(int)) and (peaklist[peak_ind-1] not in wd_segment['removed_beats']):
                            print(f'peaklist[peak_ind-1]: {peaklist[peak_ind-1]}')
                            if (peaklist[peak_ind+1] in xy_rejPeaks[:,0].astype(int)) or (peaklist[peak_ind+1] in wd_segment['removed_beats']):
                                print("I am in 0 and 1")
                                masklist[peak_ind-1] = 0
                                masklist[peak_ind] = 1
                            else:
                                print("I am in 0 and 0")
                                masklist[peak_ind - 1] = 0
                                masklist[peak_ind] = 0

                    print(f'masklist: {masklist}')
                    print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                    Artist.update(artist, props)
                    plt.draw()
            else:
                return

        cid = fig1.canvas.mpl_connect('button_press_event', add_or_remove_point)
        cid2 = fig1.canvas.mpl_connect('pick_event', onpick)
        fig1.canvas.mpl_disconnect(cid)
        fig1.canvas.mpl_disconnect(cid2)

        # save and discard buttons
        plt.subplots_adjust(bottom=0.25)
        ax_button = plt.axes([0.25, 0.1, 0.08, 0.05])
        save_button = Button(ax_button, 'Save', color='white', hovercolor='grey')
        ax_button2 = plt.axes([0.15, 0.1, 0.09, 0.05])
        discard_button = Button(ax_button2, 'Discard', color='white', hovercolor='grey')
        # mode buttons
        ax_button3 = plt.axes([0.35, 0.1, 0.12, 0.05])
        add_rem_button = Button(ax_button3, 'Add_Rem', color='white', hovercolor='grey')
        ax_button4 = plt.axes([0.50, 0.1, 0.12, 0.05])
        red_green_button = Button(ax_button4, 'Red_Green', color='white', hovercolor='grey')

        # saving/discarding figure
        def savefct(val):  # val is the value of the button
            fig1.savefig('%s%s%i.png' % (path, subject, filenum))
            choosen_sequence.append(1)
            #rr_mask.append()
            plt.close('all')

        def discardfct(val):
            choosen_sequence.append(0)
            plt.close('all')

        def add_rem(val):
            fig1.canvas.mpl_disconnect(cid2)
            cid = fig1.canvas.mpl_connect('button_press_event', add_or_remove_point)

        def change_red_green(val):
            fig1.canvas.mpl_disconnect(cid)
            cid2 = fig1.canvas.mpl_connect('pick_event', onpick)

        save_button.on_clicked(savefct)
        discard_button.on_clicked(discardfct)
        add_rem_button.on_clicked(add_rem)
        red_green_button.on_clicked(change_red_green)

        plt.show()
        filenum += 1
        print(f'wd_segment at end: {wd_segment["RR_masklist"]}')
        print(f'working_data at end: {working_data["RR_masklist"][i]}')


    return choosen_sequence

# subject
subject = 'sub03_'

# sample_rate in Hz
sample_rate = 200

# get raw data (header and data)
hrdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi03_part.csv', column_name='uV')
timerdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi03_part.csv', column_name='dt')

# bandpass filter given by heartpy
bp_filtered = hp.filter_signal(hrdata_3rd, cutoff=[7,21], sample_rate=sample_rate, order=3, filtertype='bandpass')

# create working_data dict, in which we can integrate merged arrays later on (in order to enable poincare plot)
# here in process-function: calc_poincare for complete data set
wd_whole_epi, meas_whole_epi = hp.process(bp_filtered, sample_rate=sample_rate)
print(f'working_data wd_whole_epi: {wd_whole_epi}')
print(f'Peaklist whole epi at beginning: {wd_whole_epi["peaklist"]}')
print(f'RR_masklist whole connected epi at beginning: {wd_whole_epi["RR_masklist"]}')
print(f'RR_list whole connected epi at beginning: {wd_whole_epi["RR_list"]}')
print(f'RR_list_cor whole connected epi at beginning: {wd_whole_epi["RR_list_cor"]}')

# get user input and convert text to number
seq_width = int(input("Sequence width: "))

# process segmentwise (just the processing, not the plotting yet)
work_data, meas = hp.process_segmentwise(bp_filtered, sample_rate=sample_rate, segment_width=seq_width)
print(f'meas: {meas}')

# Array to store selected hr data (we do not need for the moment!)
stitched_hr_data = []
# Array to store peaklists of single sequences
stitched_peaklists = []
# Array to store RR_masklists
stitched_RR_masklists = []
# Array to store RR_lists
stitched_RR_lists = []
# Arry to store removed_beats
stitched_removed_beats = []

choosen_seq = sequence_plotter(work_data, meas, path='/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/segmentwise_plotting/', subject=subject)
print(f'meas1: {meas}')
print(f'choosen_seq: {choosen_seq}')
print(f'work_data[peaklist][0]: {work_data["peaklist"][0]}')
print(f'work_data[peaklist][1]: {work_data["peaklist"][1]}')
print(f'work_data[RR_masklist][0]: {work_data["RR_masklist"][0]}')
print(f'work_data[RR_list][0]: {work_data["RR_list"][0]}')
print(f'work_data[removed_beats][0]: {work_data["removed_beats"][0]}')

# sequences selected by the user are stitched together
# peaklists and removed_beats need to be recalculated (because indexing starts anew with each sequence)
nr_samplepoints_per_seq = seq_width * sample_rate
print(f'nr_samplepoints_per_seq: {nr_samplepoints_per_seq}')
print(f'length choosen_seq: {len(choosen_seq)}')

for j in range(0, len(choosen_seq)):
    print(f'j: {j}')
    if choosen_seq[j] == 1:
        stitched_hr_data.append(work_data['hr'][j])
        stitched_peaklists.append(work_data['peaklist'][j] + (j * nr_samplepoints_per_seq))
        stitched_removed_beats.append(work_data['removed_beats'][j] + (j * nr_samplepoints_per_seq))
        stitched_RR_masklists.append(work_data['RR_masklist'][j])
        stitched_RR_lists.append(work_data['RR_list'][j])
    else:
        print(f'sequence {j + 1} is not appended.')
        stitched_hr_data.append(np.zeros(nr_samplepoints_per_seq))

print(f'stitched_peaklists: {stitched_peaklists}')
print(f'length stitched_peaklists: {len(stitched_peaklists)}')
print(f'length single entry in stitched_peaklists: {len(stitched_peaklists[0])}')
print(f'stitched_RR_masklists: {stitched_RR_masklists}')
print(f'length single entry in stitched_RR_masklists: {len(stitched_RR_masklists[0])}')
print(f'stitched_RR_lists: {stitched_RR_lists}')
print(f'length single entry in stitched_RR_lists: {len(stitched_RR_lists[0])}')
print(f'length stitched_hr_data: {len(stitched_hr_data)}')

# we need to fill up RR_list and RR_masklist to take into account the transitions between the individual sequences
# distance between last peak in one sequence and first peak in subsequent sequence is not yet taken into account
# RR_list and RR_masklist must be of length (len(peaklist)-1)
for i in range(0, len(stitched_peaklists)-1):
    rr_diff_trans = ((stitched_peaklists[i+1][0] - stitched_peaklists[i][len(stitched_peaklists[i]) - 1]) * 1000)/sample_rate
    # at the moment we do not take the transition differences into account (we leave them out; do not consider them for calculation measures)
    stitched_RR_masklists[i] = np.append(stitched_RR_masklists[i], 1)
    stitched_RR_lists[i] = np.append(stitched_RR_lists[i], rr_diff_trans)

print(f'last array entry stitched_peaklists[0]: {stitched_peaklists[0][len(stitched_peaklists[0])-1]}')
print(f'first array entry stitched_peaklists[1]: {stitched_peaklists[1][0]}')
#rr_diff_trans = ((stitched_peaklists[1][0] - stitched_peaklists[0][len(stitched_peaklists[0])-1])*1000)/200
print(f'stitched_RR_lists: {stitched_RR_lists}')
print(f'length single entry in stitched_RR_lists: {len(stitched_RR_lists[0])}')
print(f'length single entry in stitched_RR_masklists: {len(stitched_RR_masklists[0])}')
print(f'stitched_RR_masklists: {stitched_RR_masklists}')

# merges stitched lists to one big list
merged_hr = list(itertools.chain(*stitched_hr_data))
merged_peaklists = list(itertools.chain(*stitched_peaklists))
print(f'length merged_peaklists: {len(merged_peaklists)}')
merged_RR_masklist = list(itertools.chain(*stitched_RR_masklists))
merged_RR_list = list(itertools.chain(*stitched_RR_lists))
merged_removed_beats = list(itertools.chain(*stitched_removed_beats))
print(f'length merged_RR_list: {len(merged_RR_list)}')
print(f'length merged_RR_masklist: {len(merged_RR_masklist)}')
print(f'length merged_removed_beats: {len(merged_removed_beats)}')

### put merged lists in working_data dict of whole episode
wd_whole_epi['hr'] = merged_hr
wd_whole_epi['peaklist'] = merged_peaklists
wd_whole_epi['RR_masklist'] = merged_RR_masklist
wd_whole_epi['RR_list'] = merged_RR_list
wd_whole_epi['removed_beats'] = merged_removed_beats
print(f'removed_beats whole epi final: {wd_whole_epi["removed_beats"]}')
print(f'peaklist whole epi final: {wd_whole_epi["peaklist"]}')
print(f'RR_masklist whole epi final: {wd_whole_epi["RR_masklist"]}')
print(f'RR_list whole epi final: {wd_whole_epi["RR_list"]}')
print(f'meas_whole_epi: {meas_whole_epi}')
print(f'ybeat: {wd_whole_epi["ybeat"]}')

## recalculate wd parameters that are used for calculation of measures
# Calculation of ybeat might be wrong (in peaklist also the rejected ones are listed!!!)
print(f'length merged_hr: {len(merged_hr)}')
print(f'merged_peaklists: {merged_peaklists}')
wd_whole_epi['ybeat'] = [merged_hr[x] for x in merged_peaklists]
rr_list_cor = np.array([merged_RR_list[i] for i in range (len(merged_RR_masklist)) if merged_RR_masklist[i] == 0])
wd_whole_epi['RR_diff_cor'] = rr_list_cor
print(f'rr_list_cor: {rr_list_cor}')
wd_whole_epi['removed_beats_y'] = [merged_hr[x] for x in merged_removed_beats]
rr_diff = np.abs(np.diff(rr_list_cor))
print(f'rr_diff: {rr_diff}')
rr_sqdiff = np.power(rr_diff, 2)

## Question: Couldn't it be easier?? (because I already calculated rr_list_cor) -> yes!
## the following just takes the differences of subsequent RR-distances into account (not interrupted by red peak)
## this is what we do not want; we want to take into account all differences of valid RR-distances, even if they are not in direct succession
# rr_masked shows all RR-differences that are valid (don't interrupted by red peak) and also marks the positions in the array that are not valid with --
# rr_masked = np.ma.array(merged_RR_list, mask=merged_RR_masklist)
# print(f'rr_masked: {rr_masked}')
# rr_diff = np.abs(np.diff(rr_masked))
# print(f'rr_diff2: {rr_diff}')
# rr_diff = rr_diff[~rr_diff.mask]
# print(f'rr_diff: {rr_diff}')
# rr_sqdiff = np.power(rr_diff, 2)

wd_whole_epi['RR_diff'] = rr_diff
wd_whole_epi['RR_sqdiff'] = rr_sqdiff

#print(f'wd_whole_epi 1: {wd_whole_epi}')

# func calc_ts_measures calculates BPM, IBI, SDNN, SDSD, RMSSD, pNN20, pNN50, MAD
wd_whole_epi, meas_whole_epi = hp.analysis.calc_ts_measures(rr_list_cor, rr_diff, rr_sqdiff, measures = meas_whole_epi, working_data = wd_whole_epi)

#wd_whole_epi['sample_rate'] = sample_rate
#print(f'wd_whole_epi["sample_rate"]: {wd_whole_epi["sample_rate"]}')
#print(f'wd_whole_epi 2: {wd_whole_epi}')
print(f'wd_whole_epi["rolling_mean"]: {wd_whole_epi["rolling_mean"]}')

# calc rolling_mean
rol_mean = hp.datautils.rolling_mean(merged_hr, 0.75, sample_rate)
wd_whole_epi['rolling_mean'] = rol_mean

# plot merged dataset to proof whether algorithm worked correctly
hp.plotter(wd_whole_epi, meas_whole_epi)
plt.show()

# calc_poincare just needs working_data for calculation, but throws an error when the other parameter are missing; measures is only needed for writing in the
# recalculated SD1, SD2 ... parameter
# func works with rr_list and rr_masklist
#meas_poincare = hp.analysis.calc_poincare(merged_RR_list, rr_mask = merged_RR_masklist, measures=meas_whole_epi, working_data=wd_whole_epi)
meas_poincare = hp.analysis.calculation_poincare(measures=meas_whole_epi, working_data=wd_whole_epi)

print(f'meas_poincare: {meas_poincare}')
print(f'meas_whole_epi1: {meas_whole_epi}')

## Poincare Plot (kommt bei beiden das gleiche raus, weil wir innerhalb von calc_poincare in measures schreiben und das dann in beiden measures dicts drin)
# bei beiden kommt das gleiche raus, weil nur die
#hp.plot_poincare(wd_whole_epi, meas_whole_epi, figsize = (20,5), title='Poincare Plot 1')
#plt.show()
hp.plot_poincare(wd_whole_epi, meas_poincare, figsize = (20,5), title='Poincare Plot 2')
plt.show()