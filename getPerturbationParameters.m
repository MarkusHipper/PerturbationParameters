function [Baselinevelocity, PerturbationOffset,PerturbationOffset_relative, Acceleration1Duration, Acceleration2Duration, VelocityAmplitude, PerturbationDistance] = getPerturbationParameters(Beltvelocity,Frequency,Refpoint_TD,Refpoint_FO,Multiplier_STD)
%Summary
% This function calculates various parameters of a belt perturbation.
% The output parameters include velocities, offsets, durations, amplitude,
% and distance of the perturbation.



% Calculate basline velocity and standard deviation
Baselinevelocity = mean(Beltvelocity(1,1:3 * Frequency));
Baselinevelocity_std = std(Beltvelocity(1,1:3 * Frequency));

%Calculate Perturbationvelocity
[PerturbationVelocity_abs , PerturbationVelocity_index]= max(abs(Beltvelocity));
PerturbationVelocity_max = Beltvelocity(1,PerturbationVelocity_index);

% Calculate perturbation start
for i = PerturbationVelocity_index : -1 : 1
    if Beltvelocity(1, PerturbationVelocity_index) > 0 %Slip-like Perturbation
        if Beltvelocity(1,i) <= (Baselinevelocity + Multiplier_STD * Baselinevelocity_std)
            PerturbationStart = i;
            break
        end
    elseif Beltvelocity(1, PerturbationVelocity_index) < 0 %Trip-like Perturbation
        if Beltvelocity(1,i) >= (Baselinevelocity - Multiplier_STD * Baselinevelocity_std)
            PerturbationStart = i;
            break
        end
    end
end

%Calculate perturbation end
for ii = PerturbationVelocity_index : size(Beltvelocity,2)
    if Beltvelocity(1, PerturbationVelocity_index) > 0 %Slip-like Perturbation
        if Beltvelocity(1,ii) <= (Baselinevelocity + Multiplier_STD * Baselinevelocity_std)
            PerturbationEnd = ii;
            break
        end
    elseif Beltvelocity(1, PerturbationVelocity_index) < 0 %Trip-like Perturbation
        if Beltvelocity(1,ii) >= (Baselinevelocity - Multiplier_STD * Baselinevelocity_std)
            PerturbationEnd = ii;
            break
        end
    end
end

%Calculate Perturbation distance 
PerturbationDistance_temp = cumtrapz(Beltvelocity(round(PerturbationStart):round(PerturbationEnd)));

% Calculate Perturbation offset (abs)
PerturbationOffset = (PerturbationStart - Refpoint_TD)/Frequency;

%Calculate perturbation offset (rel) if Refpint_FO is given
if Refpoint_FO ~= 0
    PerturbationOffset_relative = PerturbationOffset / ((Refpoint_FO - Refpoint_TD)/Frequency);
else
    PerturbationOffset_relative = 'Refpoint_FO is missing';
end

% Calculate acceleration phase one durration
Beltacceleration = diff(abs(Beltvelocity));
for iii = PerturbationStart:size(Beltvelocity,2)
    if Beltacceleration(iii) <= 0 && abs(Beltvelocity(iii))> PerturbationVelocity_max-Multiplier_STD*Baselinevelocity_std
PlateauStart = iii-1;
break
    end
end
Acceleration1Duration = (PlateauStart - PerturbationStart) / Frequency;

% Calculate acceleration phase two durration
for iiii = PerturbationEnd:-1:1
    if Beltacceleration(iiii) >= 0 && abs(Beltvelocity(iiii))> PerturbationVelocity_max-Multiplier_STD*Baselinevelocity_std
PlateauEnd = iiii+1;
break
    end
end
Acceleration2Duration = (PerturbationEnd - PlateauEnd) / Frequency;

% Calculate perturbation durration
PerturbationDuration = (PerturbationEnd - PerturbationStart) / Frequency;

% Calculate Velocity amplitude
PerturbationVelocity = mean(Beltvelocity(1,PlateauStart:PlateauEnd));
VelocityAmplitude = abs(Baselinevelocity - PerturbationVelocity);

%Calculate perturbation distance
PerturbationDistance = PerturbationDistance_temp(1,end)/Frequency - (Baselinevelocity* PerturbationDuration) ;
end