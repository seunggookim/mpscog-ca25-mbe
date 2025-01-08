import time, mymne, mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

def meg_ave():
    '''
    This function is to create epochs (_epo.fif) & evoked responses (_ave.fif) from continuous data (fn_raw)
    after (1) low-pass filtering < 40 Hz, (2) down-sampling at 600 Hz
    '''
    suffix_filt = "hp0.5Hz_lp40Hz"

    epochs_tsss = list(range(3))
    cov_run = list(range(3))
    raw_pre = list(range(3))
    for iRun in range(3):
        # read tsss-filtered-ica-corrected data:
        suffix_input = 'hp0.5Hz_notch50sHz'
        fn_tsss = dn_meg + \
                  "/run%i_" % iRun + suffix_input + "_cor_raw_tsss.fif"
        raw_tsss = mne.io.read_raw_fif(fn_tsss, preload=True)

        # Low-pass filtering < 40 Hz:
        raw_tsss.filter(l_freq=None, h_freq=40)

        # Down-sampling at 600 Hz:
        raw_tsss.resample(sfreq=600)

        # epoching all conditions:
        events = mne.find_events(raw_tsss, stim_channel='UPPT001')
        picks_meg = mne.pick_types(
            raw_tsss.info, meg=True, ref_meg=False, eeg=False,
            eog=False, ecg=False, stim=False, exclude='bads')
        event_id = dict(
            HC250NRN=1, HC250RNR=2, HC20NRN=3, HC20RNR=4,
            CT250NRN=5, CT250RNR=6, CT20NRN=7, CT20RNR=8,
            RIN250NRN=9, RIN250RNR=10, RIN20NRN=11, RIN20RNR=12)
        epochs_tsss[iRun] = mne.Epochs(
            raw_tsss, events, event_id, tmin=-0.250, tmax=2.550,
            picks=picks_meg, baseline=(None, 0), reject=dict(mag=5e-12),
            preload=True)

        # find pre-run epochs for noise covariance matrix
        tmax = events[0][0] / raw_tsss.info['sfreq']
        raw_pre[iRun] = raw_tsss.copy().crop(tmax=tmax)
        cov_run[iRun] = mne.compute_raw_covariance(
            raw_pre[iRun], picks=picks_meg, reject=dict(mag=3e-12))
        fn_cov = dn_meg + "/run%i_" % iRun + suffix_out + \
                 "_cor_raw_tsss_prerun_cov.fif"
        mne.write_cov(fn_cov, cov_run[iRun])

    # concatenate all runs & save:
    epochs_tsss_all = mne.concatenate_epochs(epochs_tsss)
    fn_epochs = dn_meg + "/all_tsss_" + suffix_filt + "_cor_epo.fif"
    epochs_tsss_all.save(fn_epochs)

    # average epochs (evoked responses) & save:
    evoked_all = epochs_tsss_all.average()
    fn_evoked = dn_meg + "/all_tsss_" + suffix_filt + "_cor_ave.fif"
    mne.write_evokeds(fn_evoked, evoked_all)
    return


