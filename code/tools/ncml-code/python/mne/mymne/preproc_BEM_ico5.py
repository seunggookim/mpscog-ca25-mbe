# REF: mne cookbook.html
# Setting up the source space
import matplotlib.pyplot as mp
import mne, os, shutil

def make_bem(subj):
    import matplotlib.pyplot as mp
    import mne, os, shutil
    fsdir = "/mnt/data/MEG_pitch/data/fs+mne"
    mne.set_config("SUBJECTS_DIR", fsdir)
    
    os.chdir(fsdir + "/" + subj + "/bem")
    # 1. mesh models using freesurfer watershed
    fn_out = subj + "-head.fif"
    if not os.path.isfile(fn_out):
        mne.set_config('FREESURFER_HOME', '/usr/local/freesurfer/')
        mne.bem.make_watershed_bem(subject=subj, overwrite=True, show=True,
                                   verbose=True)
        mp.savefig(subj + "surfs.png")
        mp.close()
    
    os.chdir(os.path.join(fsdir, subj, "bem"))
    # 2. decimation of white surface
    fn_out = subj + "-10242-src.fif"
    if not os.path.isfile(fn_out):
        src = mne.setup_source_space(subj, spacing="ico5")
        mne.write_source_spaces(fn_out, src)  # save it
    
    # 3. Boundary element model (BEM): 1-layer for MEG
    fn_out = subj + "-10242-1layer-bem.fif"
    if not os.path.isfile(fn_out):
        # topology check & creating BEM
        model = mne.make_bem_model(subj, conductivity=[0.3])
        mne.write_bem_surfaces(fn_out, model)
        
    # 4. BEM solution
    fn_bem = subj + "-10242-1layer-bem-sol.fif"
    if not os.path.isfile(fn_bem):
        fn_model = subj + "-10242-1layer-bem.fif"
        model = mne.read_bem_surfaces(fn_model)
        bem = mne.make_bem_solution(model)
        mne.write_bem_solution(fn_bem, bem)

# now batch:
from joblib import Parallel, delayed
S = [1, 2, 4, 5, 7,   8, 10, 13, 15, 16,   18, 19, 20]
SUBJ = ["S%02i" % (s) for s in S]
Parallel(n_jobs=13)(delayed(make_bem)(subj) for subj in SUBJ)
# [make_bem(subj) for subj in SUBJ]  # just run them serially

'''
# check surface models:
mne.viz.plot_bem(subject=subj, subjects_dir=fsdir,
                 brain_surfaces='white', orientation='coronal')
mp.savefig("surfs.png")
mp.close()
'''
