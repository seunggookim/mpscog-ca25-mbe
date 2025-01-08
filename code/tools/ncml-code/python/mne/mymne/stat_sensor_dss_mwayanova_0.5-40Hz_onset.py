# ----------------------------------------------------
# THREE-WAY (REG x F0 x TYPE) RMANOVA ON ONSET-DSS
# ----------------------------------------------------
import mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt
import time, mymne, scipy.io

# Read data
dn_in = '/mnt/data/MEG_pitch/data/fs+mne/fsaverage/meg/all_tsss_hp0.5Hz_lp40Hz_cor_epo.mat'
dss = scipy.io.loadmat(dn_in + '/dss1_onset.mat')
n_conditions = 2*2*3
n_subjects = dss['HC250N'].shape[0]
n_times = len(dss['times'])  # 421 [-0.2, 0.5]
X_onset = [np.zeros([n_subjects, n_times]) for i in range(n_conditions)]
for isub in range(n_subjects):
    icond = 0
    for reg in ("N", "R"):
        for freq in ("20", "250"):
            for prdtype in ("HC", "CT", "RIN"):
                event = prdtype + freq + reg
                print(event)
                X_onset[icond][isub, :] = dss[event][isub]
                icond += 1


effects = ["A", "B", "C", "A:B", "B:C", "A:C", "A:B:C"]
effects_human = ['onset_Reg', 'onset_Freq', 'onset_Type',
                 'onset_RegxFreq', 'onset_FreqxType', 'onset_RegxType',
                 'onset_RegxFreqxType']
factor_levels = [2, 2, 3]

dn_out = dn_in
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
    n_permutations = 1000 * 10

    # in each n-D array, the first dimension is the number of samples/observations
    fn = dn_out + '/dss1_3way_' + effect_human + '_k%d.mat' % n_permutations
    if not os.path.isfile(fn):
        start_time = time.time()
        f, c, p, h0 = mne.stats.permutation_cluster_test(
            X_onset, stat_fun=stat_fun, threshold=f_thresh, tail=tail, n_jobs=20,
            n_permutations=n_permutations, buffer_size=None)
        # converting slice to array
        c_array = np.zeros(n_times,)
        p_array = np.zeros(n_times,)
        for j in range(c.__len__()):
            c_array[c[j]] = j+1
            p_array[c[j]] = p[j]
        scipy.io.savemat(fn, mdict={'f': f, 'c': c_array, 'p': p_array, 'h0': h0})
        print("%i permutations took: %f sec"
              % (n_permutations, time.time() - start_time))


