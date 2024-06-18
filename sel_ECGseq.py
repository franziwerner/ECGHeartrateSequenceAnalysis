import numpy as np
import heartpy as hp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import itertools
import os
from matplotlib.artist import Artist
import csv

def plotter(working_data, measures, show=True, figsize=None, title='Heart Rate Signal Peak Detection', moving_average=True):

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

    # later on (set.offsets) plotter is called with show = False
    if show:
        fig.show()
    else:
        if not rejectedpeaks.size:
            print("true: rejectedpeaks is empty")
            # TO DO: empty pathCollection (oder einfach nochmal b übergeben und letzten Wert rauslöschen??)
            c = plt.scatter(0, 0, color=colorpalette[2])
            #print(f'offsets.shape: {c.offsets.shape}')
            #rejP = False
        #else:
            #rejP = True
        if not peaklist.size:
            print("Peaklist is empty")
            b = plt.scatter(0, 0, color=colorpalette[1])

        return fig, ax, a, b, c


### core func: plots user-defined sequences and allows the automatically determined peak values to be changed manually
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
        # assign values to sub-object for plotting purposes
        wd_segment['peaklist'] = working_data['peaklist'][i]
        peaklist = wd_segment['peaklist']
        #lastAutoPeak = peaklist[len(peaklist)-1]
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
        # a contains hr data
        # b contains peaks
        # c contains rejected peaks
        fig1, ax, a, b, c = plotter(wd_segment, m_segment, show=False)
        print(f'c.get_offsets: {c.get_offsets()}')

        def add_or_remove_point(event):
            if event.inaxes in [ax]:
                nr = 0
                xydata_a = np.stack(a.get_data(), axis=1)
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
                print(f'x_rejPeaks: {x_rejPeaks}')
                ## delete entry if it is the last in rejPeaks
                # if xy_rejPeaks[len(xy_rejPeaks)-1] in xydata_b:
                #     print("Deletion is necessary")
                #     xydata_b = np.delete(xydata_b, np.where(xydata_b == xy_rejPeaks[len(xy_rejPeaks) - 1]))
                #     print(f'xydata_b after deletion: {xydata_b}')
                # else:
                #     print("Deletion is not necessary")
                # click x-value
                xdata_click = event.xdata
                #print(f'xdata_click: {xdata_click}')
                ##index of nearest x-value in a
                # we only accept points on curve
                xdata_nearest_index_a = (np.abs(xdata_a - xdata_click)).argmin()
                #print(f'xdata_nearest_index_a: {xdata_nearest_index_a}')

                ## NEW!!! (set point has to be max of curve part)
                xmin = xdata_nearest_index_a - 10 # value of 10 is still arbitrary (what is the most suited value?)
                xmax = xdata_nearest_index_a + 10
                subarr = xdata_a[xmin:xmax]
                #print(f'subarr: {subarr}')
                xydata_a_subarr = xydata_a[subarr, :]
                #print(f'xydata_a_subarr: {xydata_a_subarr}')
                ydata_a_subarr = xydata_a_subarr[:,1]
                #print(f'ydata_a_subarr: {ydata_a_subarr}')
                # the following two lines are unnecessary (we just need the index of max value), but for checking whether everything works fine
                maxV = max(ydata_a_subarr)
                #print(f'maxV: {maxV}')
                indexMaxV = np.argmax(ydata_a_subarr)
                #print(f'index maxV: {indexMaxV}')

                # new scatter point [x-value, y-value]
                # subarr contains indices from hr (5s sequence: indices from 0-999)
                new_xdata_point_b = subarr[indexMaxV]
                print(f'new_xdata_point_b: {new_xdata_point_b}')
                new_xydata_point_b = xydata_a[new_xdata_point_b, :]
                print(f'new_xydata_point_b: {new_xydata_point_b}')

                if event.button == 2:
                    # middle mouse button (set new peak)
                    if new_xdata_point_b not in wd_segment['peaklist']:
                        print(f'new_xdata_point_b: {new_xdata_point_b}')
                        # insert new scatter point into b
                        #print(f'xydata_b beforde deletion: {xydata_b[0]}')
                        ## if-Abfrage: wenn letzter Peak noch in rejPeaks -> aus xydata_b entfernen!
                        # if xydata_b[0][0] == xy_rejPeaks[0][0] and xydata_b[0][0] not in wd_segment['removed_beats']:
                        #     print("True. The last peak seems to be deleted completely, but is still listed in xy_rejPeaks")
                        #     print(f'xy_rejPeaks[0][0]: {xy_rejPeaks[0][0]}')
                        #     print(f'type of xydata_b: {type(xydata_b)}')
                        #     #xydata_b = np.array([])
                        #     #xydata_b = np.delete(xydata_b, [0][0])
                        #     xydata_b = np.delete(xydata_b, np.where(xydata_b[0] == xy_rejPeaks[0]))
                        #     print(f'xydata_b after deletion: {xydata_b}')
                        #     print(f'type of xydata_b: {type(xydata_b)}')
                        # else:
                        #     print("Everything is fine. Program can go on.")
                        new_xydata_b = np.insert(xydata_b, 0, new_xydata_point_b, axis=0)
                        print(f'new_xydata_b: {new_xydata_b}')
                        wd_segment['peaklist'] = np.insert(wd_segment['peaklist'], 0, new_xdata_point_b, axis=0)
                        print(f'wd_segment[peaklist] unsorted: {wd_segment["peaklist"]}')
                        #print(f'new_xydata_b unsorted: {new_xydata_b}')
                        print(f'length from xydata_b: {len(new_xydata_b)}')
                        ### NEW bis else:
                        #if len(new_xydata_b) == 2:
                        #    new_xdata_b = new_xydata_b[[0]]
                        #else:
                        new_xdata_b = new_xydata_b[:,0]
                        print(f'new_xdata_b unsorted: {new_xdata_b}')
                        # sort peaklist by size
                        wd_segment['peaklist'] = np.sort(wd_segment['peaklist'])
                        #print(f'wd_segment[peaklist] sorted: {wd_segment["peaklist"]}')
                        # sort b based on x-axis values (here: last peak from sequence is still listed (in new_xydata_b))
                        ### NEW bis else:
                        #if len(new_xydata_b) == 2:
                        #    new_xydata_b = new_xydata_b
                        #else:
                        new_xydata_b = new_xydata_b[np.argsort(new_xydata_b[:, 0])]
                        print(f'new_xydata_b sorted: {new_xydata_b}')
                        # update b (peaklist)
                        b.set_color('green')
                        b.set_offsets(new_xydata_b)
                        plt.draw()
                        ### the newly set peak (must be integrated in peaklist), but only the ones that are set manually (not the lastAutoPeak)
                        new_xdata_peaks = np.delete(new_xydata_b[:,0], np.where(new_xydata_b[:,0] == peaklist[len(peaklist)-1]))
                        print(f'new_xdata_peaks: {new_xdata_peaks}')
                        print(f'length of new_xdata_peaks: {len(new_xdata_peaks)}')
                        working_data['peaklist'][i] = wd_segment['peaklist']
                        print(f'working_data[peaklist][i]: {working_data["peaklist"][i]}')
                        # update RR_list
                        wd = hp.analysis.calc_rr(wd_segment['peaklist'], sample_rate=200.0)
                        working_data['RR_list'][i] = wd["RR_list"]
                        print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                        # concatenate or insert in new np.array and then update wd_segment["RR_masklist"]
                        # get peak index from newly set peak
                        print(f'new_xdata_b[nr]: {new_xdata_b[nr]}')
                        peakInd = np.where(wd_segment['peaklist'] == new_xdata_b[nr])[0][0]
                        print(f'new_xdata_b[nr]: {new_xdata_b[nr]}')
                        print(f'peakInd: {peakInd}')
                        print(f'xy_rejPeaks: {xy_rejPeaks}')
                        print(f'wd_segment[removed_beats]: {wd_segment["removed_beats"]}')
                        print(f'wd_segment[peaklist]: {wd_segment["peaklist"]}')
                        # update MASKLIST
                        # when actual peak is the first in sequence (index = 0)
                        if peakInd == 0:
                            print("First peak in sequence")
                            print(f'length all_peak: {len(wd_segment["peaklist"])}')
                            if (wd_segment['peaklist'][peakInd+1] in wd_segment['removed_beats']):
                                mutable_object['RR_masklist'] = [1]
                                # concatenate both masklists
                                new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                wd_segment['RR_masklist'] = new_mask_array
                                working_data['RR_masklist'][i] = new_mask_array
                                print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                print(f'length of wd_segment[RR_masklist]: {len(wd_segment["RR_masklist"])}')
                            else:
                                mutable_object['RR_masklist'] = [0]
                                # concatenate both masklists
                                new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                wd_segment['RR_masklist'] = new_mask_array
                                #print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                                print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                print(f'length of wd_segment[RR_masklist]: {len(wd_segment["RR_masklist"])}')
                                print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                                working_data['RR_masklist'][i] = new_mask_array
                        ## when actual peak is the last in sequence
                        elif peakInd == len(wd_segment['peaklist'])-1:
                            print("Last peak in sequence")
                            if (wd_segment['peaklist'][peakInd-1] in wd_segment['removed_beats']):
                                mutable_object['RR_masklist'] = [1]
                                # concatenate both masklists
                                new_mask_array = np.concatenate((wd_segment["RR_masklist"], mutable_object["RR_masklist"]), axis = 0)
                                #new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                wd_segment["RR_masklist"] = new_mask_array
                                working_data['RR_masklist'][i] = new_mask_array
                            else:
                                mutable_object['RR_masklist'] = [0]
                                # concatenate both masklists
                                new_mask_array = np.concatenate((wd_segment["RR_masklist"], mutable_object["RR_masklist"]), axis=0)
                                #new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd, mutable_object["RR_masklist"], axis=0)
                                print(f'new_mask_array: {new_mask_array}')
                                print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                wd_segment["RR_masklist"] = new_mask_array
                                working_data['RR_masklist'][i] = new_mask_array
                        ## when newly set peak is not first nor last peak in sequence
                        else:
                            if (wd_segment['peaklist'][peakInd-1] in wd_segment['removed_beats']):
                                if (wd_segment['peaklist'][peakInd+1] in wd_segment['removed_beats']):
                                    print("Peaks before and after actual peak are red")
                                    mutable_object['RR_masklist'] = [1,1]
                                    print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                    # concatenate both masklists
                                    new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd-1, mutable_object["RR_masklist"], axis=0)
                                    new_mask_array = np.delete(new_mask_array, peakInd+1)
                                    print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                    print(f'new_mask_array: {new_mask_array}')
                                    # update wd_segment["RR_masklist"]
                                    wd_segment["RR_masklist"] = new_mask_array
                                    working_data['RR_masklist'][i] = new_mask_array
                                else:
                                    print("Peak before actual peak is red and peak after actual peak is green")
                                    mutable_object['RR_masklist'] = [1, 0]
                                    print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                    new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd - 1, mutable_object["RR_masklist"], axis=0)
                                    new_mask_array = np.delete(new_mask_array, peakInd + 1)
                                    print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                    print(f'new_mask_array: {new_mask_array}')
                                    # update wd_segment["RR_masklist"]
                                    wd_segment["RR_masklist"] = new_mask_array
                                    working_data['RR_masklist'][i] = new_mask_array
                            elif (wd_segment['peaklist'][peakInd-1] not in wd_segment['removed_beats']):
                                if (wd_segment['peaklist'][peakInd+1] in wd_segment['removed_beats']):
                                    print("Peak before actual peak is green and peak after actual peak is red")
                                    mutable_object['RR_masklist'] = [0, 1]
                                    print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                    new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd - 1, mutable_object["RR_masklist"], axis=0)
                                    new_mask_array = np.delete(new_mask_array, peakInd + 1)
                                    print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                    print(f'new_mask_array: {new_mask_array}')
                                    # update wd_segment["RR_masklist"]
                                    wd_segment["RR_masklist"] = new_mask_array
                                    working_data['RR_masklist'][i] = new_mask_array
                                else:
                                    print("Peak before actual peak is green and peak after actual peak is green")
                                    mutable_object['RR_masklist'] = [0, 0]
                                    print(f'mutable_object: {mutable_object["RR_masklist"]}')
                                    new_mask_array = np.insert(wd_segment["RR_masklist"], peakInd - 1, mutable_object["RR_masklist"], axis=0)
                                    # new RR-distances-mask is inserted; the mask entry for the previous old distance needs to be deleted
                                    new_mask_array = np.delete(new_mask_array, peakInd + 1)
                                    print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                                    print(f'new_mask_array: {new_mask_array}')
                                    # update wd_segment["RR_masklist"]
                                    wd_segment["RR_masklist"] = new_mask_array
                                    working_data['RR_masklist'][i] = new_mask_array

                        print(f'peakInd: {peakInd}')
                        plt.draw()
                    else:
                        print("Newly set peak is already set.")
                elif event.button == 3:
                    # right mouse button (delete only self-set points! (leave red-marked points that are correct))
                    if new_xdata_point_b in xdata_b and new_xdata_point_b != xdata_b[len(xdata_b) - 1]:
                        # remove xdata point b
                        print(f'xdata_b: {xdata_b}')
                        # newly deleted peak must be deleted from dynamic peaklist
                        new_xydata_b = np.delete(xydata_b, np.where(xdata_b == new_xdata_point_b), axis=0)
                        wd_segment['peaklist'] = np.delete(wd_segment['peaklist'], np.where(wd_segment['peaklist'] == new_xdata_point_b), axis=0)
                        print(f'wd_segment[peaklist]: {wd_segment["peaklist"]}')
                        print(f'new_xdata_point_b: {new_xdata_point_b}')
                        print(f'new_xydata_b: {new_xydata_b}')
                        print(f'type of new_xydata_b: {type(new_xydata_b)}')
                        # update b
                        b.set_offsets(new_xydata_b)
                        print(f'wd_segment[peaklist]: {wd_segment["peaklist"]}')
                        # update peaklist
                        working_data['peaklist'][i] = wd_segment['peaklist']
                        # calculate new RR-list
                        wd = hp.analysis.calc_rr(wd_segment['peaklist'], sample_rate=200.0)
                        # update RR_list
                        working_data['RR_list'][i] = wd["RR_list"]
                        print(f'working_data[RR_list]: {working_data["RR_list"][i]}')
                        print(f'length peaklist: {len(wd_segment["peaklist"])}')
                        peakI = len(np.where(wd_segment['peaklist'] < new_xdata_point_b)[0])
                        print(f'peakI: {peakI}')
                        ## Peak to delete is the first peak in sequence
                        if peakI == 0:
                            print("First peak in sequence")
                            print(f'length all_peak: {len(wd_segment["peaklist"])}')
                            # delete respective entry from masklist
                            new_mask_array = np.delete(wd_segment["RR_masklist"], peakI, axis=None)
                            print(f'new_mask_array: {new_mask_array}')
                            wd_segment["RR_masklist"] = new_mask_array
                            working_data['RR_masklist'][i] = new_mask_array
                        ## Peak to delete is the last in sequence, needs to be checked!!
                        elif peakI == (len(wd_segment["peaklist"])):
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
                    else:
                        print("Automatically detected peaks cannot be deleted with this function. Within this function only manually set peaks can be deleted.")
                else:
                    print("Button 1 is not assigned to any action within this function.")
            else:
                print("outside")
        ## false green peaks can be set to red and false marked red peaks can be marked green with click
        ## only meant for the peaks that are set by the program
        def onpick(event):
            xy_rejPeaks = c.get_offsets()
            x_rejPeaks = c.get_offsets()[:, 0]
            print(f'xy_rejPeaks: {xy_rejPeaks}')
            print(f'x_rejPeaks: {x_rejPeaks}')

            if event.mouseevent.button == 1 and isinstance(event.artist, Artist):
                artist = event.artist
                artist_edgecolor = np.round(artist.get_edgecolor(), 8)
                # peak is actually green and is set to red
                if artist_edgecolor[0][1] == 0.50196078:
                    sel_point = artist.get_offsets()
                    print(f'sel_point: {sel_point}')
                    sel_peak = (artist.get_offsets()[:, 0]).astype(int)
                    print(f'1st sel_peak: {sel_peak}')
                    # until here:test
                    props = {"color": "red"}
                    Artist.update(artist, props)
                    ## add sel_peak to array xy_rejPeaks and to wd_segment['removed_beats']
                    xy_rejPeaks = np.insert(xy_rejPeaks, 0, sel_point, axis = 0)
                    wd_segment['removed_beats'] = np.insert(wd_segment['removed_beats'], 0, sel_peak, axis=0)
                    working_data['removed_beats'][i] = np.insert(working_data['removed_beats'][i], 0, sel_peak, axis = 0)
                    print(f'working_data["removed_beats"][i]: {working_data["removed_beats"][i]}')
                    print(f'wd_segment["removed_beats"]: {wd_segment["removed_beats"]}')
                    print(f'xy_rejPeaks: {xy_rejPeaks}')
                    ## update c
                    c.set_offsets(xy_rejPeaks)
                    print(f'c.set_offsets(xy_rejPeaks): {c.set_offsets(xy_rejPeaks)}')
                    plt.draw()
                    # get index from newly red marked peak
                    peak_ind = np.where(wd_segment['peaklist'] == sel_peak[0])[0]
                    print(f'peak_ind: {peak_ind}')
                    print(f'length wd[peaklist]: {len(wd_segment["peaklist"])}')
                    # ADAPT MASKLIST: set peak_ind (index) and/or peak_ind-1 in masklist to 1 (1 means that this peak is not considered later on)
                    # peak is the first in sequence
                    if peak_ind == 0:
                        print("I am the first peak in this sequence.")
                        wd_segment["RR_masklist"][peak_ind] = 1
                    # peak is the last in sequence
                    elif peak_ind == len(wd_segment['peaklist'])-1:
                        print("I am the last peak in this sequence.")
                        wd_segment["RR_masklist"][peak_ind-1] = 1
                    # peak is within sequence
                    else:
                        print("Peak is within sequence.")
                        wd_segment["RR_masklist"][peak_ind] = 1
                        wd_segment["RR_masklist"][peak_ind-1] = 1
                    print(f'working_data["RR_list"][i]: {working_data["RR_list"][i]}')
                    print(f'wd_segment[peaklist]: {wd_segment["peaklist"]}')
                    print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                    working_data['RR_masklist'][i] = wd_segment['RR_masklist']
            elif event.mouseevent.button == 3 and isinstance(event.artist, Artist):
                artist = event.artist
                artist_edgecolor = np.round(artist.get_edgecolor(), 8)
                # peak is actually red (and is set to green)
                if artist_edgecolor[0][1] != 0.50196078:
                    selection_point = artist.get_offsets()
                    print(f'selection_point in onpick 3: {selection_point}')
                    selection_peak = (artist.get_offsets()[:, 0]).astype(int)
                    print(f'selection_peak in onpick 3: {selection_peak}')
                    props = {"color": "green"}
                    print(f'xy_rejPeaks before deleting: {xy_rejPeaks}')
                    print(f'wd_segment removed_beats before deleting: {wd_segment["removed_beats"]}')
                    # delete selection_peak from xy_rejPeaks (only necessary, when last rejected peak in sequence is deleted) and from wd_segment['removed_beats']
                    ### TO DO!! 0 stimmte, sofern nicht letzter Autopeak!! Abfrage, ob es sich um den letzten roten Autopeak handelt (ist nur dann der Fall, wenn Array mehr als ein Element enthält)
                    if len(selection_peak) > 1:
                        # selection_peak is last red marked autopeak
                        print("Special case: Last red marked autopeak is selected to be turned into green.")
                        xy_rejPeaks = np.delete(xy_rejPeaks, np.where(x_rejPeaks == selection_peak[len(xy_rejPeaks)-1]), axis=0)
                        wd_segment['removed_beats'] = np.delete(wd_segment['removed_beats'], np.where(wd_segment['removed_beats'] == selection_peak[len(wd_segment['removed_beats'])-1]), axis=0)
                        working_data['removed_beats'][i] = np.delete(working_data['removed_beats'][i], np.where(working_data['removed_beats'][i] == selection_peak[len(working_data['removed_beats'][i])-1]), axis=0)
                        # QUESTION: is there a way to just turn into green the last auto peak and not the whole artist (selection_peak array??); it is just for visualization.. results remain correct
                        Artist.update(artist, props)
                    else:
                        print("No special case: Not the last red marked autopeak is selected to be turned into green.")
                        xy_rejPeaks = np.delete(xy_rejPeaks, np.where(x_rejPeaks == selection_peak[0]), axis=0)
                        wd_segment['removed_beats'] = np.delete(wd_segment['removed_beats'], np.where(wd_segment['removed_beats'] == selection_peak[0]), axis=0)
                        working_data['removed_beats'][i] = np.delete(working_data['removed_beats'][i], np.where(working_data['removed_beats'][i] == selection_peak[0]), axis=0)
                        Artist.update(artist, props)
                    ## when: last red autopeak is set to green
                    #xy_rejPeaks = np.delete(xy_rejPeaks, np.where(x_rejPeaks == sel_peak[len(xy_rejPeaks)-1]), axis=0)
                    #wd_segment['removed_beats'] = np.delete(wd_segment['removed_beats'], np.where(wd_segment['removed_beats'] == sel_peak[len(wd_segment['removed_beats'])-1]), axis=0)
                    #working_data['removed_beats'][i] = np.delete(working_data['removed_beats'][i], np.where(working_data['removed_beats'][i] == sel_peak[len(working_data['removed_beats'][i])-1]), axis=0)
                    print(f'xy_rejPeaks after deleting: {xy_rejPeaks}')
                    print(f'wd_segment removed_beats after deleting: {wd_segment["removed_beats"]}')
                    print(f'working_data[removed_beats][i] removed_beats after deleting: {working_data["removed_beats"][i]}')
                    # update c
                    #c.set_offsets(xy_rejPeaks)
                    # get x_rejPeaks
                    print(f'x_rejPeaks after deleting: {(xy_rejPeaks[:,0]).astype(int)}')
                    # get index from green marked peak
                    #peak_ind = np.where(peaklist == sel_peak[0])[0][0]
                    ### TO DO: if-Abfrage (wenn der letzte rote Autopeak, dann: selection_peak[len(selection_peak)-1]
                    if len(selection_peak) > 1:
                        peak_ind = np.where(wd_segment['peaklist'] == selection_peak[len(selection_peak)-1])[0]
                    else:
                        peak_ind = np.where(wd_segment['peaklist'] == selection_peak[0])[0]
                    print(f'peak_ind: {peak_ind}')
                    print(f'wd[peaklist]: {wd_segment["peaklist"]}')
                    # set index and index-1 in masklist to 0 (0 means that this peak is considered later on)
                    # adapt masklist for changed first peak in peaklist
                    if peak_ind == 0:
                        # when second peak in sequence (subsequent to first peak) is red, masklist at index 0 needs to be set to 1 (not considered later on)
                        #if (wd_segment['peaklist'][peak_ind+1] in xy_rejPeaks[:,0].astype(int)) or (wd_segment['peaklist'][peak_ind+1] in wd_segment['removed_beats']):
                        if (wd_segment['peaklist'][peak_ind + 1] in wd_segment['removed_beats']):
                            print("true")
                            wd_segment["RR_masklist"][peak_ind] = 1 # müsste doch schon so sein oder? Der Schritt ist überflüssig!
                        else:
                            print("false")
                            wd_segment["RR_masklist"][peak_ind] = 0
                    # adapt masklist for changed last peak in peaklist
                    elif peak_ind == len(wd_segment['peaklist'])-1:
                        print("I am the last peak in this plot")
                        # if (wd_segment['peaklist'][peak_ind-1] in xy_rejPeaks[:,0].astype(int)) or (wd_segment['peaklist'][peak_ind-1] in wd_segment['removed_beats']):
                        if (wd_segment['peaklist'][peak_ind - 1] in wd_segment['removed_beats']):
                            wd_segment["RR_masklist"][peak_ind-1] = 1
                        else:
                            wd_segment["RR_masklist"][peak_ind-1] = 0
                    # adapt masklist for a changed peak in between
                    else:
                        #if (wd_segment['peaklist'][peak_ind-1] in xy_rejPeaks[:,0].astype(int)) or (wd_segment['peaklist'][peak_ind-1] in wd_segment['removed_beats']):
                        #    if wd_segment['peaklist'][peak_ind+1] in xy_rejPeaks[:,0].astype(int) or (wd_segment['peaklist'][peak_ind+1] in wd_segment['removed_beats']):
                        if (wd_segment['peaklist'][peak_ind - 1] in wd_segment['removed_beats']):
                            if wd_segment['peaklist'][peak_ind + 1] in wd_segment['removed_beats']:
                                print("I am in 1 and 1")
                                wd_segment["RR_masklist"][peak_ind-1] = 1
                                wd_segment["RR_masklist"][peak_ind] = 1
                            else:
                                print("I am in 1 and 0")
                                wd_segment["RR_masklist"][peak_ind-1] = 1
                                wd_segment["RR_masklist"][peak_ind] = 0
                        # elif (wd_segment['peaklist'][peak_ind-1] not in xy_rejPeaks[:,0].astype(int)) and (wd_segment['peaklist'][peak_ind-1] not in wd_segment['removed_beats']):
                        elif (wd_segment['peaklist'][peak_ind - 1] not in wd_segment['removed_beats']):
                            # if (wd_segment['peaklist'][peak_ind+1] in xy_rejPeaks[:,0].astype(int)) or (wd_segment['peaklist'][peak_ind+1] in wd_segment['removed_beats']):
                            if (wd_segment['peaklist'][peak_ind + 1] in wd_segment['removed_beats']):
                                print("I am in 0 and 1")
                                wd_segment["RR_masklist"][peak_ind-1] = 0
                                wd_segment["RR_masklist"][peak_ind] = 1
                            else:
                                print("I am in 0 and 0")
                                wd_segment["RR_masklist"][peak_ind - 1] = 0
                                wd_segment["RR_masklist"][peak_ind] = 0

                    print(f'working_data["peaklist"][i]: {wd_segment["peaklist"]}')
                    print(f'working_data["RR_list"][i]: {working_data["RR_list"][i]}')
                    print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                    print(f'wd_segment[RR_masklist][i] before actualisation: {working_data["RR_masklist"][i]}')
                    #Artist.update(artist, props)
                    working_data['RR_masklist'][i] = wd_segment['RR_masklist']
                    print(f'wd_segment[RR_masklist][i] after actualisation: {working_data["RR_masklist"][i]}')
                    c.set_offsets(xy_rejPeaks)
                    plt.draw()
            elif event.mouseevent.button == 2 and isinstance(event.artist, Artist):
                thisPeak = event.artist
                thisPeak.remove()
                selPeak = (thisPeak.get_offsets()[:, 0]).astype(int)
                print(f'sel_peak: {selPeak}')
                print(f'sel_peak: {selPeak[0]}')
                # get index from selected peak
                peak_ind = np.where(wd_segment['peaklist'] == selPeak[0])[0]
                print(f'peak_ind: {peak_ind}')
                # get predecessor and successor from sel_peak (only if sel_peak is inbetween two peaks)
                print(f'length of wd_segment: {len(wd_segment["peaklist"])-1}')
                if not (peak_ind == [0] or peak_ind == [len(wd_segment['peaklist'])-1]):
                    print("sel_peak is inbetween two other peaks")
                    predecessor = wd_segment['peaklist'][peak_ind-1]
                    print(f'predecessor: {predecessor}')
                    successor = wd_segment['peaklist'][peak_ind+1]
                    print(f'successor: {successor}')
                else:
                    print("Sel_peak is the first or the last in sequence.")
                # delete peak from respective dicts (in xy_rejPeaks only the last rejected peak of the sequence is listed)
                # delete masklist entry
                print(f'wd_segment[RR_masklist] before deleting: {wd_segment["RR_masklist"]}')
                if selPeak in wd_segment['peaklist'] and peak_ind == 0:
                    wd_segment['RR_masklist'] = np.delete(wd_segment['RR_masklist'], [peak_ind])
                    working_data['RR_masklist'][i] = np.delete(working_data['RR_masklist'][i], [peak_ind])
                elif selPeak in wd_segment['peaklist'] and peak_ind != 0:
                    wd_segment['RR_masklist'] = np.delete(wd_segment['RR_masklist'], [peak_ind-1])
                    working_data['RR_masklist'][i] = np.delete(working_data['RR_masklist'][i], [peak_ind-1])
                    if peak_ind == [len(wd_segment['peaklist'])-1]:
                        print("Peak is the last in sequence.")
                    else:
                        # wenn Vorgänger und Nachfolger vom sel_peak beide grün (d.h. nicht in removed_beats gelistet), dann setze wd_segment['RR_masklist'][peak_ind-1] = 0
                        if (predecessor not in wd_segment['removed_beats'] and successor not in wd_segment['removed_beats']):
                            print("true")
                            wd_segment['RR_masklist'][peak_ind - 1] = 0
                            working_data['RR_masklist'][i][peak_ind - 1] = 0
                        else:
                            print("predecessor or successor is red")
                elif selPeak in wd_segment['peaklist'] and peak_ind == 0:
                    wd_segment['RR_masklist'] = np.delete(wd_segment['RR_masklist'], [peak_ind])
                    working_data['RR_masklist'][i] = np.delete(working_data['RR_masklist'][i], [peak_ind])
                    print("Peak is the first in sequence.")
                else:
                    print("masklist is already adapted")
                print(f'wd_segment[RR_masklist] after deleting: {wd_segment["RR_masklist"]}')
                print(f'working_data[RR_masklist][i] after deleting: {working_data["RR_masklist"][i]}')
                xy_rejPeaks = np.delete(xy_rejPeaks, np.where(x_rejPeaks == selPeak), axis=0)
                # if-Abfrage: wenn selPeak in wd_segment[removed_beats] or in wd_segment[peaklist] -> delete
                if selPeak in wd_segment['removed_beats'] and selPeak in wd_segment['peaklist']:
                    wd_segment['removed_beats'] = np.delete(wd_segment['removed_beats'], np.where(wd_segment['removed_beats'] == selPeak), axis=0)
                    working_data['removed_beats'][i] = np.delete(working_data['removed_beats'][i], np.where(working_data['removed_beats'][i] == selPeak), axis=0)
                    wd_segment['peaklist'] = np.delete(wd_segment['peaklist'], np.where(wd_segment['peaklist'] == selPeak), axis=0)
                    working_data['peaklist'][i] = np.delete(working_data['peaklist'][i], np.where(working_data['peaklist'][i] == selPeak), axis=0)
                elif selPeak in wd_segment['peaklist'] and selPeak not in wd_segment['removed_beats']:
                    wd_segment['peaklist'] = np.delete(wd_segment['peaklist'], np.where(wd_segment['peaklist'] == selPeak), axis=0)
                    working_data['peaklist'][i] = np.delete(working_data['peaklist'][i], np.where(working_data['peaklist'][i] == selPeak), axis=0)
                else:
                    print("Peaklist and removed beat list are already correct")

                ## adapt working_data[RR_list][i]
                ## update RR_list
                wd = hp.analysis.calc_rr(wd_segment['peaklist'], sample_rate=200.0)
                working_data['RR_list'][i] = wd["RR_list"]

                print(f'wd_segment[peaklist]: {wd_segment["peaklist"]}')
                print(f'working_data[peaklist][i]: {working_data["peaklist"][i]}')
                print(f'xy_rejPeaks: {xy_rejPeaks}')
                print(f'wd_segment[removed_beats]: {wd_segment["removed_beats"]}')
                print(f'working_data[removed_beats][i]: {working_data["removed_beats"][i]}')
                print(f'wd_segment[RR_masklist]: {wd_segment["RR_masklist"]}')
                print(f'working_data[RR_list][i]: {working_data["RR_list"][i]}')
                #Artist.update()
                # update c
                c.set_offsets(xy_rejPeaks)
                print(f'c.set_offsets(xy_rejPeaks): {c.set_offsets(xy_rejPeaks)}')
                plt.draw()
            else:
                return

        cid = fig1.canvas.mpl_connect('button_press_event', add_or_remove_point)
        #fig1.canvas.mpl_disconnect(cid)
        cid2 = fig1.canvas.mpl_connect('pick_event', onpick)
        #fig1.canvas.mpl_disconnect(cid)
        #fig1.canvas.mpl_disconnect(cid2)

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
            print('I am in def add_rem')
            #global cid
            fig1.canvas.mpl_disconnect(cid2)
            fig1.canvas.mpl_connect('button_press_event', add_or_remove_point)
            #cid = fig1.canvas.mpl_connect('button_press_event', add_or_remove_point)

        def change_red_green(val):
            fig1.canvas.mpl_disconnect(cid)
            fig1.canvas.mpl_connect('pick_event', onpick)
            #cid2 = fig1.canvas.mpl_connect('pick_event', onpick)

        save_button.on_clicked(savefct)
        discard_button.on_clicked(discardfct)
        add_rem_button.on_clicked(add_rem)
        red_green_button.on_clicked(change_red_green)

        plt.show()
        filenum += 1
        print(f'wd_segment at end: {wd_segment["RR_masklist"]}')
        print(f'working_data at end: {working_data["RR_masklist"][i]}')


    return choosen_sequence

