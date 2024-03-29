% run this to set variables for rocket sizing simulink thingy - im pretty
% sure it should work but there might be some problems
% this is very janky and should only be used as a guideline - i don;t
% actually know how much i trust this - usmaan 

%% run this before the simulation to set initial conditions and constants

% Environment Parameters
g = 9.81;           % assume g is constant (we're not going that high)
p0 = 101325;        % sea level pressure (Pa)
R = 287;            % think its called the gas constant right !? it's late and i don't remember

% Engine Parameters
OF = 3.5;                       % OF ratio
m0_ox = 14;                      % oxidizer mass of rocket, kg
m0_fuel = m0_ox/OF;             % fuel mass of rocket, kg
m_propellant = m0_fuel + m0_ox; % total propellant mass, kg

Isp = 220;   % Specific impulse of the rocket, s
V_e = g*Isp; % exhaust velocity, m/s
T = 4500;    % Thrust, N - we're gonna assume no regression for now

m_f_dot = (T/V_e)*(1/(OF+1));       % fuel mass flow rate
m_ox_dot = (T/V_e)*(OF/(OF+1));     % oxidiser mass flow rate
m_dot = m_f_dot + m_ox_dot;         % total mass flow rate

t_burn = m_propellant/m_dot;

T_impulse = T*t_burn;

D_e = 60;              % nozzle exit diameter, mm - random guess but has negligible effect
A_e = pi*(D_e/2000)^2; % nozzle exit area

% Rocket Parameters
m_dry = 70;  % dry mass of rocket, kg
Cd = 0.7;        % drag coefficient (neglecting supersonic drag for now cus i dont think we are going this fast (but now we are ffs !!))
D = 0.20;         % rocket diameter in m
A = (pi*D^2)/4;   % cross sectional area of rocket, m^2

% Parachute Parameters
Cd_para = 0.97;                  % Parachute drag coefficient
D_para = 6.1;                    % Parachute diameter, m
A_para = (pi*D_para^2)/4;        % Parachute area, m^2

D_drogue = 1.22;                 % Drogue diameter, m
A_drogue = (pi*D_drogue^2)/4;    % Drogue area, m^2

%% iterate and plot
% apogee = zeros(length(m_dry),1);
% maxV = zeros(length(m_dry),1);
% 
% for i = 1:length(m_dry)
%     DryMass = m_dry(i);
%     out = sim("Nimbus_Sizing_1DOF.slx");
%     apogee(i) = max(out.altitude);
%     maxV(i) = max(out.velocity);
% end
% 
% apogeeFig = figure;
% hold on
% plot(m_dry,apogee)
% yline(3000,LineWidth=2)
% hold off
% xlabel('Dry Mass, kg')
% ylabel('Predicted Apogee, m')
% nicePlot(apogeeFig)
% 
% maxVFig = figure;
% plot(m_dry,maxV)
% xlabel('Dry Mass, kg')
% ylabel('Max Velocity, ms$^{-1}$')
% nicePlot(maxVFig)
% 
% machFig = figure;
% hold on
% plot(m_dry,maxV./atmos(3000,2))
% yline(1,LineWidth=2)
% hold off
% xlabel('Dry Mass, kg')
% ylabel('Mach Number')
% nicePlot(machFig)