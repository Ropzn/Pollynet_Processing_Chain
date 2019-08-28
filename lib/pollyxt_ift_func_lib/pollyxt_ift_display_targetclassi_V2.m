function [] = pollyxt_ift_display_targetclassi_V2(data, taskInfo, config)
%pollyxt_ift_display_targetclassi_V2 display the target classification reuslts V2
%   Example:
%       [] = pollyxt_ift_display_targetclassi_V2(data, taskInfo, config)
%   Inputs:
%       data, taskInfo, config
%   Outputs:
%       
%   History:
%       2018-12-30. First Edition by Zhenping
%   Contact:
%       zhenping@tropos.de

global processInfo defaults campaignInfo

if strcmpi(processInfo.visualizationMode, 'matlab')
    %% initialization 
    fileTC = fullfile(processInfo.pic_folder, campaignInfo.name, datestr(data.mTime(1), 'yyyy'), datestr(data.mTime(1), 'mm'), datestr(data.mTime(1), 'dd'), sprintf('%s_TC_V2.png', rmext(taskInfo.dataFilename)));

    %% visualization
    load('TC_colormap.mat')

    % 355 nm FR
    figure('Units', 'Pixels', 'Position', [0, 0, 800, 400], 'Visible', 'off');

    subplot('Position', [0.1, 0.15, 0.6, 0.6]);   % mainframe

    TC_mask = double(data.tc_mask_V2);
    p1 = pcolor(data.mTime, data.height, TC_mask); hold on;
    set(p1, 'EdgeColor', 'none');
    caxis([0, 11]);
    xlim([data.mTime(1), data.mTime(end)]);
    ylim([0, 12000]);
    xlabel('UTC');
    ylabel('Height (m)');
    title(sprintf('Target Classification (V2) for %s at %s', campaignInfo.name, campaignInfo.location), 'fontweight', 'bold', 'interpreter', 'none');
    set(gca, 'Box', 'on', 'TickDir', 'out');
    set(gca, 'ytick', 0:2000:12000, 'yminortick', 'on');
    [xtick, xtickstr] = timelabellayout(data.mTime, 'HH:MM');
    set(gca, 'xtick', xtick, 'xticklabel', xtickstr);
    text(-0.04, -0.13, sprintf('%s', datestr(data.mTime(1), 'yyyy-mm-dd')), 'Units', 'Normal');
    text(0.90, -0.13, sprintf('Version %s', processInfo.programVersion), 'Units', 'Normal');

    % colorbar
    TC_TickLabels = {'No signal', ...
                    'Clean atmosphere', ...
                    'Non-typed particles/low conc.', ...
                    'Aerosol: small', ...
                    'Aerosol: large, spherical', ...
                    'Aerosol: mixture, partly non-spherical', ...
                    'Aerosol: large, non-spherical', ...
                    'Cloud: non-typed', ...
                    'Cloud: water droplets', ...
                    'Cloud: likely water droplets', ...
                    'Cloud: ice crystals', ...
                    'Cloud: likely ice crystals'};
    c = colorbar('position', [0.71, 0.15, 0.01, 0.6]); 
    colormap(TC_colormap);
    titleHandle = get(c, 'Title');
    set(titleHandle, 'string', '');
    set(c, 'TickDir', 'out', 'Box', 'on');
    set(c, 'ytick', (0.5:1:11.5)/12*11, 'yticklabel', TC_TickLabels);

    set(findall(gcf, '-property', 'fontname'), 'fontname', processInfo.fontname);

    export_fig(gcf, fileTC, '-transparent', sprintf('-r%d', processInfo.figDPI), '-painters');
    close();

elseif strcmpi(processInfo.visualizationMode, 'python')
    
    fprintf('Display the results with Python.\n');
    pyFolder = fileparts(mfilename('fullpath'));   % folder of the python scripts for data visualization
    tmpFolder = fullfile(parentFolder(mfilename('fullpath'), 3), 'tmp');
    saveFolder = fullfile(processInfo.pic_folder, campaignInfo.name, datestr(data.mTime(1), 'yyyy'), datestr(data.mTime(1), 'mm'), datestr(data.mTime(1), 'dd'));

    TC_mask = data.tc_mask_V2;
    height = data.height;
    time = data.mTime;
    figDPI = processInfo.figDPI;
    [xtick, xtickstr] = timelabellayout(data.mTime, 'HH:MM');

    % create tmp folder by force, if it does not exist.
    if ~ exist(tmpFolder, 'dir')
        fprintf('Create the tmp folder to save the temporary results.\n');
        mkdir(tmpFolder);
    end
    
    %% display rcs 
    tmpFile = fullfile(tmpFolder, [basename(tempname), '.mat']);
    save(tmpFile, 'figDPI', 'TC_mask', 'height', 'time', 'processInfo', 'campaignInfo', 'taskInfo', 'xtick', 'xtickstr', '-v7');
    flag = system(sprintf('%s %s %s %s', fullfile(processInfo.pyBinDir, 'python'), fullfile(pyFolder, 'pollyxt_ift_display_targetclassi_V2.py'), tmpFile, saveFolder));
    if flag ~= 0
        warning('Error in executing %s', 'pollyxt_ift_display_targetclassi_V2.py');
    end
    delete(tmpFile);
    
else
    error('Unknow visualization mode. Please check the settings in pollynet_processing_chain_config.json');
end

end