clc
clear all
close all

load('Inputdata.mat')


n_participant = size(Inputdata.Participant,2);

for i = 1:n_participant
    n_trial = size(Inputdata.Participant(i).Trial,2);
    for ii = 1:n_trial
        Beltvelocity = Inputdata.Participant(i).Trial(ii).Beltvelocity.data;
        Refpoint_TD = Inputdata.Participant(i).Trial(ii).Referencepoint_TD;
        Refpoint_FO = Inputdata.Participant(i).Trial(ii).Referencepoint_FO;

        
       [Baselinevelocity, PerturbationOffset,PerturbationOffset_relative, Acceleration1Duration, Acceleration2Duration, VelocityAmplitude, PerturbationDistance] = getPerturbationParameters(Beltvelocity,200,Refpoint_TD,Refpoint_FO,2);

       
       PerturbationParameters.Participant(i).Trial(ii).Baselinevelocity = Baselinevelocity;
       PerturbationParameters.Participant(i).Trial(ii).PerturbationOffset = PerturbationOffset;
       PerturbationParameters.Participant(i).Trial(ii).PerturbationOffset_relative = PerturbationOffset_relative;
       PerturbationParameters.Participant(i).Trial(ii).Acceleration1Duration = Acceleration1Duration;
       PerturbationParameters.Participant(i).Trial(ii).Acceleration2Duration = Acceleration2Duration;
       PerturbationParameters.Participant(i).Trial(ii).VelocityAmplitud = VelocityAmplitude;
       PerturbationParameters.Participant(i).Trial(ii).PerturbationDistance = PerturbationDistance;
    end
end

save('PerturbationParameters.mat',"PerturbationParameters",'-mat')