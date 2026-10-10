"""Shared control geometry; theme color must not change the action silhouette."""
SHAPES = dict(r_btn='999px', r_icon='50%', r_segment='12px', r_segment_item='9px')
CONTRACT = dict(version=1, text_action='capsule', icon_action='circle',
                scope='standalone_app_and_widget_actions',
                native_text_shape='Capsule', native_icon_shape='Circle',
                css_capsule_radius='999px',
                exceptions=['plain_text_action','alert_action_row','segmented_control'],
                note='Project styling choice; not a universal Apple button radius')

# Navigation is a persistent location indicator, not a standalone action.
NAVIGATION_CONTRACT = dict(version=1, selected_background='accent_soft',
    selected_text='accent_deep', selected_icon='accent_deep',
    unselected_background='transparent', unselected_foreground='faint',
    radius='r_segment', min_hit_target=44,
    indicator='rounded_background_around_icon_and_label',
    semantics='one_current_item_with_accessibility_selected_state',
    note='Resolve foreground against accent_soft; retain labels and native selected semantics')
