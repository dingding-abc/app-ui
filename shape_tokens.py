"""Shared control geometry; theme color must not change the action silhouette."""
SHAPES = dict(r_btn='999px', r_icon='50%', r_segment='12px', r_segment_item='9px')
CONTRACT = dict(version=1, text_action='capsule', icon_action='circle',
                scope='standalone_app_and_widget_actions',
                native_text_shape='Capsule', native_icon_shape='Circle',
                css_capsule_radius='999px',
                exceptions=['plain_text_action','alert_action_row','segmented_control'],
                note='Project styling choice; not a universal Apple button radius')
