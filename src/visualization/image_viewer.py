import copy
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.widgets import Button
import nrrd

# View the CT scan side-by-side with the dose overlaid on top.
# the --image and --dose arguments are required.
# You can specify an optional mask file that will be shown on top
# of the CT but below the dose.
#
# usage: view_ct_and_dose.py [-h] [--dose DOSE] [--masks [MASKS [MASKS ...]]]
#                            [--dose_cmap DOSE_CMAP] [--dose_alpha DOSE_ALPHA]
#                            [--mask_alpha MASK_ALPHA]
#                            image
#
# positional arguments:
#   image                 image filename
#
#  optional arguments:
#    -h, --help            show this help message and exit
#   --dose DOSE           dose filename
#   --masks [MASKS [MASKS ...]]
#                        mask filename
#   --dose_cmap DOSE_CMAP
#                         colormap to use for dose
#   --dose_alpha DOSE_ALPHA
#                         dose alpha
#   --mask_alpha MASK_ALPHA
#                         mask alpha

def redraw(i,j,k):
    axs[0].imshow(ct[:, :, i], cmap='bone')
    axs[1].imshow(ct[:, j, :], cmap='bone')
    axs[4].imshow(ct[k, :, :].T, cmap='bone', origin='lower')

    axs[2].imshow(ct[:, :, i], cmap='bone')
    axs[3].imshow(ct[:, j, :], cmap='bone')
    axs[6].imshow(ct[k, :, :].T, cmap='bone', origin='lower')

    if args.masks is not None:
        mask_maxv = len(args.masks)
        for n in range(len(args.masks)):
            axs[2].imshow(masks[n][:, :, i],   cmap=mask_cmap, alpha=mask_alpha, vmin=0, vmax=mask_maxv)
            axs[3].imshow(masks[n][:, j, :],   cmap=mask_cmap, alpha=mask_alpha, vmin=0, vmax=mask_maxv)
            axs[6].imshow(masks[n][k, :, :].T, cmap=mask_cmap, alpha=mask_alpha, vmin=0, vmax=mask_maxv, origin='lower')

    if args.dose is not None:
        # This will use the range in the entire dose image to set max/min for the colormap
        axs[2].imshow(dose[:, :, i], cmap=dose_cmap, vmin=dose_minv, vmax=dose_maxv, alpha=dose_alpha)
        axs[3].imshow(dose[:, j, :], cmap=dose_cmap, vmin=dose_minv, vmax=dose_maxv, alpha=dose_alpha)
        axs[6].imshow(dose[k, :, :].T, cmap=dose_cmap, vmin=dose_minv, vmax=dose_maxv, alpha=dose_alpha, origin='lower')

        # # This will use the range in this slice to set max/min for the colormap
        # axs[2].imshow(dose[:, :, i], cmap=dose_cmap, alpha=dose_alpha)
        # axs[3].imshow(dose[:, j, :], cmap=dose_cmap, alpha=dose_alpha)
        # axs[6].imshow(dose[k, :, :].T, cmap=dose_cmap, alpha=dose_alpha, origin='lower')

    axs[0].set_aspect(1.171875/1.171875)
    axs[1].set_aspect(1.171875/3.000000)
    axs[4].set_aspect(3.000000/1.171875)
    axs[2].set_aspect(1.171875/1.171875)
    axs[3].set_aspect(1.171875/3.000000)
    axs[6].set_aspect(3.000000/1.171875)

def updateFromSlider(val):
    i = int(axialSlider.val)
    j = int(sagittalSlider.val)
    k = int(coronalSlider.val)
    redraw(i,j,k)

def updateFromAxialUpButton(val):
    i = int(axialSlider.val)
    axialSlider.set_val(i+1)

def updateFromSagittalUpButton(val):
    i = int(sagittalSlider.val)
    sagittalSlider.set_val(i+1)

def updateFromCoronalUpButton(val):
    i = int(coronalSlider.val)
    coronalSlider.set_val(i+1)

def updateFromAxialDownButton(val):
    i = int(axialSlider.val)
    axialSlider.set_val(i-1)

def updateFromSagittalDownButton(val):
    i = int(sagittalSlider.val)
    sagittalSlider.set_val(i-1)

