import mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt
import mymne, scipy.io

suffix_filt = "hp0.5Hz_notch50sHz"

event_names = [
    'HC250NRN', 'HC250RNR', 'HC20NRN', 'HC20RNR',
    'CT250NRN', 'CT250RNR', 'CT20NRN', 'CT20RNR',
    'RIN250NRN', 'RIN250RNR', 'RIN20NRN', 'RIN20RNR']
mne.set_config("SUBJECTS_DIR", "/mnt/data/MEG_pitch/data/fs+mne")
df = pd.read_excel(
    "/mnt/data/MEG_pitch/data/rawdata/MEGStudy/Subjects.xlsx",
    sheet_name="rawdata")
goodsubjects = df.SubjectID.loc[df.goodmeg_for_tsss == True]

for subj in goodsubjects:
    dn_meg = "/mnt/data/MEG_pitch/data/fs+mne/" + subj + "/meg"
    epochs_tsss = list(range(3))
    for iRun in range(3):
        # Find filename for tsss-filtered-ica-corrected data
        suffix_filt0 = "hp0.5Hz_notch50sHz"
        fn_tsss = dn_meg + \
                  "/run%i_" % iRun + suffix_filt0 + "_cor_raw_tsss.fif"
        
        # Read and BPF
        #raw_tsss = mne.io.read_raw_fif(fn_tsss, preload=True).filter(l_freq=1, h_freq=40)
        
        # Just read:
        raw_tsss = mne.io.read_raw_fif(fn_tsss, preload=True)
        
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
    
    # concatenate all runs & downsample:
    epochs_tsss_all = mne.concatenate_epochs(epochs_tsss)
    epochs_tsss_all.resample(600)
    fn_epochs = dn_meg + "/all_tsss_" + suffix_filt + "_cor_epo.fif"
    if not os.path.isfile(fn_epochs):
        epochs_tsss_all.save(fn_epochs)
    
    # save as MAT files:
    dn_mat = mne.get_config('SUBJECTS_DIR') + "/" + subj + \
             "/meg/all_tsss_" + suffix_filt + "_cor_epo.mat"
    if not os.path.isdir(dn_mat):
        os.mkdir(dn_mat)
    for event in event_names:
        fn_mat = dn_mat + "/" + event + ".mat"
        if not os.path.isfile(fn_mat):
            scipy.io.savemat(
                fn_mat,mdict={'trials': epochs_tsss_all[event].get_data(),
                              'times': epochs_tsss_all[event].times})