import mne, os, pandas as pd, numpy as np, matplotlib.pyplot as plt, time


def viz_stc_fs(stc, title, prefix_png, views=['fro'],
               clim=dict(kind='value', lims=(3, 9, 20))):
    # visualize source distribution at peak:
    for hemi in ('lh', 'rh'):
        if not os.path.isfile(prefix_png + "-" + hemi + ".stc.png"):
            # vertno_max, time_max = stc.get_peak(hemi=hemi, tmin=0.050, tmax=0.200)
            vertno_max, time_max = stc.get_peak(hemi=hemi)
            brain = stc.plot(
                subject='fsaverage', surface='inflated', hemi=hemi, time_viewer=False,
                initial_time=time_max, clim=clim,
                transparent=True, backend='mayavi', views=views, size=400
            )
            brain.brain_matrix[0][0]._f.children[1].children[0]. \
                children[0].children[0].actor.actor.force_opaque = True
            brain.add_foci(vertno_max, coords_as_verts=True, hemi=hemi,
                           color='blue', scale_factor=0.6, alpha=0.8)
            brain.add_text(.1, .9, title, 'title', font_size=16)
            brain.save_single_image(prefix_png + "-" + hemi + ".stc.png")
            brain.close()
    return


# def viz_stc_fs_mean(stc, title, prefix_png, tmin, tmax):
#     stc_mean = stc.copy().crop(tmin=tmin, tmax=tmax).mean()
#     # visualize source distribution at peak:
#     for hemi in ('lh', 'rh'):
#         if not os.path.isfile(prefix_png + "-" + hemi + ".stc.png"):
#             # vertno_max, time_max = stc.get_peak(hemi=hemi, tmin=0.050, tmax=0.200)
#             vertno_max, time_max = stc.get_peak(hemi=hemi)
#             brain = stc_mean.plot(
#                 subject='fsaverage', surface='inflated', hemi=hemi, time_viewer=False,
#                 initial_time=time_max, # clim=dict(kind='value', lims=(3, 9, 20)
#                 transparent=True, backend='mayavi', views=['fro'], size=400
#             )
#             brain.brain_matrix[0][0]._f.children[1].children[0]. \
#                 children[0].children[0].actor.actor.force_opaque = True
#             brain.add_foci(vertno_max, coords_as_verts=True, hemi=hemi,
#                            color='blue', scale_factor=0.6, alpha=0.8)
#             brain.add_text(.1, .9, title, 'title', font_size=16)
#             brain.save_single_image(prefix_png + "-" + hemi + ".stc.png")
#             brain.close()
#     return

def viz_stc_fs_mean(stc, title, fn_png, tmin, tmax, lims=None):
    stc_mean = stc.copy().crop(tmin=tmin, tmax=tmax).mean()
    time_label = '%s t=%%d ms' % title
    brain = stc_mean.plot(
        subject='fsaverage', surface='inflated', hemi='both', time_viewer=False,
        initial_time=0, clim=dict(kind='value', lims=lims), time_label=time_label,
        time_unit='ms',
        transparent=True, backend='mayavi', views=['lat'], size=400
    )
    # brain.brain_matrix[0][0]._f.children[1].children[0]. \
    #     children[0].children[0].actor.actor.force_opaque = True
    # for hemi in ['lh','rh']:
    #     vertno_max, time_max = stc.get_peak(hemi=hemi, tmin=tmin, tmax=tmax)
    #     brain.add_foci(vertno_max, coords_as_verts=True, hemi=hemi,
    #                    color='blue', scale_factor=0.6, alpha=0.8)
    # brain.add_text(.1, .9, title, 'title', font_size=16)
    # brain.save_single_image(prefix_png + "-" + hemi + ".stc.png")
    brain.save_montage(filename=fn_png, order=['med', 'lat'],
                      orientation='h', border_size=5)
    brain.close()
    return

def labels_roi3():
    roi_names = ['G_temp_sup-G_T_transv', 'S_temporal_transverse',
                 'G_temp_sup-Plan_tempo', 'G_temp_sup-Lateral', 'S_temporal_sup']
    labels_5rois = [mne.read_labels_from_annot(
        'fsaverage', parc='aparc.a2009s', regexp=roi, verbose=False)
        for roi in roi_names]
    labels = list(range(6))
    labels[0] = labels_5rois[0][0].__add__(labels_5rois[1][0])
    labels[0].name = 'HG-lh'
    labels[1] = labels_5rois[0][1].__add__(labels_5rois[1][1])
    labels[1].name = 'HG-rh'
    labels[2] = labels_5rois[2][0]
    labels[2].name = 'PT-lh'
    labels[3] = labels_5rois[2][1]
    labels[3].name = 'PT-rh'
    labels[4] = labels_5rois[3][0]
    labels[4].name = 'STG-lh'
    labels[5] = labels_5rois[3][1]
    labels[5].name = 'STG-rh'

    return labels


