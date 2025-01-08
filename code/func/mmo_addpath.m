function mmo_addpath(Job)
%MMO_ADDPATH adds paths to access functions for ManyMusic-Online analysis
%   MMO_ADDPATH()

[MyPath,~,~] = fileparts(mfilename('fullpath'));
addpath (fullfile(MyPath,'..','tools','ncml-code','matlab','sgfunc'))
sgfunc_addpath()

if not(exist('Job','var')); Job = []; end
Job = defaultjob(struct(IsLea=false), Job, mfilename);

if Job.IsLea
  addpath (fullfile(MyPath,'..','tools','ncml-code','matlab','lea'))
  lea_addpath()
end

set(0, 'DefaultFigureColormap', flipud(brewermap(256,'spectral')), 'DefaultAxesColorOrder', get_colormap(6,1), ...
  'DefaultAxesTickDir','out', 'DefaultFigureColor','w', 'DefaultAxesLineWidth',1, 'DefaultLineLineWidth',2)

end
