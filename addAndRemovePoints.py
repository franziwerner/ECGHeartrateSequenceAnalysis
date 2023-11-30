import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(16,4))
a_input = np.sin(range(100))*np.random.normal(20,10,100)
b_input = [ 5, 15, 25, 30, 40, 50, 75, 85]

a = plt.plot(range(len(a_input)),a_input,color='red')[0]
b = plt.scatter(b_input,a_input[b_input],color='grey',s=50,picker=5)

def add_or_remove_point(event):
    global a
    xydata_a = np.stack(a.get_data(),axis=1)
    xdata_a = a.get_xdata()
    ydata_a = a.get_ydata()
    global b
    xydata_b = b.get_offsets()
    xdata_b = b.get_offsets()[:,0]
    print(f'xdata_b: {xdata_b}')
    ydata_b = b.get_offsets()[:,1]

    #click x-value
    xdata_click = event.xdata
    #index of nearest x-value in a
    xdata_nearest_index_a = (np.abs(xdata_a-xdata_click)).argmin()
    #new scatter point x-value
    new_xdata_point_b = xdata_a[xdata_nearest_index_a]
    #new scatter point [x-value, y-value]
    new_xydata_point_b = xydata_a[new_xdata_point_b,:]

    if event.button == 1:
        if new_xdata_point_b not in xdata_b:
            #insert new scatter point into b
            new_xydata_b = np.insert(xydata_b,0,new_xydata_point_b,axis=0)
            #sort b based on x-axis values
            new_xydata_b = new_xydata_b[np.argsort(new_xydata_b[:,0])]
            print(f'new_xydata_b: {new_xydata_b}')
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

fig.canvas.mpl_connect('button_press_event',add_or_remove_point)
plt.show()

#### AUSGESCHLOSSENES

#scatterplt = plt.scatter()
#pt = []
#pt_exact = []

# def handleEvent(event):
#     global pt
#     global pt_exact
#     global line
#     print("Button-Press-Event is called")
#     if event.button == 3:
#         if [round(event.xdata,0),round(event.ydata,1)] not in pt:
#             print(event.xdata, event.ydata)
#             ##pt_exact.append([event.xdata, event.ydata])
#             pt.append([round(event.xdata,0), round(event.ydata,1)])
#             #line, = plt.plot(round(event.xdata,0), round(event.ydata,1), 'go') ## exact values were plotted and this leads to problems, when I (as soon as I delete values) replot (new) line
#             for p in pt:
#                 line, = plt.plot(p[0],p[1], 'go')
#             plt.draw()
#             #line.remove()
#         elif [round(event.xdata,0),round(event.ydata,1)] in pt:
#             line.remove()
#             print("Point was placed manually before.")
#             pt.remove([round(event.xdata, 0), round(event.ydata, 1)])
#             print(f'pt.remove: {pt}')
#             for p in pt:
#                 line, = plt.plot(p[0], p[1], 'go')
#             plt.draw()

### THE OLD HANDLEEVENT FUNCTION

# def handleEvent(event):
#     global pt
#     print("Button-Press-Event is called")
#     if event.button == 3:
#         print(event.xdata, event.ydata)
#         print(round(event.xdata,1))
#         print(type(pt))
#         #pt = [event.xdata, event.ydata]
#         pt.append([round(event.xdata,1), round(event.ydata,1)])
#         print(f'pt: {pt}')
#         plt.plot(event.xdata, event.ydata, 'go')
#     elif event.button == 1 and [round(event.xdata,1),round(event.ydata,1)] in pt:
#         print("Point was placed manually before.")
#         pt.remove([round(event.xdata,1),round(event.ydata,1)])
#         print(f'pt.remove: {pt}')
#         for i in range(0,len(pt)-1):
#         #for p in pt:
#             #print(f'p in pt: {p}')
#             plt.plot(pt[i][i], pt[i][i+1])
#             #plt.plot(p[0], p[0])
#     plt.draw()

## from sel_ECGseq.py onclick routine in order to access rejected peaks and be able to actualize

## insert new scatter point into removed peaks
                    #new_xy_rejPeaks = np.insert(xy_rejPeaks, 0, artist.get_offsets(), axis=0)
                    #print(f'new_xy_rejPeaks unsorted: {new_xy_rejPeaks}')
                    ## sort b based on x-axis values (here: last peak from sequence is still listed)
                    #new_xy_rejPeaks = new_xy_rejPeaks[np.argsort(new_xy_rejPeaks[:, 0])]
                    #print(f'new_xy_rejPeaks sorted: {new_xy_rejPeaks}')
                    ## update b
                    #c.set_offsets(new_xy_rejPeaks)
                    #removedpeaks_new = np.concatenate((removedpeaks, sel_peak), axis = None)
                    #removedpeaks_new = np.append(removedpeaks_new, sel_peak)
                    #removedpeaks_new = np.insert(removedpeaks, 0, sel_peak, axis=0)
                    #wd_segment["removed_beats"] = removedpeaks_new # just the last settet red peak is listed
                    #print(f'wd_segment["removed_beats"]: {wd_segment["removed_beats"]}')