# subject (needs to be changed manually)
subject = 'sub016_'
#subject = 'sub021_'
# episode (needs to be changed manually)
episode = '3rd_Episode'

# storage path: generated plots and calculated data should be stored here; for real data analysis: delete last directory "tests"
storage_path = os.path.join("/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/plots/", subject, episode)
print(f'storage_path: {storage_path}')
storage_path_data = os.path.join("/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/", subject, episode)
print(f'storage_path: {storage_path_data}')

# check, whether plot path exists; if not -> create directory
isExist = os.path.exists(storage_path)
if not isExist:
    os.makedirs(storage_path)
    print("New plot directory is created.")
else:
    print("Storage path plots already exists.")

# check, whether data path exists; if not -> create directory
isExist = os.path.exists(storage_path_data)
if not isExist:
    os.makedirs(storage_path_data)
    print("New data directory is created.")
else:
    print("Storage path data already exists.")

# sample_rate in Hz
sample_rate = 200

# get raw data (header and data); needs to be changed manually!!
hrdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi016_0_250.csv', column_name='uV')
timerdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi016_0_250.csv', column_name='dt')

#hrdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi016_0_250.csv', column_name='uV')
#timerdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi016_0_250.csv', column_name='dt')

# bandpass filter given by heartpy
bp_filtered = hp.filter_signal(hrdata_3rd, cutoff=[7,21], sample_rate=sample_rate, order=3, filtertype='bandpass')

