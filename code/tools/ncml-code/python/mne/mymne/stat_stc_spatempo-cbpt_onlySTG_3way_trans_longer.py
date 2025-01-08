import mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt
os.sys.path.append('/mnt/data/MEG_pitch/codes/log_py')
import mymne, scipy.io, pickle as pkl

##
# PREPARE data lists (downsampled to ico5)
'''
Desired data structure:
X = [X1, X2, ... Xk] for k conditions
Xi is (n_obs, n_times, n_vertices)
'''
fn_src = '/mnt/data/MEG_pitch/data/fs+mne/fsaverage/bem/fsaverage-ico5-src.fif'
src = mne.read_source_spaces(fn_src)
rois = ['transversetemporal', 'superiortemporal']
parc = 'aparc'
exclude, include = mymne.get_spatial_exclude_from_rois(rois, parc, src)
connectivity = mne.spatial_src_connectivity(mne.read_source_spaces(fn_src))
connectivity_stg = connectivity.tocsr()[include, :].tocsc()[:, include]
##
dn_data = \
    '/mnt/data/MEG_pitch/data/fs+mne/fsaverage/meg/n10_ave_0.5-40Hz_stc_fsavg'
if not os.path.isdir(dn_data):
    os.mkdir(dn_data)

fn_pkl = dn_data + '/stg_X_trans_2x2x3_long.pkl'
if not os.path.isfile(fn_pkl):  # if not done yet:
    # READ source time course (STC) files of evoked responses:
    event_names = [
        'HC250NRN', 'HC250RNR', 'HC20NRN', 'HC20RNR',
        'CT250NRN', 'CT250RNR', 'CT20NRN', 'CT20RNR',
        'RIN250NRN', 'RIN250RNR', 'RIN20NRN', 'RIN20RNR']
    subjects = [
        'S01', 'S02', 'S04', 'S05', 'S08', 'S13', 'S16', 'S18', 'S19', 'S20']
    stc = dict()
    for event in event_names:
        stc[event] = list()
    for subj in subjects:
        dn_ave = "/mnt/data/MEG_pitch/data/fs+mne/" + subj + "/meg/ave_0.5-40Hz"
        print(dn_ave)
        for event in event_names:
            tmp = mne.read_source_estimate(fname=dn_ave + "/" + event + "_fsavg")
            stc[event].append(tmp)
    
    ##
    # EPOCH transitions & COMPUTE averages:
    X_trans = list(range(2*2*3))
    n_sub = 10
    n_times = 661  # -0.2 to 0.9 sec (1.1 sec)
    n_vertices = len(include)
    
    for itype in range(2*2*3):
        X_trans[itype] = np.zeros([n_sub, n_times, n_vertices])
    
    for isub in range(len(subjects)):
        icond = 0
        for reg in ["RN", "NR"]:
            for freq in ["20", "250"]:
                for prdtype in ["HC", "CT", "RIN"]:
                    for condreg in ["NRN", "RNR"]:
                        event = prdtype + freq + condreg
                        t = dict()
                        if 'NRN' in event:  # (0, 0.5, 1.4)
                            t['NR'] = 0.5  # NR transition
                            t['RN'] = 1.4  # RN transition
                        else:
                            t['RN'] = 0.5  # RN transition
                            t['NR'] = 1.4  # NR transition
                        print(event)
                        epo = stc[event][isub].copy().crop(
                            tmin=t[reg]-0.2, tmax=t[reg]+0.9)
                        epo.tmin = -0.2
                        # 20484 x 421
                        x = epo.data[include].transpose()
                        X_trans[icond][isub, :, :] += x
                    X_trans[icond][isub, :, :] /= 2
                    icond += 1
        
    tstep = epo.tstep
    times = epo.times
    del stc  # to save memory
    
    # Pickle epoched transitions:
    outfile = open(fn_pkl, 'wb')
    pkl.dump([X_trans, tstep, times, include,
              ['X_trans', 'tstep', 'times', 'include']],
             outfile)
    outfile.close()

    fn_mat = dn_data + '/stg_X_trans_2x2x3_long.mat'
    scipy.io.savemat(fn_mat, dict(X_trans=X_trans, times=times, include=include),
                     do_compression=True)
else:  # if done, read it!
    infile = open(fn_pkl, 'rb')
    [X_trans, tstep, times, include, _] = pkl.load(infile)
    infile.close()


##
'''
Desired data structure:
X = [X1, X2, ... Xk] for k conditions
Xi is (n_obs, n_times, n_vertices)

'''
n_conditions = 2*2*3
n_subjects = 10
n_times = 661
effects = ["A", "B", "C", "A:B", "B:C", "A:C", "A:B:C"]
effects_human = ['trans_Reg', 'trans_Freq', 'trans_Type',
                 'trans_RegxFreq', 'trans_FreqxType', 'trans_RegxType',
                 'trans_RegxFreqxType']
factor_levels = [2, 2, 3]
dn_out = dn_data
for effect, effect_human in zip(effects, effects_human):
    # 1. Compute critical value for F-stat:
    pthresh = 0.001  # set threshold rather high to save some time
    f_thresh = mne.stats.f_threshold_mway_rm(
        n_subjects, factor_levels, effect, pthresh)
    print("F-threshold for \""+effect+"\": %.2f" % f_thresh)

    # 2. Define stat_fun for a specific effect
    def stat_fun(*args):
        return mne.stats.f_mway_rm(
            np.swapaxes(args, 1, 0), factor_levels=factor_levels,
            effects=effect, return_pvals=False)[0]

    # 3. Run CBPT
    tail = 1  # f-test, so tail > 0
    # Save some time (the test won't be too sensitive ...)
    n_permutations = 1000 * 10
    
    fn = dn_out + '/stg_3way_' + effect_human + '_k%d_long.pkl' % n_permutations
    if not os.path.isfile(fn):
        import time
        start_time = time.time()
        f, c, p, h0 = mne.stats.spatio_temporal_cluster_test(
            X_trans, stat_fun=stat_fun, threshold=f_thresh, tail=tail,
            n_jobs=10, n_permutations=n_permutations, buffer_size=None,
            spatial_exclude=None, connectivity=connectivity_stg)
        outfile = open(fn, 'wb')
        pkl.dump([f, c, p, h0, ['f', 'c', 'p', 'h0']], outfile)
        outfile.close()
        print("%i permutations took: %f sec"
              % (n_permutations, time.time() - start_time))
        '''
        Now with 4 conditions (4 lists) I can only run 1 job at a time.
        Thus 1000 permutations took 16456 sec (4.5 hours)
        
        Now for STG only (1379 vertices), I can run 16 jobs
        Thus 1000 permutations took 161 sec (2.7 min)
        : and identical results with all together!
        : 10000 permutations took: 1080.642025 sec
        '''
    else:
        infile = open(fn, 'rb')
        [f, c, p, h0, _] = pkl.load(infile)
        infile.close()
  
    ## Results
    '''
    f : (ndarray) #times x #verts
    c : (list) #clusters
        c[0] : (tuple)
            c[0][0] : time indices
            c[0][1] : vertex indices
    p : (ndarray) #clusters
    '''
    fn_out = dn_out + "/stg_3way_" + effect_human + "_k%d_long.mat" % n_permutations
    scipy.io.savemat(
        fn_out, dict(f=f, c=c, p=p, h0=h0, t=times, include=include),
        do_compression=True)
    
