clear;
clc;
close all;

data = readtable("telemetrylog.txt");

% figure();
% stackedplot(data)

time = table2array(data(37075:37740,"Var17"));
time = (time - time(1)) .* 1e-6;
thrust = table2array(data(37075:37740,"Var7"));

thrustCurve = figure();
plot(time,thrust)
xlabel('Time (s)')
ylabel('Thrust (N)')
nicePlot(thrustCurve)

totalImpulse = trapz(time,thrust)

A = [time'; thrust'];

fileID = fopen('thanos_thrust_curve_hotfire.txt','w');
fprintf(fileID,'%6s %12s\n','time (s)','thrust (N)');
fprintf(fileID,'%6.2f %12.2f\n', A);
fclose(fileID);