# create working_data dict, in which we can integrate merged arrays later on (in order to enable poincare plot)
# here in process-function: calc_poincare for complete data set
wd_whole_epi, meas_whole_epi = hp.process(bp_filtered, sample_rate=sample_rate)
#print(f'working_data wd_whole_epi: {wd_whole_epi}')
#print(f'Peaklist whole epi at beginning: {wd_whole_epi["peaklist"]}')
#print(f'RR_masklist whole connected epi at beginning: {wd_whole_epi["RR_masklist"]}')
#print(f'RR_list whole connected epi at beginning: {wd_whole_epi["RR_list"]}')
#print(f'RR_list_cor whole connected epi at beginning: {wd_whole_epi["RR_list_cor"]}')

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
# Array to store removed_beats
stitched_removed_beats = []

#choosen_seq = sequence_plotter(work_data, meas, path='/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/plots/', subject=subject)
choosen_seq = sequence_plotter(work_data, meas, path=storage_path, subject=subject)
print(f'meas1: {meas}')
print(f'choosen_seq: {choosen_seq}')
print(f'work_data[peaklist][0]: {work_data["peaklist"][0]}')
print(f'work_data[peaklist][1]: {work_data["peaklist"][1]}')
print(f'work_data[RR_masklist][0]: {work_data["RR_masklist"][0]}')
print(f'work_data[RR_list][0]: {work_data["RR_list"][0]}')
print(f'work_data[removed_beats][0]: {work_data["removed_beats"][0]}')

