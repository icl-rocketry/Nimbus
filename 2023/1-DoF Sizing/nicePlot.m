% ive finally started on this, so yeah this function should in theory work

function [] = nicePlot(figure)

    % Plot parameters
    plot_width_px = 600;
    plot_height_px = 400;
    
    axis_tick_font_size = 15;
    axis_label_font_size = 20;
    legend_font_size = 15;
    marker_size=10;
    marker_line_width=2;
    marker_outline = 'matching';
    box_thickness = 1;

    fig = figure;                    
    % set gigure backgorund to white
    set(fig, 'Color', 'white');

    % set figure size
    set(fig, 'rend', 'painters', 'Units', 'pixels', 'pos', [100 100 plot_width_px plot_height_px]);

    % find axes handles
    axis_handles = findobj(fig,'type','axe');

    % iterate over axes handle
    for i = 1:length(axis_handles)
        ax = axis_handles(i);

        % change default font size 
        set(ax, 'FontSize', axis_tick_font_size, 'FontName', 'Arial',...
            'TickLabelInterpreter', 'latex', 'LineWidth', box_thickness);
        
        % set box and grid on 
        set(ax, 'Box', 'on');
        set(ax, 'XGrid', 'on');
        set(ax, 'YGrid', 'on');

        % modify font size for axis labels
        set(get(ax, 'XLabel'),'FontSize', axis_label_font_size, 'FontWeight', 'Bold', 'Interpreter', 'latex');
        set(get(ax, 'YLabel'),'FontSize', axis_label_font_size, 'FontWeight', 'Bold', 'Interpreter', 'latex');
    
    end
    
    % find all markers and lines
    LineH = findobj(fig, 'type', 'line', '-or', 'type', 'errorbar');

    if(~isempty(LineH))
        for i=1:length(LineH) % iterate for all lines in the plot
            % choose what colour for  marker edges
            this_line_color = get(LineH(i),'color');
            if strcmp(marker_outline, 'black')
                marker_outline_color = 'black';
            elseif strcmp(marker_outline, 'matching')
                marker_outline_color = this_line_color;
            else
                marker_outline_color = 'black';
            end

            % change the linewidth if it has not been customized
            if (get(LineH(i), 'LineWidth') <= 1.0)
                set(LineH(i), 'LineWidth', marker_line_width)
            end
            % change lines and markers
            set(LineH(i),   'MarkerSize', marker_size, 'MarkerEdgeColor', marker_outline_color, 'MarkerFaceColor', this_line_color);
        end
    end


    % if there's a legend modify it   
    h = get(fig,'children');
    for k = 1:length(h)
        if strcmpi(get(h(k),'Tag'),'legend')
            set(h(k), 'FontSize', legend_font_size, 'Interpreter', 'latex', 'location', 'best');
            break;
        end
    end

end