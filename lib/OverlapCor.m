function [sigCor] = OverlapCor(sigFR, overlap, height, normRange)
%OVERLAPCOR Overlap correction.
%Example:
%   sigCor = OverlapCor(sigFR, overlap, height, normRange)
%Inputs:
%   sigFR: matrix (height * time)
%       far-range signal
%   overlap: array
%       overlap function.
%   height: array
%       height above ground. (m)
%   normRange: array
%       signal normalization range. (m)
%Outputs:
%   sigCor: matrix (height * time)
%       glued signal.
%History:
%   2020-04-30. First Edition by Zhenping
%Contact:
%   zp.yin@whu.edu.cn

sigCor = NaN(size(sigFR));

sigNR = sigFR ./ repmat(transpose(overlap), 1, size(sigFR, 2));

if (~ isempty(normRange))
    bottomIndx = find(height >= normRange(1), 1);
    topIndx = find(height >= normRange(end), 1);

    % step-like gluing
    sigCor(1:bottomIndx, :) = sigNR(1:bottomIndx, :);

    m = repmat((transpose(bottomIndx:topIndx) - bottomIndx) ./ (topIndx - bottomIndx), ...
            1, size(sigFR, 2));
    sigCor(bottomIndx:topIndx, :) = sigNR(bottomIndx:topIndx, :) .* (1 - m) + ...
                                    sigFR(bottomIndx:topIndx, :) .* m;

    sigCor(topIndx:end, :) = sigFR(topIndx:end, :);
end

end