# sequences modified and selected by the user are stitched together
# peaklists and removed_beats need to be recalculated (because indexing starts anew with each sequence)
nr_samplepoints_per_seq = seq_width * sample_rate
print(f'nr_samplepoints_per_seq: {nr_samplepoints_per_seq}')
print(f'length choosen_seq: {len(choosen_seq)}')

for j in range(0, len(choosen_seq)):
    #print(f'j: {j}')
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
#print(f'length stitched_peaklists: {len(stitched_peaklists)}')
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
    # rr_diff_trans is the time in ms between last peak of previous sequence and first peak of subsequent sequence
    rr_diff_trans = ((stitched_peaklists[i+1][0] - stitched_peaklists[i][len(stitched_peaklists[i]) - 1]) * nr_samplepoints_per_seq)/sample_rate
    # We consider transition differences, but it is a bit redundant. It would be sufficient to set rr_diff_trans to 0 in masklist.
    # we need to check whether respective peaks are listed in removed_beats
    # Later on the entries being too small or too big were deleted
    # add rr_diff_trans to stitched_RR_lists
    # actually we do not consider transition differences
    stitched_RR_lists[i] = np.append(stitched_RR_lists[i], rr_diff_trans)
    stitched_RR_masklists[i] = np.append(stitched_RR_masklists[i], 1)

    # if rr_diff_trans < 300 or rr_diff_trans > 1200:
    #     stitched_RR_masklists[i] = np.append(stitched_RR_masklists[i], 1)
    # elif stitched_peaklists[i+1][0] in stitched_removed_beats or stitched_peaklists[i][len(stitched_peaklists[i]) - 1] in stitched_removed_beats:
    #     stitched_RR_masklists[i] = np.append(stitched_RR_masklists[i], 1)
    # else:
    #     stitched_RR_masklists[i] = np.append(stitched_RR_masklists[i], 0)

