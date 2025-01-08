%{
LOCAL-JATOS TEST
http://localhost:9000/publix/eTj66qun1Ay

WEB-JATOS TEST
https://onlineexperiment.ae.mpg.de/publix/fHLhq8lFigW 

WEB-JATOS MAIN
https://onlineexperiment.ae.mpg.de/publix/eIXedE8yqVL 
%}

cd ~/MATLAB-Drive/mpscog-ca25-mbe/musafx-online-analysis/
addpath code/matlab/func/
mmo_addpath()
%%
Dataset = [];
Dataset = [Dataset, mmo_import('data/mps-test/study_result_6734/comp-result_12208/data.txt')];
Dataset = [Dataset, mmo_import('data/mps-test/study_result_6737/comp-result_12211/data.txt')];

%%
Y = mmo_prep(Dataset, struct(TrackId=1374300, ToiSec=[30 -30]) );
clf; plot(Y.RelaxedToExcited)
%%


files = findfiles('/Users/seung-goo.kim/MATLAB-Drive/mpscog-ca25-mbe/musafx-online-analysis/data/mps-main/jatos_results_data_20241205104744/*/*/data.txt')
%%
Dataset = [];
for i = 1:numel(files)
  try 
    Dataset = [Dataset, mmo_import(files{i})];
  end
end
%% Correlation btw AROUSAL (spotify-1) vs. PAS
PAS = []; mA = [];
for iSub = 1:numel(Dataset)
  mA(iSub) = mean(Dataset(iSub).Spotify{1}.Excited);
  PAS(iSub) = Dataset(iSub).Panas.Factors.Score(1);
end
%%
lm = fitlm(mA, PAS)
plot(lm)