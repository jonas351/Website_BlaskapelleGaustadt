<?php
if (!defined('ABSPATH')) { exit; }

function gaustadt_is_local() {
    $host = strtolower((string) wp_parse_url(home_url('/'), PHP_URL_HOST));
    return in_array(wp_get_environment_type(), array('local', 'development'), true)
        || in_array($host, array('localhost', '127.0.0.1', '::1'), true) || str_ends_with($host, '.local') || str_ends_with($host, '.test');
}
function gaustadt_brand_colors($value) {
    $map = array('#183c34'=>'#211d19', '#faf8f1'=>'#faf7ed', '#dbc18a'=>'#fff000', '#f0eee4'=>'#f1ead9', '#233c33'=>'#211d19', '#65716a'=>'#635f58', '#123129'=>'#211d19', '#d7dccb'=>'#e8e2d7', '#c1cdbc'=>'#e8e2d7', '#ccd4c9'=>'#635f58', '#bbc8b7'=>'#635f58', '#eeeee3'=>'#f1ead9', '#dedfd4'=>'#dcd3c1');
    if (is_array($value)) {
        foreach ($value as $key => $item) { $value[$key] = gaustadt_brand_colors($item); }
        if (($value['elType'] ?? '') === 'container' && isset($value['settings']['_css_classes'])) {
            $value['settings']['css_classes'] = $value['settings']['_css_classes']; unset($value['settings']['_css_classes']);
        }
        if (($value['widgetType'] ?? '') === 'heading' && ($value['settings']['title'] ?? '') === '<small>BLASKAPELLE</small>GAUSTADT') { $value['settings']['title'] = '<small>BLASKAPELLE ST. JOSEF</small>GAUSTADT'; }
        if (($value['widgetType'] ?? '') === 'heading' && ($value['settings']['_css_classes'] ?? '') === 'bg-roundmark') {
            $value['widgetType'] = 'gaustadt-logo'; $value['settings'] = array();
        }
    } elseif (is_string($value)) { $value = str_ireplace(array_keys($map), array_values($map), $value); }
    return $value;
}
function gaustadt_brand_hero($elements) {
    foreach ($elements as &$element) {
        if (($element['widgetType'] ?? '') === 'heading') {
            $color = $element['settings']['title_color'] ?? '';
            if ($color === '#faf7ed') { $element['settings']['title_color'] = '#211d19'; }
            if ($color === '#fff000') { $element['settings']['title_color'] = '#00789d'; }
            $element['settings']['title'] = str_replace('#fff000', '#00789d', $element['settings']['title'] ?? '');
        }
        $element['elements'] = gaustadt_brand_hero($element['elements'] ?? array());
    }
    unset($element); return $elements;
}
function gaustadt_apply_brand($privacy_template = false) {
    $state = get_option('gaustadt_setup_state', array());
    if (($state['design_version'] ?? '') === GAUSTADT_THEME_VERSION) { return true; }
    $ids = array_merge($state['pages'] ?? array(), $state['parts'] ?? array());
    if (count($ids) !== 10) { return new WP_Error('import', 'Bitte zuerst die Website-Seiten vollständig anlegen.'); }
    $backup = array();
    foreach ($ids as $slug => $id) {
        if (!get_post($id) || get_post_status($id) === 'trash') { return new WP_Error('missing', 'Eine Projektseite fehlt. Bitte den Import ergänzen.'); }
        $backup[$id] = array('data' => get_post_meta($id, '_elementor_data', true), 'settings' => get_post_meta($id, '_elementor_page_settings', true));
    }
    // Save one restorable snapshot; repeat updates must not overwrite it.
    if (!get_option('gaustadt_brand_backup')) { update_option('gaustadt_brand_backup', $backup, false); }
    $assets = array();
    foreach ($state['media'] ?? array() as $name => $id) { $assets[$name] = array('id' => $id, 'url' => wp_get_attachment_url($id)); }
    foreach ($ids as $slug => $id) {
        $data = gaustadt_brand_colors(json_decode(get_post_meta($id, '_elementor_data', true), true) ?? array());
        if ($slug === 'startseite' && !empty($data[0]['elements'])) {
            $data[0]['settings']['background_color'] = '#faf7ed';
            $data[0]['settings']['css_classes'] = trim(($data[0]['settings']['css_classes'] ?? '') . ' bg-hero');
            $data[0]['elements'] = gaustadt_brand_hero($data[0]['elements']);
        }
        if ($slug === 'datenschutz' && $privacy_template) {
            $template = json_decode(file_get_contents(get_theme_file_path('/templates/datenschutz.json')), true);
            $data = gaustadt_resolve_template($template['content'], $state, $assets);
        }
        update_post_meta($id, '_elementor_data', wp_slash(wp_json_encode($data)));
        update_post_meta($id, '_elementor_page_settings', gaustadt_brand_colors(get_post_meta($id, '_elementor_page_settings', true)));
        delete_post_meta($id, '_elementor_element_cache'); delete_post_meta($id, '_elementor_css');
    }
    $state['design_version'] = GAUSTADT_THEME_VERSION; update_option('gaustadt_setup_state', $state, false);
    if (did_action('elementor/loaded')) { \Elementor\Plugin::instance()->files_manager->clear_cache(); }
    return true;
}
add_action('admin_post_gaustadt_brand', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('gaustadt_brand');
    $result = gaustadt_apply_brand(!empty($_POST['privacy_template']));
    if (is_wp_error($result)) { wp_die(esc_html($result->get_error_message())); }
    wp_safe_redirect(admin_url('admin.php?page=gaustadt')); exit;
});
add_action('admin_post_gaustadt_restore_brand', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('gaustadt_restore_brand');
    foreach (get_option('gaustadt_brand_backup', array()) as $id => $item) {
        update_post_meta($id, '_elementor_data', wp_slash($item['data'])); update_post_meta($id, '_elementor_page_settings', $item['settings']);
        delete_post_meta($id, '_elementor_element_cache'); delete_post_meta($id, '_elementor_css');
    }
    $state = get_option('gaustadt_setup_state', array()); unset($state['design_version']); update_option('gaustadt_setup_state', $state, false);
    delete_option('gaustadt_brand_backup');
    if (did_action('elementor/loaded')) { \Elementor\Plugin::instance()->files_manager->clear_cache(); }
    wp_safe_redirect(admin_url('admin.php?page=gaustadt')); exit;
});
function gaustadt_local_preview() {
    if (!gaustadt_is_local()) { return new WP_Error('local', 'Diese Vorschau ist nur in Local verfügbar.'); }
    $state = get_option('gaustadt_setup_state', array());
    foreach (array('startseite', 'kapelle', 'termine', 'galerie', 'mitmachen', 'kontakt', 'impressum', 'datenschutz') as $slug) {
        $id = (int) ($state['pages'][$slug] ?? 0);
        if (!$id || !in_array(get_post_status($id), array('draft', 'publish'), true)) { return new WP_Error('import', 'Bitte den Import abschließen und private Projektseiten einzeln prüfen.'); }
    }
    foreach ($state['pages'] as $id) { if (get_post_status($id) === 'draft') { wp_update_post(array('ID' => (int) $id, 'post_status' => 'publish')); } }
    if (!isset($state['previous_homepage'])) { $state['previous_homepage'] = array('show_on_front' => get_option('show_on_front'), 'page_on_front' => get_option('page_on_front')); update_option('gaustadt_setup_state', $state, false); }
    update_option('show_on_front', 'page'); update_option('page_on_front', (int) $state['pages']['startseite']);
    return true;
}
add_action('admin_post_gaustadt_local_preview', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('gaustadt_local_preview'); $result = gaustadt_local_preview();
    if (is_wp_error($result)) { wp_die(esc_html($result->get_error_message())); }
    wp_safe_redirect(admin_url('admin.php?page=gaustadt')); exit;
});