print(f'last array entry stitched_peaklists[0]: {stitched_peaklists[0][len(stitched_peaklists[0])-1]}')
print(f'first array entry stitched_peaklists[1]: {stitched_peaklists[1][0]}')
#rr_diff_trans = ((stitched_peaklists[1][0] - stitched_peaklists[0][len(stitched_peaklists[0])-1])*1000)/200
print(f'stitched_RR_lists: {stitched_RR_lists}')
print(f'length stitched_peaklists: {len(stitched_peaklists)}')
print(f'length single entry in stitched_RR_lists: {len(stitched_RR_lists[0])}')
print(f'length single entry in stitched_RR_masklists: {len(stitched_RR_masklists[0])}')
print(f'stitched_RR_masklists: {stitched_RR_masklists}')

# merges stitched lists to one big list
merged_hr = list(itertools.chain(*stitched_hr_data))
merged_peaklists = list(itertools.chain(*stitched_peaklists))
print(f'length merged_peaklists: {len(merged_peaklists)}')
print(f'merged_peaklists: {merged_peaklists}')
merged_RR_masklist = list(itertools.chain(*stitched_RR_masklists))
print(f'merged_RR_masklist: {merged_RR_masklist}')
merged_RR_list = list(itertools.chain(*stitched_RR_lists))
print(f'merged_RR_list: {merged_RR_list}')
merged_removed_beats = list(itertools.chain(*stitched_removed_beats))
print(f'type of merged_RR_list: {type(merged_RR_list)}')
print(f'length merged_RR_list before deleting: {len(merged_RR_list)}')
print(f'length merged_RR_masklist before deleting: {len(merged_RR_masklist)}')
#print(f'length merged_removed_beats: {len(merged_removed_beats)}')