def updateFromCoronalDownButton(val):
    i = int(coronalSlider.val)
    coronalSlider.set_val(i-1)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=str, help='image filename')
    parser.add_argument('--dose', type=str, help='dose filename')
    parser.add_argument('--masks', type=str, help='mask filename', nargs='*')
    parser.add_argument('--dose_cmap', type=str, help='colormap to use for dose')
    parser.add_argument('--dose_alpha', type=float, help='dose alpha')
    parser.add_argument('--mask_alpha', type=float, help='mask alpha')
    args = parser.parse_args()

    plt.style.use('dark_background')

    if args.dose_cmap is not None:
        dose_cmap = args.dose_cmap
    else:
        dose_cmap = 'magma'

    if args.dose_alpha is not None:
        dose_alpha = args.dose_alpha
    else:
        dose_alpha = 0.6

    if args.mask_alpha is not None:
        mask_alpha = args.mask_alpha
    else:
        mask_alpha = 1.0

    ct, ct_header = nrrd.read(args.image)
    ct_minv = ct.min()
    ct_maxv = ct.max()

    # Calculate central coordinate in CT for initializing display
    axialMidpoint = int(np.floor(ct.shape[2]/2))
    sagittalMidpoint = int(np.floor(ct.shape[0]/2))
    coronalMidpoint = int(np.floor(ct.shape[1]/2))

    if args.dose is not None:
        dose, dose_header = nrrd.read(args.dose)
        dose_minv = np.min(dose[np.nonzero(dose)])
        dose_maxv = dose.max()

        # dose_cmap = copy.copy(plt.cm.get_cmap(dose_cmap))
        # dose_cmap.set_bad(alpha=0)
        # dose = np.ma.masked_where(dose<dose_minv, dose)

    # Read in all the specified masks
    # I assume that each mask consists of ones and zeros.
    # To give each mask a unique color in the colormap,
    # I multiply it by the length of the mask list.
    if args.masks is not None:
        # This will hide all the voxels equal to zero in each mask
        mask_cmap = copy.copy(plt.cm.get_cmap('Set1').reversed())
        mask_cmap.set_bad(alpha=0)

        masks = []
        for m in args.masks:
            mask, mask_header = nrrd.read(m)
            mask = mask * (len(masks)+1)
            mask = np.ma.masked_where(mask<1, mask)
            masks.append(mask)

    fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8)) = plt.subplots(2,4)
    plt.axis('off')
    plt.subplots_adjust(left=0.1, bottom=0.25, top=0.95)

    axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
    axs[5].axis('off')
    axs[7].axis('off')

    redraw(axialMidpoint, sagittalMidpoint, coronalMidpoint)

    # sliders for navigation
    axcolor="lavender"
    axAxial = plt.axes([0.10, 0.15, 0.65, 0.03], facecolor=axcolor)
    axSagittal = plt.axes([0.10, 0.10, 0.65, 0.03], facecolor=axcolor)
    axCoronal = plt.axes([0.10, 0.05, 0.65, 0.03], facecolor=axcolor)

    axialSlider = Slider(axAxial, 'Axial', 0, ct.shape[2]-1, valinit=axialMidpoint, valstep=1)
    sagittalSlider = Slider(axSagittal, 'Sagittal', 0, ct.shape[0]-1, valinit=sagittalMidpoint, valstep=1)
    coronalSlider = Slider(axCoronal, 'Coronal', 0, ct.shape[1]-1, valinit=coronalMidpoint, valstep=1)

    coronalSlider.on_changed(updateFromSlider)
    sagittalSlider.on_changed(updateFromSlider)
    axialSlider.on_changed(updateFromSlider)

    # buttons for navigation
    axAxialUp = plt.axes([0.90, 0.15, 0.03, 0.03], facecolor=axcolor)
    axSagittalUp = plt.axes([0.90, 0.10, 0.03, 0.03], facecolor=axcolor)
    axCoronalUp = plt.axes([0.90, 0.05, 0.03, 0.03], facecolor=axcolor)
    axAxialDown = plt.axes([0.95, 0.15, 0.03, 0.03], facecolor=axcolor)
    axSagittalDown = plt.axes([0.95, 0.10, 0.03, 0.03], facecolor=axcolor)
    axCoronalDown = plt.axes([0.95, 0.05, 0.03, 0.03], facecolor=axcolor)

    axialUpButton = Button(axAxialUp, '+')
    sagittalUpButton = Button(axSagittalUp, '+')
    coronalUpButton = Button(axCoronalUp, '+')
    axialDownButton = Button(axAxialDown, '-')
    sagittalDownButton = Button(axSagittalDown, '-')
    coronalDownButton = Button(axCoronalDown, '-')

    axialUpButton.on_clicked(updateFromAxialUpButton)
    sagittalUpButton.on_clicked(updateFromSagittalUpButton)
    coronalUpButton.on_clicked(updateFromCoronalUpButton)
    axialDownButton.on_clicked(updateFromAxialDownButton)
    sagittalDownButton.on_clicked(updateFromSagittalDownButton)
    coronalDownButton.on_clicked(updateFromCoronalDownButton)

    plt.show()

