function [factorscores, factorperctiles, factornames] = computepanas10scores(ratings)
%computepanas10scores computes 10-item I-PANAS-SF scores
%
% USAGE
% [factorscores, factorperctiles, factornames] = computepanas10scores(ratings)
%
% 2024, seung-goo.kim@ae.mpg.de
%
% REF: Thompson, 2007, IACCP. https://doi.org/10.1177/0022022106297301 (I-PANAS-SF)
%
% positive = [determined, attentive, alert, inspired, active]
% negative = [afraid, nervous, upset, ashamed, hostile]
% PA: US (n=411), M=19.73, SD=2.59
% NA: US (n=411), M=11.27, SD=2.66

assert(min(ratings)>0, 'Scales seem 0-based! | expecting 1-based scales')

PAS = sum(ratings([3, 5, 7, 8, 10]));
NAS = sum(ratings([1, 2, 4, 6, 9]));
factorscores = [PAS NAS];
factorperctiles = [cdf('norm', PAS, 19.73, 2,59), cdf('norm', NAS, 11.27, 2.66)]*100;
factornames = {'PositiveAffect','NegativeAffect'};
end