### delete RR-distances that are too low and too high (and its respective entry in RR_masklists)
## NEEDS TO BE CHECKED!! seems to be correct
indices_to_be_deleted = []
print(f'length merged_RR_list: {len(merged_RR_list)}')
for i in range(len(merged_RR_list)-1):
    if merged_RR_list[i] < 300 or merged_RR_list[i] > 1200:
        print(f'RR distance of {merged_RR_list[i]} will be neglected, because it is too small or too big.')
        indices_to_be_deleted.append(i)
    else:
        pass

print(f'indices_to_be_deleted: {indices_to_be_deleted}')
print(f'length of indices_to_be_deleted: {len(indices_to_be_deleted)}')

indices_to_be_deleted = sorted(indices_to_be_deleted, reverse=True)
# delete entries of too low or too high RR-distances ( I can also convert list to an array: np.array(indices_to_be_deleted))
# no longer has to match peaklist
# after this operation: there are still entries in RR_list that should not be considered (have corresponding 1 in masklist)(valid distance, but neglected for other reasons)
# adressed later on
for indx in indices_to_be_deleted:
    if indx < len(merged_RR_list):
        merged_RR_list.pop(indx)
        merged_RR_masklist.pop(indx)

print(f'length merged_RR_list after deleting: {len(merged_RR_list)}')
print(f'length merged_RR_masklist after deleting: {len(merged_RR_masklist)}')

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
#print(f'wd_whole_epi[hr]: {wd_whole_epi["hr"]}')
#print(f'ybeat1: {wd_whole_epi["ybeat"]}')

