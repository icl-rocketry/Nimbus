% so atmosisa can be super annoying so here's a version which should be less annoying - usmaan
% 
% Outputs - var       = return variable
%
% Inputs  - altitude  = altitude (m)
%         - index     = atmosisa variable index
%                         1 = temperature (K)
%                         2 = speed of sound (ms^-1)
%                         3 = pressure (Pa)
%                         4 = air density (kgm^-3)

function var = atmos(altitude, index) 
	[A, B, C, D] = atmosisa(altitude);
	mat = [A; B; C; D];
	var = mat(index, :);
end
