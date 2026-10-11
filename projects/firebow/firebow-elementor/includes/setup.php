<?php
if (!defined('ABSPATH')) { exit; }
function firebow_is_local() {
    $host = strtolower((string) wp_parse_url(home_url(), PHP_URL_HOST));
    return in_array($host, array('localhost', '127.0.0.1', '::1'), true) || str_ends_with($host, '.local') || str_ends_with($host, '.test');
}
add_action('admin_menu', function () {
    add_menu_page('FireBow Website', 'FireBow', 'manage_options', 'firebow', 'firebow_setup_screen', 'dashicons-admin-customizer', 25);
});
add_action('admin_notices', function () {
    if (current_user_can('manage_options') && !get_option('firebow_setup_state')) {
        echo '<div class="notice notice-info"><p><strong>FireBow für Elementor:</strong> <a href="' . esc_url(admin_url('admin.php?page=firebow')) . '">Hier deine Website einrichten</a>.</p></div>';
    }
});
function firebow_setup_screen() {
    if (!current_user_can('manage_options')) { return; }
    $state = get_option('firebow_setup_state', array());
    echo '<div class="wrap" style="max-width:1000px"><h1>Deine FireBow-Website</h1><p>Alle Texte und Seiten mit Elementor Free bearbeiten. Kopfbereich und Fußbereich gelten für die gesamte Website.</p>';
    if (!did_action('elementor/loaded')) {
        $installed = file_exists(WP_PLUGIN_DIR . '/elementor/elementor.php');
        $url = $installed ? wp_nonce_url(admin_url('plugins.php?action=activate&plugin=elementor%2Felementor.php'), 'activate-plugin_elementor/elementor.php') : wp_nonce_url(admin_url('update.php?action=install-plugin&plugin=elementor'), 'install-plugin_elementor');
        echo '<h2>1. Elementor</h2><p>Das kostenlose Plugin „Elementor Website Builder“ installieren und aktivieren. Danach hierher zurückkehren.</p><a class="button button-primary" href="' . esc_url($url) . '">' . ($installed ? 'Elementor aktivieren' : 'Elementor installieren') . '</a></div>'; return;
    }
    echo '<h2>1. Seiten anlegen</h2><p>Erstellt elf Seiten als Entwürfe. Vorhandene Seiten und bereits bearbeitete FireBow-Seiten bleiben erhalten.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="firebow_import">';
    wp_nonce_field('firebow_import'); submit_button($state ? 'Fehlende Seiten ergänzen' : 'FireBow-Seiten anlegen', 'primary', 'submit', false); echo '</form>';
    if (!empty($state['pages'])) {
        if (firebow_is_local()) {
            echo '<h2>2. In Local anschauen</h2><p>Veröffentlicht nur die FireBow-Projektseiten in deiner lokalen Installation und stellt die FireBow-Startseite ein. Die alte Startseiten-Zuordnung wird gespeichert.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="firebow_local_preview">';
            wp_nonce_field('firebow_local_preview'); submit_button('Alle FireBow-Seiten in Local anschauen', 'primary', 'submit', false); echo '</form>';
        }
        echo '<h2>Seiten bearbeiten</h2><table class="widefat striped"><thead><tr><th>Seite</th><th>Status</th><th>Bearbeiten</th></tr></thead><tbody>';
        foreach ($state['pages'] as $id) {
            if (!get_post($id)) { continue; }
            $status = get_post_status_object(get_post_status($id));
            echo '<tr><td>' . esc_html(get_the_title($id)) . '</td><td>' . esc_html($status->label ?? '') . '</td><td><a class="button" href="' . esc_url(admin_url('post.php?post=' . (int) $id . '&action=elementor')) . '">Mit Elementor bearbeiten</a> <a href="' . esc_url(get_post_status($id) === 'publish' ? get_permalink($id) : get_preview_post_link($id)) . '" target="_blank" rel="noopener">Anschauen</a></td></tr>';
        }
        echo '</tbody></table><h2>Kopf- und Fußbereich</h2>';
        foreach (array('header' => 'Kopfbereich & Menü', 'footer' => 'Fußbereich') as $part => $label) {
            if (!empty($state['parts'][$part])) { echo '<a class="button" style="margin-right:10px" href="' . esc_url(admin_url('post.php?post=' . (int) $state['parts'][$part] . '&action=elementor')) . '">' . esc_html($label) . ' bearbeiten</a>'; }
        }
        echo '<h2>So änderst du Inhalte</h2><p><strong>Text:</strong> anklicken und links ändern. <strong>Teamfoto:</strong> Widget „FireBow Teamfoto“ anklicken und ein Bild hochladen. <strong>Logo:</strong> Kopfbereich → „FireBow Logo“. <strong>Kontakt:</strong> Kontaktseite → „FireBow Anfrage“. Immer mit Veröffentlichen bzw. Aktualisieren speichern.</p><p><strong>Vor dem öffentlichen Start:</strong> Logo und Foto ergänzen, Texte bestätigen, Impressum und Datenschutz ausfüllen. Der Formularversand verwendet WordPress; SMTP einrichten und tatsächliche Zustellung prüfen. In Local werden E-Mails normalerweise von Mailpit aufgefangen.</p>';
        if (!firebow_is_local() && get_post_status($state['pages']['startseite'] ?? 0) === 'publish') {
            echo '<h2>Startseite einstellen</h2><p>Stellt die veröffentlichte FireBow-Seite als Startseite ein.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="firebow_set_home">';
            wp_nonce_field('firebow_set_home'); submit_button('FireBow als Startseite verwenden', 'secondary', 'submit', false); echo '</form>';
        }
        if (isset($state['previous_homepage'])) {
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="firebow_restore_home">';
            wp_nonce_field('firebow_restore_home'); submit_button('Vorherige Startseiten-Zuordnung wiederherstellen', 'secondary', 'submit', false); echo '</form>';
        }
    }
    echo '</div>';
}
function firebow_resolve_template($value, $state) {
    if (is_array($value)) { foreach ($value as $key => $item) { $value[$key] = firebow_resolve_template($item, $state); } }
    elseif (is_string($value)) {
        foreach ($state['pages'] as $slug => $id) {
            $token = '@@link:' . $slug . '@@'; $url = get_permalink($id);
            $value = str_replace($token . '?', $url . (strpos($url, '?') !== false ? '&' : '?'), $value);
            $value = str_replace($token, $url, $value);
        }
    }
    return $value;
}
function firebow_import_starters() {
    if (!did_action('elementor/loaded')) { return new WP_Error('elementor', 'Bitte zuerst Elementor aktivieren.'); }
    $templates = array();
    foreach (glob(get_theme_file_path('/templates/*.json')) as $file) {
        $slug = basename($file, '.json'); $data = json_decode(file_get_contents($file), true);
        if (!is_array($data) || !isset($data['content'], $data['title'])) { return new WP_Error('template', 'Ungültige Vorlage: ' . $slug); }
        $templates[$slug] = $data;
    }
    if (count($templates) !== 13) { return new WP_Error('template', 'Vorlagen sind unvollständig. Bitte das vollständige Theme hochladen.'); }
    $state = get_option('firebow_setup_state', array());
    $state += array('pages' => array(), 'parts' => array()); $created = array();
    foreach ($templates as $slug => $data) {
        $part = in_array($slug, array('header', 'footer'), true); $group = $part ? 'parts' : 'pages';
        $id = (int) ($state[$group][$slug] ?? 0);
        if ($id && get_post($id) && get_post_status($id) !== 'trash') { continue; }
        $id = wp_insert_post(array('post_title' => $data['title'], 'post_name' => 'firebow-' . $slug, 'post_type' => $part ? 'elementor_library' : 'page', 'post_status' => $part ? 'publish' : 'draft'), true);
        if (is_wp_error($id)) { return $id; }
        $state[$group][$slug] = $id; $created[$slug] = $id;
        update_option('firebow_setup_state', $state, false);
    }
    // Complete a previously interrupted import without touching initialized content.
    foreach ($templates as $slug => $data) {
        $group = in_array($slug, array('header', 'footer'), true) ? 'parts' : 'pages'; $id = $state[$group][$slug];
        if (!isset($created[$slug]) && get_post_meta($id, '_elementor_data', true) !== '') { continue; }
        update_post_meta($id, '_elementor_edit_mode', 'builder');
        update_post_meta($id, '_elementor_template_type', $group === 'parts' ? 'section' : 'wp-page');
        update_post_meta($id, '_elementor_version', ELEMENTOR_VERSION);
        update_post_meta($id, '_elementor_data', wp_slash(wp_json_encode(firebow_resolve_template($data['content'], $state))));
        update_post_meta($id, '_elementor_page_settings', array('hide_title' => 'yes', 'background_background' => 'classic', 'background_color' => '#f8f4ed'));
        delete_post_meta($id, '_elementor_element_cache');
        if ($group === 'parts') { wp_set_object_terms($id, 'section', 'elementor_library_type'); }
    }
    return $state;
}
function firebow_set_home() {
    $state = get_option('firebow_setup_state', array());
    if (!isset($state['previous_homepage'])) {
        $state['previous_homepage'] = array('show_on_front' => get_option('show_on_front'), 'page_on_front' => get_option('page_on_front'));
        update_option('firebow_setup_state', $state, false);
    }
    update_option('show_on_front', 'page'); update_option('page_on_front', (int) $state['pages']['startseite']);
}
foreach (array('import', 'local_preview', 'set_home', 'restore_home') as $action) {
    add_action('admin_post_firebow_' . $action, function () use ($action) {
        if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
        check_admin_referer('firebow_' . $action);
        $state = get_option('firebow_setup_state', array());
        if ($action === 'import') {
            $result = firebow_import_starters();
            if (is_wp_error($result)) { wp_die(esc_html($result->get_error_message())); }
        } elseif ($action === 'local_preview') {
            if (!firebow_is_local()) { wp_die('Diese Funktion steht nur in Local zur Verfügung.', '', array('response' => 403)); }
            if (empty($state['pages']['startseite'])) { wp_die('Bitte zuerst die Seiten anlegen.'); }
            foreach ($state['pages'] as $id) {
                if (get_post_type($id) !== 'page' || !in_array(get_post_status($id), array('draft', 'publish'), true)) { continue; }
                wp_update_post(array('ID' => (int) $id, 'post_status' => 'publish'));
                delete_post_meta((int) $id, '_elementor_element_cache');
            }
            firebow_set_home();
        } elseif ($action === 'set_home') {
            if (get_post_status($state['pages']['startseite'] ?? 0) !== 'publish') { wp_die('Bitte zuerst die Startseite veröffentlichen.'); }
            firebow_set_home();
        } elseif (isset($state['previous_homepage'])) {
            foreach ($state['previous_homepage'] as $option => $value) { update_option($option, $value); }
            unset($state['previous_homepage']); update_option('firebow_setup_state', $state, false);
        }
        if (did_action('elementor/loaded')) { \Elementor\Plugin::instance()->files_manager->clear_cache(); }
        wp_safe_redirect(admin_url('admin.php?page=firebow&done=1')); exit;
    });
}
