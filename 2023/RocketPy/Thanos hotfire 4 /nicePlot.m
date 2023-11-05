% Usmaan
% ive finally started on this, so yeah this function should in theory work

function [] = nicePlot(figure)

    %---------------------------------------------------------------------%
    % Plot parameters
    plot_width_in_px = 800;
    plot_height_in_px = 600;
    
    marker_size=6;
    marker_line_width=2;
    marker_outline = 'matching'; % could be 'black' or 'matching'
    box_thickness = 1;
    axis_tick_font_size = 15;
    axis_label_font_size = 20;
    legend_font_size = 15;
    %---------------------------------------------------------------------%

    % Use h as handle for current figure
    hFig = figure;                    
    % Change figure background colour to white
    set(hFig, 'Color', 'white');

    % Make the figure bigger
    set(hFig, 'rend', 'painters', 'Units', 'pixels', 'pos', ...
        [100 100 plot_width_in_px plot_height_in_px]);

    % Grab the axes handle(s)
    axis_handles=findobj(hFig,'type','axe');

    % Iterate over all axes handle(s), this is useful if there are subplots
    for i = 1:length(axis_handles)
        ax = axis_handles(i);

        % Change default font size (tick labels, legend, etc.)
        set(ax, 'FontSize', axis_tick_font_size, 'FontName', 'Arial',...
            'TickLabelInterpreter', 'latex', 'LineWidth', box_thickness);
        
        set(ax, 'Box', 'on');
        set(ax, 'XGrid', 'on');
        set(ax, 'YGrid', 'on');

        % Change font size for axis text labels
        set(get(ax, 'XLabel'),'FontSize', axis_label_font_size, 'FontWeight', 'Bold', 'Interpreter', 'latex');
        set(get(ax, 'YLabel'),'FontSize', axis_label_font_size, 'FontWeight', 'Bold', 'Interpreter', 'latex');
    
        set(get(ax, 'Title'),'FontSize', axis_label_font_size, 'FontWeight', 'Bold', 'Interpreter', 'latex');
    end
    
    % Find all the lines, and markers
    LineH = findobj(hFig, 'type', 'line', '-or', 'type', 'errorbar');

    if(~isempty(LineH))
        for i=1:length(LineH) % Iterate over all lines in the plot
            % Decide what color for the marker edges
            this_line_color = get(LineH(i),'color');
            if strcmp(marker_outline, 'black')
                marker_outline_color = 'black';
            elseif strcmp(marker_outline, 'matching')
                marker_outline_color = this_line_color;
            else
                marker_outline_color = 'black';
            end

            % If the LineWidth has not been customized, then change it
            if (get(LineH(i), 'LineWidth') <= 1.0)
                set(LineH(i), 'LineWidth', marker_line_width)
            end
            % Change lines and markers if they exist on the plot
            set(LineH(i),   'MarkerSize', marker_size, ...
                'MarkerEdgeColor', marker_outline_color, ...
                'MarkerFaceColor', this_line_color);
        end
    end

    % Find and change the error bars
    LineH = findobj(hFig, 'type', 'errorbar');
    if(~isempty(LineH))
        for i=1:length(LineH) % Iterate over all lines in the plot
            LineH(i).CapSize=15;
        end
    end

    % Find the legend, and if there is one, change it  
    h = get(hFig,'children');
    for k = 1:length(h)
        if strcmpi(get(h(k),'Tag'),'legend')
            set(h(k), 'FontSize', legend_font_size, 'Interpreter', 'latex', ...
                'location', 'best');
            break;
        end
    end

end