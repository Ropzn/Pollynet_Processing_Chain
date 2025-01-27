import os
import sys
import scipy.io as spio
import numpy as np
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.colors import ListedColormap
from matplotlib.dates import DateFormatter, DayLocator, HourLocator, \
    MinuteLocator, date2num
plt.switch_backend('Agg')


def celltolist(xtickstr):
    """
    convert list of list to list of string.

    Examples
    --------

    [['2010-10-11'], [], ['2011-10-12]] =>
    ['2010-10-11], '', '2011-10-12']
    """

    tmp = []
    for iElement in range(0, len(xtickstr)):
        if not len(xtickstr[iElement][0]):
            tmp.append('')
        else:
            tmp.append(xtickstr[iElement][0][0])

    return tmp


def datenum_to_datetime(datenum):
    """
    Convert Matlab datenum into Python datetime.

    Parameters
    ----------
    Date: float

    Returns
    -------
    dtObj: datetime object

    """
    days = datenum % 1
    hours = days % 1 * 24
    minutes = hours % 1 * 60
    seconds = minutes % 1 * 60

    dtObj = datetime.fromordinal(int(datenum)) + \
        timedelta(days=int(days)) + \
        timedelta(hours=int(hours)) + \
        timedelta(minutes=int(minutes)) + \
        timedelta(seconds=round(seconds)) - timedelta(days=366)

    return dtObj


def rmext(filename):
    """
    remove the file extension.

    Parameters
    ----------
    filename: str
    """

    file, _ = os.path.splitext(filename)
    return file