### Save merged lists into text files and save in data directory
# open file
with open(os.path.join(storage_path_data, 'merged_hr.txt'), 'w+') as f:
    for items in merged_hr:
            f.write('%s\n' %items)
    print("merged_hr successfully written")
# close file
f.close()
# save as csv
np.savetxt(os.path.join(storage_path_data, 'merged_hr.csv'), merged_hr, delimiter=',')

with open(os.path.join(storage_path_data, 'merged_peaklists.txt'), 'w+') as f:
    for items in merged_peaklists:
            f.write('%s\n' %items)
    print("merged_peaklists successfully written")
f.close()
np.savetxt(os.path.join(storage_path_data, 'merged_peaklists.csv'), merged_peaklists, delimiter=',')

with open(os.path.join(storage_path_data, 'merged_RR_masklist.txt'), 'w+') as f:
    for items in merged_RR_masklist:
            f.write('%s\n' %items)
    print("merged_RR_masklist successfully written")
f.close()
np.savetxt(os.path.join(storage_path_data, 'merged_RR_masklist.csv'), merged_RR_masklist, delimiter=',')

with open(os.path.join(storage_path_data, 'merged_RR_list.txt'), 'w+') as f:
    for items in merged_RR_list:
            f.write('%s\n' %items)
    print("merged_RR_list successfully written")
