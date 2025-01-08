import scipy.io, mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt


def get_headpos_raw():
    dn_raw = "/mnt/data/MEG_pitch/data/rawdata/MEGStudy/Originals/" \
             + fnames_meg[iRun][iSubj]
    raw = mne.io.read_raw_ctf(dn_raw, preload=False)
    chpi_locs = mne.chpi.extract_chpi_locs_ctf(raw)
    head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs, gof_limit=0.98)
    return head_pos, raw


def get_headpos_tsss():
    dn_meg = "/mnt/data/MEG_pitch/data/fs+mne/" + subj + "/meg"
    prefix = dn_meg + "/run%i_" % iRun + "hp0.5Hz_notch50sHz"
    fn_raw = prefix + "_cor_raw_tsss.fif"
    raw = mne.io.read_raw_fif(fn_raw, preload=False)
    chpi_locs = mne.chpi.extract_chpi_locs_ctf(raw)
    head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs, gof_limit=0.98)
    return head_pos, raw


dframe = pd.read_excel(
    "/mnt/data/MEG_pitch/data/rawdata/MEGStudy/Subjects.xlsx",
    sheet_name="rawdata")
fnames_meg = [dframe.meg1.tolist(), dframe.meg2.tolist(), dframe.meg3.tolist()]
subjects = dframe.SubjectID.tolist()

# np.ndarray([12,3,3]) * np.nan

iSubj = 0
for subid in (0, 1, 3, 4, 6, 7, 12, 14, 15, 17, 18, 19):  # subjects with MRI
    subj = subjects[subid]
    dn_meg = "/mnt/data/MEG_pitch/data/fs+mne/" + subj + "/meg"
    for iRun in range(3):
        head_pos, raw = get_headpos_raw()
        scipy.io.savemat(
            '/mnt/data/MEG_pitch/data/fs+mne/fsaverage/meg/headpos/headpos_raw_' + subj + 'run%i.mat' % iRun,
            dict(dev_head_t=raw.info['dev_head_t'],
                 head_pos=dict(head_pos=head_pos,
                               info='[t, {q1, q2, q3, x, y, z}=quaterion, gof, err, v [m/s]] for each fit in meter .')),
            do_compression=True)
        
        head_pos2, raw2 = get_headpos_tsss()
        scipy.io.savemat(
            '/mnt/data/MEG_pitch/data/fs+mne/fsaverage/meg/headpos/headpos_tsss_' + subj + 'run%i.mat' % iRun,
            dict(dev_head_t=raw2.info['dev_head_t'],
                 head_pos=dict(head_pos=head_pos2,
                               info='[t, {q1, q2, q3, x, y, z}=quaterion, gof, err, v [m/s]] for each fit in meter .')),
            do_compression=True)
    iSubj += 1
