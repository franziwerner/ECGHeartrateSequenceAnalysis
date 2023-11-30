import heartpy as hp
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import os

timetable = [0]*52
print(type(timetable))
print(timetable)

# load timestamps table
with open('/Users/franziskawerner/Documents/ISN/DFGProjekt/EKG/Timestamps_Eyetracking.csv') as csv_file:
#with open('/Users/franziskawerner/Documents/ISN/DFGProjekt/EKG/Timestamps_komplett_FF.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(row)
            print(f'Column names are {", ".join(row)}')
            timetable[line_count] = row
            line_count += 1
        else:
            print(row)
            print(f'\t{row[0]} started MAS {row[14]} minutes after start of video tape {row[3]} and the episode ended {row[18]} minutes after start.')
            timetable[line_count] = row
            line_count += 1
    print(f'Processed {line_count} lines.')

print(timetable)
print(timetable[2][0][0])
print(len(timetable))

# loop through subjects
for n in range(2, len(timetable)):
    # load EKG start times
    print(f'n: {n}')
    subject = timetable[n][0]
    print(f'ID: {subject}')
    print(type(subject))
    print(type(int(subject)))
    print('/Users/franziskawerner/Documents/ISN/DFGProjekt/Probandendaten/0' + str(subject) + '/EKG_Qardio/hf-0' + str(subject) + '.csv')

    #with open('/Users/franziskawerner/Documents/ISN/DFGProjekt/Probandendaten/021/EKG_Qardio/hf-021.csv') as csv_file:
    with open('/Users/franziskawerner/Documents/ISN/DFGProjekt/Probandendaten/0' + str(subject) + '/EKG_Qardio/hf-0' + str(subject) + '.csv') as csv_file:
        csvReader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csvReader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            elif line_count == 1:
                print(f'ECG Recording started at \t{row[0]}')
                start_ecg_unix = int(f'\t{row[0]}')
                line_count += 1
            else:
                line_count += 1
        print(f'Processed {line_count} lines.')
        csv_file.close()

    # Unix time conversion
    timestamp_ecg = datetime.utcfromtimestamp(start_ecg_unix/1000).strftime('%Y-%m-%d %H:%M:%S')
    print(f'Start ECG recording (converted from unix): {timestamp_ecg}')

    start_ecg = datetime.utcfromtimestamp(start_ecg_unix/1000).strftime('%H:%M:%S')
    print(f'Start ECG (only time): {start_ecg}')

    # Calculate difference between eyetracking start and ecg start
    # timetable[0] corresponds to first line in table
    print(f'timetable first row: {timetable[0]}')

    # subject x, minutes passed after start recording before MAS started
    thirdEpi_start_eye = timetable[n][14]
    print(f'Start of third episode (minutes passed after eyetracking start): {thirdEpi_start_eye}')
    end_thirdEpi_eye = timetable[n][18]
    print(f'End of third episode (minutes passed after eyetracking start): {end_thirdEpi_eye}')
    start_eye = timetable[n][3]
    print(f'Start Eyetracking Recording: {start_eye}')

    # Conversion of string in datetime object (btw only time object)
    time_format = '%H:%M:%S'
    start_eye_obj = datetime.strptime(start_eye, time_format)
    start_ecg_obj = datetime.strptime(start_ecg, time_format)
    thirdEpi_start_eye_obj = datetime.strptime(thirdEpi_start_eye, time_format)
    end_thirdEpi_eye_obj = datetime.strptime(end_thirdEpi_eye, time_format)

    # calculate time difference between eyetracking start and ecg start
    dt_start = start_eye_obj - start_ecg_obj
    #dt_start = start_ecg_obj - start_eye_obj
    print(f'Time difference between ECG and Eyetracking Start: {dt_start}')
    #print(dt_start.days)

    if dt_start.days:
        print(f'Eyetracking was started earlier')
        dt_start = start_ecg_obj - start_eye_obj
        thirdEpi_start_ecg = thirdEpi_start_eye_obj - dt_start
        thirdEpi_end_ecg = end_thirdEpi_eye_obj - dt_start
        print(f'Delta Start: {dt_start}')
        print(f'ECG start third episode (minutes passed since recording start): {thirdEpi_start_ecg.time()}')
        print(f'ECG end third episode (minutes passed since recording start): {thirdEpi_end_ecg.time()}')
    else:
        print(f'ECG started before Eyetracking')
        thirdEpi_start_ecg = thirdEpi_start_eye_obj + dt_start
        thirdEpi_end_ecg = end_thirdEpi_eye_obj + dt_start
        print(f'ECG start third episode (minutes passed since recording start): {thirdEpi_start_ecg.time()}')
        print(f'ECG end third episode (minutes passed since recording start): {thirdEpi_end_ecg.time()}')

    # conversion minutes in seconds
    thirdEpi_start_ecg_seconds = thirdEpi_start_ecg.minute * 60 + thirdEpi_start_ecg.second
    thirdEpi_end_ecg_seconds = thirdEpi_end_ecg.minute * 60 + thirdEpi_end_ecg.second
    print(f'ECG start in seconds: {thirdEpi_start_ecg_seconds}')
    print(f'ECG end in seconds: {thirdEpi_end_ecg_seconds}')

    # conversion to sample values (0.005 due to sampling frequency of 200 Hz --> every 0.005 seconds one sample)
    start_smpls = thirdEpi_start_ecg_seconds/0.005
    end_smpls = thirdEpi_end_ecg_seconds/0.005

    # conversion samples to int
    start = int(start_smpls)
    end = int(end_smpls)
    print(f'Start in samples: {start}')
    print(f'End in samples: {end}')

    ## run shell commands
    # first: change working directory to actual subject
    os.chdir("/Users/franziskawerner/Documents/ISN/DFGProjekt/EKG/csvEKG/vp0" + str(subject) + "/")
    #os.chdir("/Users/franziskawerner/Documents/ISN/DFGProjekt/EKG/csvEKG/vp021/")
    os.system("ls")
    # creates new ....csv-file and copies head from MDC_ECG_LEAD_II.csv into it
    os.system("head -n 1 MDC_ECG_LEAD_II.csv > thirdEpi0" + str(subject) + ".csv")
    #os.system("head -n 1 MDC_ECG_LEAD_II.csv > thirdEpi021test4.csv")
    # copies sequence between start and end to the above newly created file
    os.system(f"sed -n '{start},{end} p' MDC_ECG_LEAD_II.csv >> thirdEpi0" + str(subject) + ".csv")
    #os.system(f"sed -n '{start},{end} p' MDC_ECG_LEAD_II.csv >> thirdEpi021test4.csv")

    # copy created csv-file to working directory of PyCharm
    os.system("cp ~/Documents/ISN/DFGProjekt/EKG/csvEKG/vp0" + str(subject) + "/thirdEpi0" + str(subject) + ".csv ~/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi0" + str(subject) + ".csv")

    # sample_rate in Hz
    sample_rate = 200

    # get raw data (header and data)
    hrdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi0' + str(subject) + '.csv', column_name='uV')
    timerdata_3rd = hp.get_data('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/data/thirdEpi0' + str(subject) + '.csv', column_name='dt')

    ## bandpass filter given by heartpy
    bp_filtered = hp.filter_signal(hrdata_3rd, cutoff = [7,35], sample_rate = sample_rate, order=3, filtertype='bandpass')
    wd_bp_filtered, m_bp_filtered = hp.process(bp_filtered, sample_rate = sample_rate)
    plot_bp = hp.plotter(wd_bp_filtered, m_bp_filtered, figsize=(20,5), title = 'bandpass-filtered with heartpy')
    #plt.show()
    plt.savefig('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/pics/thirdEpi0' + str(subject) + '.png')
    #plt.show()

    # Poincare Plot
    hp.plot_poincare(wd_bp_filtered, m_bp_filtered, figsize = (20,5), title='Poincare Plot')
    plt.savefig('/Users/franziskawerner/PycharmProjects/heartrate_analysis_python-master/heartpy/pics/poinplot_thirdEpi0' + str(subject) + '.png')
    #plt.show()


#command = F"sed -n '$start,$end p' MDC_ECG_LEAD_II.csv >> thirdEpi021test3.csv"
## that works, but static variables
#os.system(f"sed -n '289000,343000 p' MDC_ECG_LEAD_II.csv >> thirdEpi021test2.csv")
## dynamic variables
#os.system(f"sed -n '{start},{end} p' MDC_ECG_LEAD_II.csv >> thirdEpi021test3.csv")