def pollyxt_ift_display_quasiretrieving(tmpFile, saveFolder):
    '''
    Description
    -----------
    Display the housekeeping data from laserlogbook file.

    Parameters
    ----------
    tmpFile: str
    the .mat file which stores the housekeeping data.

    saveFolder: str

    Usage
    -----
    pollyxt_ift_display_quasiretrieving(tmpFile, saveFolder)

    History
    -------
    2019-01-10. First edition by Zhenping
    '''

    if not os.path.exists(tmpFile):
        print('{filename} does not exists.'.format(filename=tmpFile))
        return

    # read matlab .mat data
    try:
        mat = spio.loadmat(tmpFile, struct_as_record=True)
        figDPI = mat['figDPI'][0][0]
        quasi_bsc_532 = mat['quasi_bsc_532'][:]
        quality_mask_532 = mat['quality_mask_532'][:]
        quasi_bsc_355 = mat['quasi_bsc_355'][:]
        quality_mask_355 = mat['quality_mask_355'][:]
        quasi_bsc_1064 = mat['quasi_bsc_1064'][:]
        quality_mask_1064 = mat['quality_mask_1064'][:]
        quasi_pardepol_532 = mat['quasi_pardepol_532'][:]
        quasi_ang_532_1064 = mat['quasi_ang_532_1064'][:]
        height = mat['height'][0][:]
        time = mat['time'][0][:]
        yLim_Quasi_Params = mat['yLim_Quasi_Params'][:][0]
        quasi_beta_cRange_355 = mat['quasi_beta_cRange_355'][0][:]
        quasi_beta_cRange_532 = mat['quasi_beta_cRange_532'][0][:]
        quasi_beta_cRange_1064 = mat['quasi_beta_cRange_1064'][0][:]
        quasi_Par_DR_cRange_532 = mat['quasi_Par_DR_cRange_532'][0][:]
        pollyVersion = mat['campaignInfo']['name'][0][0][0]
        location = mat['campaignInfo']['location'][0][0][0]
        version = mat['processInfo']['programVersion'][0][0][0]
        fontname = mat['processInfo']['fontname'][0][0][0]
        dataFilename = mat['taskInfo']['dataFilename'][0][0][0]
        xtick = mat['xtick'][0][:]
        xticklabel = mat['xtickstr']
        imgFormat = mat['imgFormat'][:][0]
    except Exception as e:
        print(e)
        print('Failed reading %s' % (tmpFile))
        return

    # set the default font
    matplotlib.rcParams['font.sans-serif'] = fontname
    matplotlib.rcParams['font.family'] = "sans-serif"

    # meshgrid
    Time, Height = np.meshgrid(time, height)
    quasi_bsc_355 = np.ma.masked_where(quality_mask_355 > 0, quasi_bsc_355)
    quasi_bsc_532 = np.ma.masked_where(quality_mask_532 > 0, quasi_bsc_532)
    quasi_bsc_1064 = np.ma.masked_where(quality_mask_1064 > 0, quasi_bsc_1064)
    quasi_pardepol_532 = np.ma.masked_where(
        quality_mask_532 > 0,
        quasi_pardepol_532
    )
    quasi_ang_532_1064 = np.ma.masked_where(
        np.logical_or(quality_mask_532 > 0, quality_mask_1064 > 0),
        quasi_ang_532_1064
    )

    # define the colormap
    cmap = plt.cm.jet
    cmap.set_bad('k', alpha=1)
    cmap.set_over('w', alpha=1)
    cmap.set_under('k', alpha=1)

    # display quasi backscatter at 355 nm
    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_axes([0.11, 0.15, 0.79, 0.75])
    pcmesh = ax.pcolormesh(
        Time, Height, quasi_bsc_355 * 1e6,
        vmin=quasi_beta_cRange_355[0],
        vmax=quasi_beta_cRange_355[1],
        cmap=cmap,
        rasterized=True
        )
    ax.set_xlabel('UTC', fontsize=15)
    ax.set_ylabel('Height (m)', fontsize=15)

    ax.yaxis.set_major_locator(MultipleLocator(2000))
    ax.yaxis.set_minor_locator(MultipleLocator(500))
    ax.set_ylim(yLim_Quasi_Params.tolist())
    ax.set_xticks(xtick.tolist())
    ax.set_xticklabels(celltolist(xticklabel))
    ax.tick_params(axis='both', which='major', labelsize=15,
                   right=True, top=True, width=2, length=5)
    ax.tick_params(axis='both', which='minor', width=1.5,
                   length=3.5, right=True, top=True)

    ax.set_title(
        'Quasi backscatter coefficient at {wave}nm'.format(wave=355) +
        ' from {instrument} at {location}'.format(
            instrument=pollyVersion,
            location=location
            ),
        fontsize=15
        )

    cb_ax = fig.add_axes([0.94, 0.20, 0.02, 0.65])
    cbar = fig.colorbar(
        pcmesh, cax=cb_ax, ticks=np.linspace(
            quasi_beta_cRange_355[0],
            quasi_beta_cRange_355[1],
            5
            ),
        orientation='vertical'
        )
    cbar.ax.tick_params(direction='in', labelsize=15, pad=5)
    cbar.ax.set_title('$Mm^{-1}*sr^{-1}$', fontsize=12)

    fig.text(0.05, 0.02, datenum_to_datetime(
        time[0]).strftime("%Y-%m-%d"), fontsize=12)
    fig.text(0.8, 0.02, 'Version: {version}'.format(
        version=version), fontsize=12)

    fig.savefig(os.path.join(
        saveFolder, '{dataFilename}_Quasi_Bsc_355.{imgFormat}'.format(
            dataFilename=rmext(dataFilename),
            imgFormat=imgFormat
            )), dpi=figDPI)
    plt.close()

    # display quasi backscatter at 532 nm
    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_axes([0.11, 0.15, 0.79, 0.75])
    pcmesh = ax.pcolormesh(
        Time, Height, quasi_bsc_532 * 1e6,
        vmin=quasi_beta_cRange_532[0],
        vmax=quasi_beta_cRange_532[1],
        cmap=cmap,
        rasterized=True
        )
    ax.set_xlabel('UTC', fontsize=15)
    ax.set_ylabel('Height (m)', fontsize=15)

    ax.yaxis.set_major_locator(MultipleLocator(2000))
    ax.yaxis.set_minor_locator(MultipleLocator(500))
    ax.set_ylim(yLim_Quasi_Params.tolist())
    ax.set_xticks(xtick.tolist())
    ax.set_xticklabels(celltolist(xticklabel))
    ax.tick_params(axis='both', which='major', labelsize=15,
                   right=True, top=True, width=2, length=5)
    ax.tick_params(axis='both', which='minor', width=1.5,
                   length=3.5, right=True, top=True)

    ax.set_title(
        'Quasi backscatter coefficient at {wave}nm'.format(wave=532) +
        ' from {instrument} at {location}'.format(
            instrument=pollyVersion,
            location=location
            ),
        fontsize=15
        )

    cb_ax = fig.add_axes([0.94, 0.20, 0.02, 0.65])
    cbar = fig.colorbar(
        pcmesh, cax=cb_ax, ticks=np.linspace(
            quasi_beta_cRange_532[0],
            quasi_beta_cRange_532[1],
            5
            ),
        orientation='vertical'
        )
    cbar.ax.tick_params(direction='in', labelsize=15, pad=5)
    cbar.ax.set_title('$Mm^{-1}*sr^{-1}$', fontsize=12)

    fig.text(0.05, 0.02, datenum_to_datetime(
        time[0]).strftime("%Y-%m-%d"), fontsize=12)
    fig.text(0.8, 0.02, 'Version: {version}'.format(
        version=version), fontsize=12)

    fig.savefig(os.path.join(
        saveFolder, '{dataFilename}_Quasi_Bsc_532.{imgFormat}'.format(
            dataFilename=rmext(dataFilename),
            imgFormat=imgFormat
        )), dpi=figDPI)
    plt.close()

    # display quasi backscatter at 1064 nm
    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_axes([0.11, 0.15, 0.79, 0.75])
    pcmesh = ax.pcolormesh(
        Time, Height, quasi_bsc_1064 * 1e6,
        vmin=quasi_beta_cRange_1064[0],
        vmax=quasi_beta_cRange_1064[1],
        cmap=cmap,
        rasterized=True
        )
    ax.set_xlabel('UTC', fontsize=15)
    ax.set_ylabel('Height (m)', fontsize=15)

    ax.yaxis.set_major_locator(MultipleLocator(2000))
    ax.yaxis.set_minor_locator(MultipleLocator(500))
    ax.set_ylim(yLim_Quasi_Params.tolist())
    ax.set_xticks(xtick.tolist())
    ax.set_xticklabels(celltolist(xticklabel))
    ax.tick_params(axis='both', which='major', labelsize=15,
                   right=True, top=True, width=2, length=5)
    ax.tick_params(axis='both', which='minor', width=1.5,
                   length=3.5, right=True, top=True)

    ax.set_title(
        'Quasi backscatter coefficient at {wave}nm'.format(wave=1064) +
        ' from {instrument} at {location}'.format(
            instrument=pollyVersion,
            location=location
            ),
        fontsize=15
        )

    cb_ax = fig.add_axes([0.94, 0.20, 0.02, 0.65])
    cbar = fig.colorbar(
        pcmesh, cax=cb_ax, ticks=np.linspace(
            quasi_beta_cRange_1064[0],
            quasi_beta_cRange_1064[1],
            5
            ),
        orientation='vertical'
        )
    cbar.ax.tick_params(direction='in', labelsize=15, pad=5)
    cbar.ax.set_title('$Mm^{-1}*sr^{-1}$', fontsize=12)

    fig.text(0.05, 0.02, datenum_to_datetime(
        time[0]).strftime("%Y-%m-%d"), fontsize=12)
    fig.text(0.8, 0.02, 'Version: {version}'.format(
        version=version), fontsize=12)

    fig.savefig(os.path.join(
        saveFolder, '{dataFilename}_Quasi_Bsc_1064.{imgFormat}'.format(
            dataFilename=rmext(dataFilename),
            imgFormat=imgFormat
        )), dpi=figDPI)
    plt.close()

    # display quasi particle depolarization ratio at 532 nm
    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_axes([0.11, 0.15, 0.79, 0.75])
    pcmesh = ax.pcolormesh(
        Time, Height, quasi_pardepol_532,
        vmin=quasi_Par_DR_cRange_532[0],
        vmax=quasi_Par_DR_cRange_532[1],
        cmap=cmap,
        rasterized=True
        )
    ax.set_xlabel('UTC', fontsize=15)
    ax.set_ylabel('Height (m)', fontsize=15)

    ax.yaxis.set_major_locator(MultipleLocator(2000))
    ax.yaxis.set_minor_locator(MultipleLocator(500))
    ax.set_ylim(yLim_Quasi_Params.tolist())
    ax.set_xticks(xtick.tolist())
    ax.set_xticklabels(celltolist(xticklabel))
    ax.tick_params(axis='both', which='major', labelsize=15,
                   right=True, top=True, width=2, length=5)
    ax.tick_params(axis='both', which='minor', width=1.5,
                   length=3.5, right=True, top=True)

    ax.set_title(
        'Quasi particle depolarization ratio at 532nm ' +
        'from {instrument} at {location}'.format(
            instrument=pollyVersion,
            location=location
            ),
        fontsize=15
        )

    cb_ax = fig.add_axes([0.92, 0.20, 0.02, 0.65])
    cbar = fig.colorbar(pcmesh, cax=cb_ax, ticks=np.arange(
        0, 0.41, 0.05), orientation='vertical')
    cbar.ax.tick_params(direction='in', labelsize=15, pad=5)
    cbar.ax.set_title('', fontsize=12)

    fig.text(0.05, 0.02, datenum_to_datetime(
        time[0]).strftime("%Y-%m-%d"), fontsize=12)
    fig.text(0.8, 0.02, 'Version: {version}'.format(
        version=version), fontsize=12)

    fig.savefig(os.path.join(
        saveFolder, '{dataFilename}_Quasi_PDR_532.{imgFormat}'.format(
            dataFilename=rmext(dataFilename),
            imgFormat=imgFormat
        )), dpi=figDPI)
    plt.close()

    # display quasi angtroem exponent 532-1064
    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_axes([0.11, 0.15, 0.79, 0.75])
    pcmesh = ax.pcolormesh(
        Time, Height, quasi_ang_532_1064, vmin=0, vmax=2, cmap=cmap,
        rasterized=True)
    ax.set_xlabel('UTC', fontsize=15)
    ax.set_ylabel('Height (m)', fontsize=15)

    ax.yaxis.set_major_locator(MultipleLocator(2000))
    ax.yaxis.set_minor_locator(MultipleLocator(500))
    ax.set_ylim(yLim_Quasi_Params.tolist())
    ax.set_xticks(xtick.tolist())
    ax.set_xticklabels(celltolist(xticklabel))
    ax.tick_params(axis='both', which='major', labelsize=15,
                   right=True, top=True, width=2, length=5)
    ax.tick_params(axis='both', which='minor', width=1.5,
                   length=3.5, right=True, top=True)

    ax.set_title(
        'Quasi BSC Angstoem Exponent 532-1064 ' +
        'from {instrument} at {location}'.format(
            instrument=pollyVersion,
            location=location
            ),
        fontsize=15
        )

    cb_ax = fig.add_axes([0.92, 0.20, 0.02, 0.65])
    cbar = fig.colorbar(pcmesh, cax=cb_ax, ticks=np.arange(
        0, 2.1, 0.5), orientation='vertical')
    cbar.ax.tick_params(direction='in', labelsize=15, pad=5)
    cbar.ax.set_title('', fontsize=12)

    fig.text(0.05, 0.02, datenum_to_datetime(
        time[0]).strftime("%Y-%m-%d"), fontsize=12)
    fig.text(0.8, 0.02, 'Version: {version}'.format(
        version=version), fontsize=12)

    fig.savefig(os.path.join(
        saveFolder, '{dataFilename}_Quasi_ANGEXP_532_1064.{imgFormat}'.format(
            dataFilename=rmext(dataFilename),
            imgFormat=imgFormat
            )), dpi=figDPI)
    plt.close()


def main():
    pollyxt_ift_display_quasiretrieving(
        'C:\\Users\\zhenping\\Desktop\\Picasso\\tmp\\tmp.mat',
        'C:\\Users\\zhenping\\Desktop'
        )


if __name__ == '__main__':
    # main()
    pollyxt_ift_display_quasiretrieving(sys.argv[1], sys.argv[2])
