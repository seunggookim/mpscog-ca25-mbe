import mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

# NOTE: for methods defined in the same file, all variables are like global?
def get_dest():
    dn_raw = "/mnt/data/MEG_pitch/data/rawdata/MEGStudy/Originals/" \
             + fnames_meg[0][iSubj]
    raw = mne.io.read_raw_ctf(dn_raw, preload=False)
    dest = raw.info['dev_head_t']
    return dest

def maxfilt_and_ica(dest):
    dn_raw = "/mnt/data/MEG_pitch/data/rawdata/MEGStudy/Originals/" \
                 + fnames_meg[iRun][iSubj]
    raw = mne.io.read_raw_ctf(dn_raw, preload=True)
    # 1. MANUAL bad channeral identification by visual inspection:
    raw.plot(n_channels=274)  # Click on channel number (gray) to mark BAD channels!
    mgnr = plt.get_current_fig_manager()
    mgnr.window.setGeometry(0, 24, 1080, 1896)
    plt.show(block=True) # default is block=false;
    '''
    what is "block"?
    [from help] "In non-interactive mode, display all figures and block until
    the figures have been closed."
    '''
    # ==========================================================================
    #    MANUAL IDENTIFICATION: selection using GUI (mark BAD channels GRAY)   #
    # ==========================================================================

    # 2. Maxwell filter (align dev-to-head transform to run0)
    head_pos = mne.chpi._calculate_head_pos_ctf(raw, gof_limit=0.98)
    raw.apply_gradient_compensation(0)
    raw = mne.preprocessing.maxwell_filter(
        raw, st_duration=10, head_pos=head_pos, destination=dest)

    # 3. Artifact correction with ICA
    # high-pass and notch filtering:
    # suffix_filt = "hp0.5Hz_notch50sHz"
    raw.filter(.5, None, fir_design='firwin')
    raw.notch_filter(np.arange(50, 551, 50), phase='zero-double',
                     fir_design='firwin2')
    picks_meg = mne.pick_types(raw.info, meg=True, ref_meg=False, eeg=False,
                               eog=False, ecg=False, stim=False, exclude='bads')
    # running ICA/manual IC selection or load it
    dn_meg = "/mnt/data/MEG_pitch/data/fs+mne/" + subj + "/meg"
    if not os.path.isdir(dn_meg):
        # os.mkdir(dn_meg)
        os.makedirs(dn_meg)  # recurvise directory creation
    prefix = dn_meg + "/run%i_" % iRun + suffix_filt
    fn_ica = prefix + "_tsss_ica.fif"
    if not os.path.isfile(fn_ica):
        ica = mne.preprocessing.ICA(n_components=40, method='fastica',
                                    random_state=23)
        ica.fit(raw, picks=picks_meg, decim=3, reject=dict(mag=5e-12))
        ica.plot_components(show=False)
        plt.figure(1)
        mgnr = plt.get_current_fig_manager()
        mgnr.window.setGeometry(440, 52, 640, 642)
    
        plt.figure(2)
        mgnr = plt.get_current_fig_manager()
        mgnr.window.setGeometry(440, 52 + 650, 640, 642)
    
        ica.plot_sources(raw, picks=range(40), stop=60, show=False)
        mgnr = plt.get_current_fig_manager()
        mgnr.window.setGeometry(1117, 626, 1883, 1056)
        plt.draw_all()
        plt.pause(0.001)
        plt.show(block=True)
        # ======================================================================
        #   MANUAL IDENTIFICATION: selection using GUI (mark ECG/EOG ICs RED)  #
        # ======================================================================
        ica.exclude
        ica.save(fn_ica)
    else:
        ica = mne.preprocessing.read_ica(fn_ica)

    ica.apply(raw)  # exclude marked components
    raw.save(fname=prefix + "_cor_raw_tsss.fif")
    return

##
df = pd.read_excel(
    "/mnt/data/MEG_pitch/data/rawdata/MEGStudy/Subjects.xlsx",
    sheet_name="rawdata")
fnames_meg = [df.meg1.tolist(), df.meg2.tolist(), df.meg3.tolist()]
subj_womri = df.SubjectID[
    (df.hasmri == False) & (df.goodmeg_for_tsss == True)
    ] # subjects without MRI
for subj, iSubj in zip(subj_womri, subj_womri.index):
    dn_meg = "/mnt/data/MEG_pitch/data/fs+mne/" + subj + "/meg"
    suffix_filt = "hp0.5Hz_notch50sHz"
    dest = get_dest() # destination for tsss
    for iRun in range(3):
        fn_tsss = dn_meg + "/run%i_" % iRun + suffix_filt + "_cor_raw_tsss.fif"
        if not os.path.isfile(fn_tsss):
            maxfilt_and_ica(dest)

##