def labels_roi4():
    roi_names = ['G_temp_sup-G_T_transv', 'S_temporal_transverse',
                 'G_temp_sup-Plan_tempo', 'G_temp_sup-Lateral', 'S_temporal_sup']
    labels_5rois = [mne.read_labels_from_annot(
        'fsaverage', parc='aparc.a2009s', regexp=roi, verbose=False)
        for roi in roi_names]
    labels = list(range(8))
    labels[0] = labels_5rois[0][0].__add__(labels_5rois[1][0])
    labels[0].name = 'HG-lh'
    labels[1] = labels_5rois[0][1].__add__(labels_5rois[1][1])
    labels[1].name = 'HG-rh'
    labels[2] = labels_5rois[2][0]
    labels[2].name = 'PT-lh'
    labels[3] = labels_5rois[2][1]
    labels[3].name = 'PT-rh'
    labels[4] = labels_5rois[3][0]
    labels[4].name = 'STG-lh'
    labels[5] = labels_5rois[3][1]
    labels[5].name = 'STG-rh'
    labels[6] = labels_5rois[4][0]
    labels[6].name = 'STS-lh'
    labels[7] = labels_5rois[4][1]
    labels[7].name = 'STS-rh'
    return labels


def viz_stc(stc, subject='fsaverage', surface='inflated',hemi='rh',
            time_viewer=False, initial_time=0, clim='auto', views=['lat']):
    brain = mne.viz.plot_source_estimates(stc,
        subject=subject, surface=surface, hemi=hemi, time_viewer=time_viewer,
        initial_time=initial_time, clim=clim,
        transparent=True, backend='mayavi', views=views, size=400
    )
    brain.brain_matrix[0][0]._f.children[1].children[0]. \
        children[0].children[0].actor.actor.force_opaque = True
    return brain


def viz_stc_contour_roi4(stc, initial_time, lims, prefix_png):
    labels = labels_roi4()
    
    lh = viz_stc(stc, initial_time=initial_time, hemi="lh", views=['lat'],
                       clim=dict(kind='value', lims=lims))
    [lh.add_label(labels[i], borders=True, color='black') for i in range(0, 8, 2)]
    # for i in range(4):
    #     lh.brain_matrix[0][0]._f.children[2 + i].children[0].children[0].children[0]. \
    #         actor.actor.force_opaque = True
    # lh.brain_matrix[0][0]._f.children[2].children[0]
    # time.sleep(3)
    lh.save_single_image(prefix_png + "-lh.stc.png")
    lh.close()
    
    rh = viz_stc(stc, initial_time=initial_time, hemi="rh", views=['lat'],
                       clim=dict(kind='value', lims=lims))
    [rh.add_label(labels[i], borders=True, color='black') for i in range(1, 8, 2)]
    # for i in range(4):
    #     rh.brain_matrix[0][0]._f.children[2 + i].children[0].children[0].children[0]. \
    #         actor.actor.force_opaque = True
    # time.sleep(3)
    rh.save_single_image(prefix_png + "-rh.stc.png")
    rh.close()


def viz_stc_contour_roi3(stc, initial_time, lims, prefix_png):
    labels = labels_roi3()
    
    lh = viz_stc(stc, initial_time=initial_time, hemi="lh", views=['lat'],
                 clim=dict(kind='value', lims=lims))
    [lh.add_label(labels[i], borders=True, color='black') for i in range(0, 6, 2)]
    # for i in range(3):
    #     lh.brain_matrix[0][0]._f.children[2 + i].children[0].children[0]\
    #         .children[0].actor.actor.force_opaque = True
    # time.sleep(len(labels))
    lh.save_single_image(prefix_png + "-lh.stc.png")
    
    
    rh = viz_stc(stc, initial_time=initial_time, hemi="rh", views=['lat'],
                 clim=dict(kind='value', lims=lims))
    [ rh.add_label(labels[i], borders=True, color='blacx') for i in range(1, 6, 2)]
    # for i in range(3):
    #     rh.brain_matrix[0][0]._f.children[2 + i].children[0].children[0]\
    #         .children[0].actor.actor.force_opaque = True
    # time.sleep(3)
    rh.save_single_image(prefix_png + "-rh.stc.png")
    
    return lh, rh


def get_spatial_exclude_from_rois(rois, parc, src):
    """
    spatial_exclude = get_spatial_exclude_from_rois(rois, parc, src):
    
    :param rois: list of strings eg. ['transversetemporal', 'superiortemporal']
    :param parc: string eg. 'aparc'
    :param src:  mne source space object (from mne.read_source_spaces)
    :return spatial_exclude: list of integers (vertno)
            spatial_include: list of integers (vertno)
    """

    labels = [mne.read_labels_from_annot(
        subject='fsaverage5', parc=parc, verbose=True, regexp=roi) for roi in rois]
    """
    68/48 'transversetemporal'
    442/429 'superiortemporal'
    """
    vertno = [s['vertno'] for s in src]  # vertex number 0, ..., 10241 (in the source, in this case ico5)
    nverts = [len(vn) for vn in vertno]
    # spatial_exclude = np.arange(0, sum(nverts))
    spatial_include = list()
    for label in labels:
        for hemi, vertno1 in zip(label, vertno):

            if hemi.hemi == 'lh':
                verts = hemi.vertices
            elif hemi.hemi == 'rh':
                verts = hemi.vertices + nverts[0]
            spatial_include.extend(verts.tolist())

    spatial_exclude = np.setdiff1d(np.arange(0, sum(nverts)), np.asarray(spatial_include)).tolist()
    print("%i vertices excluded." %(len(spatial_exclude)))
    return spatial_exclude, spatial_include