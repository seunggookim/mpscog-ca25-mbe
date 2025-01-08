function Data = mmo_import(fnameTxt)
%MMO_IMPORT parses JATOS-jsPysch data of ManyMusic-Online (MM-O)
%
% Data = mmo_import(fnameTxt)

[~, compId, ~] = fileparts(fileparts(fnameTxt));
c = strsplit(compId,'_');
Data = struct(RespId=c{2});
logthis('ResponseID = "%s"\n', Data.RespId)

INDEX_PANAS = 1;
INDEX_BMRQ = 8;
IDX_PRACTICE = 2;
IDX_SPOTIFY = [3 7];
IDX_JAMENDO = [4 5 6];
VARNAMES = {'Liking','Disliking','Relaxed','Excited'};

%% READ file
jsData = fileread(fnameTxt);
idxLeft = strfind(jsData,'{');
idxRight = strfind(jsData,'}');
levels = zeros(numel(jsData),1);
levels(idxLeft) = 1;
levels(idxRight) = -1;
levels = cumsum(levels);
idxZero = [0; find(levels==0)];
trialType = ["survey-likert", "audio-grid-latency-calibration", "audio-grid-tracking", "audio-grid-tracking", ...
  "audio-grid-tracking", "audio-grid-tracking", "audio-grid-tracking", "survey-likert", "survey-multi-choice"];
trials = {};
for i = 1:numel(idxZero)-1
  txt = jsData(idxZero(i)+1:idxZero(i+1));
  trials = [trials, jsondecode(txt).trials ];
  assert(strcmp(trials{end}.trial_type, trialType(i)), '[Trial-%i] type="%s" | expected type="%s"', ...
    i, trials{end}.trial_type, trialType(i))
end
logthis('TIMELINE validity check: PASS\n')

%% SCORE questionnaires: PANAS

panasValues = [];
fldNames = fieldnames(trials{INDEX_PANAS}.response);
for i = 1:numel(fldNames)
  panasValues = [panasValues; trials{INDEX_PANAS}.response.(fldNames{i}) ];
end
assert(isequal(trials{INDEX_PANAS}.question_order, (0:9)'), 'PANAS questions were randomized?!')
if all(panasValues(1)==panasValues)
  logthis('*WARN* PANAS: STRAIGHT-LINING DETECTED!\n')
end
panasValues = panasValues + 1; % 1-based index
[factorscores, factorperctiles, factornames] = computepanas10scores(panasValues);
Data.Panas.Factors = table(factorscores', factorperctiles');
Data.Panas.Factors.Properties.VariableNames = {'Score', 'Percentile'};
Data.Panas.Factors.Properties.RowNames = factornames';
Data.Panas.Values = panasValues;

%% SCORE questionnaires: BMRQ

bmrqValues = [];
fldNames = fieldnames(trials{INDEX_BMRQ}.response);
for i = 1:numel(fldNames)
  bmrqValues = [bmrqValues; trials{INDEX_BMRQ}.response.(fldNames{i}) ];
end
bmrqValues = bmrqValues + 1; % 1-based index
assert(isequal(trials{INDEX_BMRQ}.question_order, (0:19)'), 'BMRQ questions were randomized?!')
if all(bmrqValues(1)==bmrqValues)
  logthis('*WARN* BMRQ: STRAIGHT-LINING DETECTED!\n')
end
[factorscores, factorperctiles, factornames] = computebmrq20factorscores(bmrqValues);
Data.Bmrq.Factors = table(factorscores', factorperctiles');
Data.Bmrq.Factors.Properties.VariableNames = {'Score', 'Percentile'};
Data.Bmrq.Factors.Properties.RowNames = factornames';
Data.Bmrq.Values = bmrqValues;

%% PARSE emotioal tracking data as TimeTable at 125 Hz
Data = helper_readratings(trials, Data, IDX_SPOTIFY, 'Spotify');
Data = helper_readratings(trials, Data, IDX_JAMENDO, 'Jamendo');


end


function Data = helper_readratings(trials, Data, IDX, fieldname)
Data.(fieldname) = {};
for i = 1:numel(IDX)
  TrialName = sprintf('%s-trial%02i', fieldname, i);
  j = IDX(i);
  if not(isempty(trials{j}.mouseData))
    xyValues = [[trials{j}.mouseData.xScaled]',[trials{j}.mouseData.yScaled]'];
    Times = [trials{j}.mouseData.movementTimeRelSec]';

    % normalize scales
    eval([trials{j}.axisLabels.xLabelPositive,' = max(xyValues(:,1),0);']);
    eval([trials{j}.axisLabels.xLabelNegative,' = max(-xyValues(:,1),0);']);
    eval([trials{j}.axisLabels.yLabelPositive,' = max(xyValues(:,2),0);']);
    eval([trials{j}.axisLabels.yLabelNegative,' = max(-xyValues(:,2),0);']);

    DislikingToLiking = Liking - Disliking;
    RelaxedToExcited = Excited - Relaxed;

    Tt = timetable(seconds(Times), Liking, Disliking, Relaxed, Excited, DislikingToLiking, RelaxedToExcited);
    Tt = retime(Tt, 'regular', 'nearest', 'SampleRate',125); % regular resample to 125 Hz
  else
    Tt = timetable();
    logthis('*WARN* No emotional tracking data for "%s"\n', TrialName)
  end
  Tt.Properties.Description = TrialName;
  Tt.Properties.UserData.Stimulus = struct(TrackInfo=trials{j}.track_id, TrackUrl=trials{j}.stimulus);
  Tt.Properties.UserData.OrigAxisLabels = trials{j}.axisLabels; % preserve original axes

  Data.(fieldname){i} = Tt;
end

end