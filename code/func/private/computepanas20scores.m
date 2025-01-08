function [factorscores, factorperctiles, factornames] = computepanas20scores(ratings)
%computepanas20scores computes PANAS scores
%
% USAGE
% [factorscores, factorperctiles, factornames] = computepanas20scores(ratings)
%
% 2024, seung-goo.kim@ae.mpg.de
%
% REF: 


% % % % REF: https://ogg.osu.edu/media/documents/MB%20Stream/PANAS.pdf
% % % % REF: Watson, Clark, Tellegen, 1988, JPSP.
% % % %
% % % % PAS: idx=[1,3,5,9,10,12,14,16,17,19]; mean = 33.3; sd=7.2
% % % % NAS: idx=[2,4,6,7,8,11,13,15,18,20]; mean = 17.4, sd=6.2

assert(min(ratings)>0, 'Scales seem 0-based! | expecting 1-based scales')

PAS = sum(ratings([1,3,5,9,10,12,14,16,17,19]));
NAS = sum(ratings([2,4,6,7,8,11,13,15,18,20]));
factorscores = [PAS NAS];
factorperctiles = [cdf('norm',PAS, 33.3, 7.2), cdf('norm',NAS, 17.4, 6.2)];
factornames = {'PositiveAffect','NegativeAffect'};
end
