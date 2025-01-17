load('OverturningMomentWindspeed9.mat')
file_dist = {'v = 9 m/s', 'v = 9 m/s', 'v = 9 m/s', 'v = 9 m/s', ...
    'v = 9 m/s', 'v = 9 m/s', 'v = 15 m/s', 'v = 21 m/s'}; 

N_BLOCKS = 60;


rs = {M.S1, M.S2, M.S3, M.S4, M.S5, M.S6, M.V15, M.V21};
t = M.t;
block_length = floor(length(t) / N_BLOCKS);

n_seeds = 6;
ks = [];
sigmas = [];
mus = [];
npeaks = [];

pds = [];
maxima = zeros(n_seeds, 1);
x1 = zeros(n_seeds, 1);
blocks = zeros(N_BLOCKS, block_length);
block_maxima = zeros(n_seeds, N_BLOCKS);
block_max_i = zeros(N_BLOCKS, 1);
for j = 1 : length(rs)
    r = rs{j};
    maxima(j) = max(r);
    
    for i = 1 : N_BLOCKS
        blocks(i,:) = r((i - 1) * block_length + 1 : i * block_length);
        [block_maxima(j, i), maxid] = max(blocks(i,:));
        block_max_i(i) = maxid + (i - 1) * block_length;
    end
    
    

    figure()
    subplot(2, 1, 1)
    hold on
    plot(t, r);    
    plot(t(block_max_i), r(block_max_i), 'xr');
    xlabel('Time (s)');
    ylabel('Overturning moment (Nm)');

    subplot(2, 1, 2)
    % Thanks to: https://de.mathworks.com/matlabcentral/answers/315084-
    % how-can-i-fit-a-gumbel-maximum-distribution-using-both-maximum-likelihood-estimates-and-method-of-mo
    gamma = 0.5772;
    sigmaHat = sqrt(6)*std(block_maxima(j,:)')/pi;
    muHat = mean(block_maxima(j,:)') - gamma*sigmaHat;
    pd = makedist('GeneralizedExtremeValue','k',0,'sigma',sigmaHat,'mu',muHat);
    qqplot(block_maxima(j,:), pd)
    
    pds = [pds; pd];
    sigmas = [sigmas; pd.sigma];
    mus = [mus; pd.mu];
    x1(j) = pd.icdf(1 - 1/N_BLOCKS);
end




figure
subplot(1, 4, 1:4)
y = [sigmas, mus, x1, maxima]';
h = bar(y);
set(h, {'DisplayName'}, file_dist')
legend('location', 'northwest', 'box', 'off') 
box off
set(gca, 'XTick', [1,2,3,4])
set(gca, 'XTickLabel', {'$\sigma$', '$\mu$', '$\hat{x}_{1hr}$', 'realized max'}, 'TickLabelInterpreter', 'latex')
exportgraphics(gcf, 'gfx/Gumbel-Parameters.jpg') 
exportgraphics(gcf, 'gfx/Gumbel-Parameters.pdf') 

figure('Position', [100 100 900 900])
x = [7:0.01:16] * 10^7;

% PDF
for i = 1:length(rs)
    subplot(length(rs), 3, i * 3 - 2)
    ax = gca;
    title(file_dist{i});
    ax.TitleHorizontalAlignment = 'left'; 
    hold on
    histogram(block_maxima(i,:), 'normalization', 'pdf')
    f = pds(i).pdf(x);
    plot(x, f);
    xlim([7*10^7, 12*10^7]);
end

% CDF of 1-hr maximum
for i = 1:length(rs)
    subplot(length(rs), 3, i * 3 - 1)
    hold on
    p = pds(i).cdf(x);
    plot(x, p);
    p = pds(i).cdf(x).^N_BLOCKS;
    plot(x, p);
    realizedp(i) = pds(i).cdf(maxima(i)).^N_BLOCKS;
    xlim([7*10^7, 16*10^7]);
end

% ICDF of 1-hr maximum
for i = 1:length(rs)
    subplot(length(rs), 3, i * 3)
    hold on
    p = rand(10^4, 1).^(1/N_BLOCKS);
    x = pds(i).icdf(p);
    histogram(x, 'normalization', 'pdf');
    ylims = get(gca, 'ylim');
    if i <= 6
        plot([min(maxima) min(maxima)], [0 ylims(2)], '-r', 'linewidth', 1)
        plot([max(maxima) max(maxima)], [0 ylims(2)], '-r', 'linewidth', 1)
        h = text(min(maxima) -0.3 * 10^7, 0.5 * ylims(2), ...
            'min(realized)', 'fontsize', 6', 'color', 'red', ...
            'horizontalalignment', 'center');
        set(h,'Rotation',90);
        h = text(max(maxima) + 0.3 * 10^7, 0.5 * ylims(2), ...
            'max(realized)', 'fontsize', 6', 'color', 'red', ...
            'horizontalalignment', 'center');
        set(h,'Rotation',90);
    end
    xlim([9*10^7, 16*10^7]);
end

exportgraphics(gcf, 'gfx/Gumbel-PDFs.jpg') 
exportgraphics(gcf, 'gfx/Gumbel-PDFs.pdf') 