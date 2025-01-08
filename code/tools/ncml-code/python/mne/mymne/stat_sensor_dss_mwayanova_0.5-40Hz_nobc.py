# ----------------------------------------------------
# TWO-WAY (F0 X STIM) RMANOVA ON NR OR RN TRANSITIONS
# ----------------------------------------------------
import mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt
import mymne, scipy.io
dn = '/mnt/data/MEG_pitch/data/fs+mne/fsaverage/meg/all_tsss_hp0.5Hz_lp40Hz_cor_epo.mat'
dss = scipy.io.loadmat(dn + '/dss1_trans_nobc.mat')
'''
"data" (for f_mway_rm) is a ndarray like:
----------------------------
subj  A1B1  A1B2  A1B3  ...
S01   x1    x2    x3    ...
----------------------------
0-dim: # of repetitions (trials of subjects)
1-dim: # of conditions
2-dim: # of (spatial x spectral x temporal) measures
'''
n_conditions = 2 * 3
n_times = len(dss['times'][0]) # 661 [-0.2, 0.9]
n_subjects = dss['HC250_NR'].shape[1]
trans = ['NR', 'RN']
stims = ['HC', 'CT', 'RIN']
f0s = ['250', '20']

for tran in trans:  # NR or RN
    X = list()
    conds = list()
    for f0 in f0s:  # 2 levels
        for stim in stims:  # 3 levels
            X.append(dss[stim + f0 + '_' + tran].T)
            conds.append(tran + '_' + f0 + stim)
    effects = ["A", "B", "A:B"]
    effects_human = ['F0', 'STIM', 'F0xSTIM']
    factor_levels = [2, 3]
    
    # F_obs, clusters, cluster_pvals, H0 = list(), list(), list(), list()
    for effect, effect_human in zip(effects, effects_human):
        # 1. Compute critical value for F-stat:
        pthresh = 0.001  # set threshold rather high to save some time
        f_thresh = mne.stats.f_threshold_mway_rm(
            n_subjects, factor_levels, effect, pthresh)
        print("F-threshold for \"" + effect + "\": %.2f" % f_thresh)
    
        # 2. Define stat_fun for a specific effect
        def stat_fun(*args):
            return mne.stats.f_mway_rm(
                np.swapaxes(args, 1, 0), factor_levels=factor_levels,
                effects=effect, return_pvals=False)[0]
    
        # 3. Run CBPT
        tail = 1  # f-test, so tail > 0
        # Save some time (the test won't be too sensitive ...)
        n_permutations = 1000 * 10
        # permutation_cluster_test: data should be a list of n-D arrays
        # in each n-D array, the first dimension is the number of samples/observations
        fn = dn + '/dss1_nobc_trans_rmanova_' + tran + '_' + effect_human + '_k%i.mat' % n_permutations
        if not os.path.isfile(fn):
            f, c, p, h0 = mne.stats.permutation_cluster_test(
                X, stat_fun=stat_fun, threshold=f_thresh, tail=tail, n_jobs=20,
                n_permutations=n_permutations, buffer_size=None)
            # converting slice to array
            c_array = np.zeros(n_times,)
            p_array = np.zeros(n_times,)
            for j in range(c.__len__()):
                c_array[c[j]] = j+1
                p_array[c[j]] = p[j]
            scipy.io.savemat(fn, mdict={'f': f, 'c': c_array, 'p': p_array, 'h0': h0})