f.close()
np.savetxt(os.path.join(storage_path_data, 'merged_RR_list.csv'), merged_RR_list, delimiter=',')

with open(os.path.join(storage_path_data, 'merged_removed_beats.txt'), 'w+') as f:
    for items in merged_removed_beats:
            f.write('%s\n' %items)
    print("merged_removed_beats successfully written")
f.close()
np.savetxt(os.path.join(storage_path_data, 'merged_removed_beats.csv'), merged_removed_beats, delimiter=',')

## recalculate wd parameters that are used for calculation of measures
# Calculation of ybeat might be wrong (in peaklist also the rejected ones are listed!!!)
print(f'length merged_hr: {len(merged_hr)}')
print(f'merged_peaklists: {merged_peaklists}')
wd_whole_epi['ybeat'] = [merged_hr[x] for x in merged_peaklists]
#print(f'ybeat2: {wd_whole_epi["ybeat"]}')
#print(f'length ybeat: {len(wd_whole_epi["ybeat"])}')
#print(f'wd_whole_epi[RR_diff_cor]: {wd_whole_epi["RR_diff_cor"]}')
rr_list_cor = np.array([merged_RR_list[i] for i in range (len(merged_RR_masklist)) if merged_RR_masklist[i] == 0])
#wd_whole_epi['RR_diff_cor'] = rr_list_cor
wd_whole_epi['RR_list_cor'] = rr_list_cor
#print(f'wd_whole_epi[RR_diff_cor]: {wd_whole_epi["RR_diff_cor"]}')
print(f'wd_whole_epi[RR_list_cor]: {wd_whole_epi["RR_list_cor"]}')
print(f'rr_list_cor: {rr_list_cor}')
print(f'length of rr_list_cor: {len(rr_list_cor)}')
wd_whole_epi['removed_beats_y'] = [merged_hr[x] for x in merged_removed_beats]
rr_diff = np.abs(np.diff(rr_list_cor))
print(f'rr_diff: {rr_diff}')
rr_sqdiff = np.power(rr_diff, 2)
print(f'rr_sqdiff: {rr_sqdiff}')

# save RR_list_cor (here: RR distances that are considered in Poincare Plot)
with open(os.path.join(storage_path_data, 'RR_list_cor.txt'), 'w+') as f:
    for items in rr_list_cor:
            f.write('%s\n' %items)
    print("RR_list_cor successfully written")
f.close()
np.savetxt(os.path.join(storage_path_data, 'RR_list_cor.csv'), rr_list_cor, delimiter=',')

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
#print(f'wd_whole_epi["rolling_mean"]: {wd_whole_epi["rolling_mean"]}')

# calc rolling_mean
rol_mean = hp.datautils.rolling_mean(merged_hr, 0.75, sample_rate)
wd_whole_epi['rolling_mean'] = rol_mean

# plot merged dataset to check whether algorithm worked correctly
hp.plotter(wd_whole_epi, meas_whole_epi)
plt.show()

# calc_poincare just needs working_data for calculation, but throws an error when the other parameter are missing; measures is only needed for writing in the
# recalculated SD1, SD2 ... parameter
# func works with rr_list and rr_masklist
#meas_poincare = hp.analysis.calc_poincare(merged_RR_list, rr_mask = merged_RR_masklist, measures=meas_whole_epi, working_data=wd_whole_epi)
meas_poincare = hp.analysis.calculation_poincare(measures=meas_whole_epi, working_data=wd_whole_epi)
# save meas_poincare
with open(os.path.join(storage_path_data, 'measures_poincare.csv'), 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in meas_poincare.items():
       writer.writerow([key, value])
# save wd_whole_epi
with open(os.path.join(storage_path_data, 'wd_whole_episode.csv'), 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in wd_whole_epi.items():
       writer.writerow([key, value])

## TO READ IT BACK
# with open('dict.csv') as csv_file:
#     reader = csv.reader(csv_file)
#     mydict = dict(reader)

print(f'meas_poincare: {meas_poincare}')
print(f'meas_whole_epi1: {meas_whole_epi}')

## Poincare Plot (kommt bei beiden das gleiche raus, weil wir innerhalb von calc_poincare in measures schreiben und das dann in beiden measures dicts drin)
# bei beiden kommt das gleiche raus, weil nur die
#hp.plot_poincare(wd_whole_epi, meas_whole_epi, figsize = (20,5), title='Poincare Plot 1')
#plt.show()
hp.plot_poincare(wd_whole_epi, meas_poincare, figsize = (20,5), title='Poincare')
#plt.show()
# Plot "Lorentzplot" is saved
plt.savefig(os.path.join(storage_path, "Lorenzplot.png"))
## Poincare.png is not saved
#plt.savefig('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/plots/' + str(subject) + '/Poincare.png')
plt.show()