clear all, fclose all
fid = fopen('MDC_ECG_LEAD_I.csv', 'r');
header = fscanf(fid, '%s, %s', [2 1])
A = fscanf(fid, '%f, %f', [2 100000])
B = A'
fclose(fid);
x = B(:,1);
y = B(:,2);
plot(x,y);
set (gca, 'linewidth', 1, 'fontsize', 36)
xlabel('s');
ylabel('uV');
grid on
