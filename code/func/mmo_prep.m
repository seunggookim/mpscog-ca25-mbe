function Y = mmo_prep(Dataset, Cfg)
%MMO_PREP runs preprocessing (high-pass sampling and alignment across subjects) and return rating
% as matrices (#times x #subjects) for each scale:
% {'Liking'}    {'Disliking'}    {'Relaxed'}    {'Excited'}    {'DislikingToLiking'}    {'RelaxedToExcited'})
%
% Y = mmo_prep(Dataset, Cfg)
%     Cfg = defaultcfg(struct(HighPassHz=0.01, SamplingRateHz=1, ToiSec=[15 -15]), Cfg, mfilename);

Cfg = defaultcfg(struct(HighPassHz=0.01, SamplingRateHz=1, ToiSec=[15 -15]), Cfg, mfilename);
if not(isduration(Cfg.ToiSec))
  Cfg.ToiSec = seconds(Cfg.ToiSec);
end

X = {};
for iSet = 1:numel(Dataset)
  for jTrial = 1:numel(Dataset(iSet).Jamendo)
    if Dataset(iSet).Jamendo{jTrial}.Properties.UserData.Stimulus.TrackInfo == Cfg.TrackId
      break
    end
  end
  X{iSet} = Dataset(iSet).Jamendo{jTrial};
  if Cfg.HighPassHz
    X{iSet} = highpass(X{iSet}, Cfg.HighPassHz);
  end
end
Tt = synchronize(X{:}, 'regular', 'linear', 'samplerate',Cfg.SamplingRateHz);
Tt = ...
  Tt( ( Tt.Time >= Cfg.ToiSec(1) ) ...
    & ( Tt.Time <= (Tt.Time(end) + Cfg.ToiSec(2)) ) ,:);
% Tt = trimdata(Tt, ceil(seconds(Cfg.TrimSec(1))/Tt.Properties.TimeStep), side="leading");
% Tt = trimdata(Tt, floor(seconds(Cfg.TrimSec(2))/Tt.Properties.TimeStep), side="trailing");

varNames = X{iSet}.Properties.VariableNames;

Y = struct(Time=Tt.Time);
for jVar = 1:numel(varNames)
  Y.(varNames{jVar}) = [];
  for iSet = 1:numel(Dataset)
    Y.(varNames{jVar}) = [Y.(varNames{jVar}), Tt.([varNames{jVar},'_',num2str(iSet)])];
  end
end

end