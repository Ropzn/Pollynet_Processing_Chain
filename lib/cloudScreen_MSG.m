function flagCloudFree = cloudScreen_MSG(time, height, signal, slope_thres, ...
                                         search_region)
%CLOUDSCREEN_MSG cloud screen with maximum signal gradient.
%Usage:
%   flagCloudFree = cloudScreen_MSG(height, signal, slope_thres, ...
%                                     search_region)
%Inputs:
%   time: array
%       measurement time for each profile.
%   height: array
%       height. [m]
%   signal: matrix (height * time)
%       photon count rate. [MHz]
%   slope_thres: float
%       threshold of the slope to determine whether there is 
%       strong backscatter signal. [MHz*m]
%   search_region: 2-elements array
%       [baseHeight, topHeight]. [m]
%Outputs:
%   flagCloudFree: boolean
%       whether the profile is cloud free. 
%History:
%   2018-03-04. First edition by zhenping.
%Contact:
%   zhenping@tropos.de

if nargin < 4
    error('Not enough inputs!')
end

if search_region(2) <= height(1)
    error('Not a valid search_region.');
end

if search_region(1) < height(1)
    warning(['Base of search_region is lower than %f, ' ...
             'set it to be %f'], height(1), height(1));
    search_region(1) = height(1);
end

flagCloudFree = false(size(time));

% Range Corrected Signal
RCS = signal .* repmat(transpose(height), 1, size(signal, 2)).^2;

search_indx = int32((search_region - height(1))/(height(2) - height(1))) + 1;

for indx = 1:size(signal, 2)
    if isnan(RCS(1, indx))
        continue;
    end

    slope = [0; diff(smooth(RCS(:, indx), 10))]/(height(2) - height(1));

    if isempty(find(slope(search_indx(1):search_indx(2)) >= slope_thres, 1))
        flagCloudFree(indx) = true;
    end
end

end