def stc_ave():
    '''
    This function is to compute source-time-course from
    (1) evoked MEG signal (_ave.fif)
    (2) coregistration (fn_trans)
    (3) forward solution from given source space (src) and 1layer-BEM
    (4) noise covariance (fn_cov)
    '''

    # Read averaged epochs:
    fn_evoked = dn_meg + "/all_tsss_" + suffix_filt + "_cor_ave.fif"
    evoked_all = mne.read_evokeds(fn_evoked)
    evoked_all = evoked_all[0]

    # Read the 0-th noise covariance:
    cov_run = list(range(1))
    fn_cov = dn_meg + "/run%i_" % 0 + suffix_filt + \
             "_cor_raw_tsss_prerun_cov.fif"
    cov_run[0] = mne.read_cov(fn_cov)

    # Compute/read forward solution
    fn_fwd = dn_bem + "/" + subj + "-10242-fwd.fif"
    if not os.path.isfile(fn_fwd):
        bem = mne.read_bem_solution(
            dn_bem + "/" + subj + "-10242-1layer-bem-sol.fif")
        fn_trans = dn_meg + "/" + subj + "-trans.fif"
        trans = mne.read_trans(fn_trans)
        src = mne.read_source_spaces(
            dn_bem + "/" + subj + "-10242-src.fif")
        fwd = mne.make_forward_solution(
            evoked_all.info, trans=trans, src=src, bem=bem)
        mne.write_forward_solution(fn_fwd, fwd)  # , overwrite=True)
        del bem, trans, src
    else:
        fwd = mne.read_forward_solution(fn_fwd)

    # Make inverse solution
    inv = mne.minimum_norm.make_inverse_operator(
        evoked_all.info, fwd, cov_run[0])
    fn_inv = dn_bem + "/" + subj + "-10242-allconds-inv.fif"
    mne.minimum_norm.write_inverse_operator(fn_inv, inv)

    # Apply inverse solution & save results
    stc = mne.minimum_norm.apply_inverse(evoked_all, inv, 1 / 3 ** 2, 'dSPM')
    stc.save(fname=dn_meg + "/all_tsss_" + suffix_filt + "_cor_ave_ico5")
    return


def morph_ave():
    '''
    This is to morph source-time-course of evoked responses in individual spaces
    to FSAVERAGE template space
    '''

    # Read source space
    src = mne.read_source_spaces(dn_bem + "/" + subj + "-10242-src.fif")

    # individual source space = 10242 verts x 2 hemi = 20484 vertices
    morph = mne.compute_source_morph(
        src=src, subject_from=subj, subject_to='fsaverage', spacing=5)
    # fsavg5 : 10242 x 2 = 20484 vertices
    
    # all events:
    fn_stc = dn_meg + "/all_tsss_" + suffix_filt + "_cor_ave"
    stc = mne.read_source_estimate(fn_stc, subject=subj)
    stc = morph.apply(stc)
    stc.save(fname=dn_meg + "/all_tsss_" + suffix_filt + "_cor_ave_fsavg")
    mymne.viz_stc_fs(stc, title=subj + ': all conditions',
               prefix_png=dn_meg + "/all_tsss_" + suffix_filt + "_cor_ave_fsavg")
    
    # each event:
    event_id = dict(
        HC250NRN=1, HC250RNR=2, HC20NRN=3, HC20RNR=4,
        CT250NRN=5, CT250RNR=6, CT20NRN=7, CT20RNR=8,
        RIN250NRN=9, RIN250RNR=10, RIN20NRN=11, RIN20RNR=12)
    
    for event in event_id.keys():
        fn_stc = dn_ave + "/" + event
        stc = mne.read_source_estimate(fn_stc, subject=subj)
        stc = morph.apply(stc)
        stc.save(fname=dn_ave + "/" + event + "_fsavg")
        mymne.viz_stc_fs(stc, title=subj + ': ' + event,
                   prefix_png=dn_ave + "/" + event + "_fsavg")
    return

# ------------------------------------------------------------------------------
mne.set_config("SUBJECTS_DIR", "/mnt/data/MEG_pitch/data/fs+mne")
dframe = pd.read_excel(
    "/mnt/data/MEG_pitch/data/rawdata/MEGStudy/Subjects.xlsx",
    sheet_name="rawdata")
subjects = dframe.SubjectID.tolist()

for iSubj in (0, 1, 3, 4, 7,  12, 15, 17, 18, 19):  # GOOD subjects (n=10)
    subj = subjects[iSubj]
    dn_meg = mne.get_config('SUBJECTS_DIR') + "/" + subj + "/meg"
    dn_bem = mne.get_config('SUBJECTS_DIR') + "/" + subj + "/bem"

    if not os.path.isfile(dn_ave + "/" + subj + "_" + "RIN20RNR_fsavg-rh.stc"):
        print("> Morphing " + subj + "..")
        morph_ave()