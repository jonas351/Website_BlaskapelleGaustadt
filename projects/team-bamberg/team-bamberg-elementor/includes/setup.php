<?php
if (!defined('ABSPATH')) { exit; }

function team_bamberg_manifest() {
    static $manifest;
    if ($manifest === null) { $manifest = json_decode(file_get_contents(get_theme_file_path('/manifest.json')), true); }
    if (!is_array($manifest) || empty($manifest['pages']) || !isset($manifest['media'])) { return new WP_Error('manifest', 'Das Theme-Paket ist unvollständig.'); }
    return $manifest;
}
function team_bamberg_is_local_test() {
    $host = strtolower((string) wp_parse_url(home_url('/'), PHP_URL_HOST));
    return in_array(wp_get_environment_type(), array('local', 'development'), true)
        || in_array($host, array('localhost', '127.0.0.1', '::1'), true)
        || str_ends_with($host, '.local') || str_ends_with($host, '.test');
}
add_action('admin_menu', function () { add_menu_page('Team Bamberg Website', 'Team Bamberg', 'manage_options', 'team-bamberg', 'team_bamberg_setup_screen', 'dashicons-building', 25); });
add_action('admin_notices', function () {
    if (current_user_can('manage_options') && !get_option('team_bamberg_setup_state')) {
        echo '<div class="notice notice-info"><p><strong>Team Bamberg für Elementor:</strong> <a href="' . esc_url(admin_url('admin.php?page=team-bamberg')) . '">Hier die Website einrichten</a>.</p></div>';
    }
});
add_action('admin_enqueue_scripts', function ($hook) {
    if ($hook !== 'toplevel_page_team-bamberg') { return; }
    wp_enqueue_script('team-bamberg-setup', get_theme_file_uri('/assets/setup.js'), array(), TEAM_BAMBERG_THEME_VERSION, true);
});
function team_bamberg_setup_screen() {
    if (!current_user_can('manage_options')) { return; }
    $manifest = team_bamberg_manifest();
    if (is_wp_error($manifest)) { echo '<div class="wrap"><h1>Team Bamberg</h1><p>' . esc_html($manifest->get_error_message()) . '</p></div>'; return; }
    $state = get_option('team_bamberg_setup_state', array());
    echo '<div class="wrap" style="max-width:1100px"><h1>Deine Team-Bamberg-Website</h1><p>Eigenständiger Gestaltungsentwurf mit Originalinhalten aus team-bamberg.de. Texte, Bilder und Farben direkt in Elementor Free bearbeiten.</p>';
    if (!did_action('elementor/loaded')) {
        $installed = file_exists(WP_PLUGIN_DIR . '/elementor/elementor.php');
        $url = $installed ? wp_nonce_url(admin_url('plugins.php?action=activate&plugin=elementor%2Felementor.php'), 'activate-plugin_elementor/elementor.php') : wp_nonce_url(admin_url('update.php?action=install-plugin&plugin=elementor'), 'install-plugin_elementor');
        echo '<h2>Elementor bereitstellen</h2><p>Das kostenlose Plugin „Elementor Website Builder“ installieren und aktivieren.</p><a class="button button-primary" href="' . esc_url($url) . '">' . ($installed ? 'Elementor aktivieren' : 'Elementor installieren') . '</a></div>'; return;
    }
    echo '<h2>Website anlegen</h2><p>' . count($manifest['pages']) . ' Seiten, Kopf- und Fußbereich sowie Originalbilder und Dokumente importieren. Seiten starten als <strong>Entwürfe</strong>. Bestehende Seiten und Bearbeitungen werden beim Wiederholen erhalten.</p>';
    echo '<button type="button" class="button button-primary" id="team-bamberg-import" data-url="' . esc_url(admin_url('admin-ajax.php')) . '" data-nonce="' . esc_attr(wp_create_nonce('team_bamberg_import')) . '">' . ($state ? 'Import fortsetzen / fehlende Seiten ergänzen' : 'Website-Seiten anlegen') . '</button><p id="team-bamberg-progress" role="status" aria-live="polite"></p><noscript><p>Für den Import JavaScript aktivieren.</p></noscript>';
    if (!empty($state['pages'])) {
        if (($state['design_version'] ?? '') !== TEAM_BAMBERG_THEME_VERSION) {
            echo '<h2>Neue, persönlichere Gestaltung</h2><p>Übernimmt die neuen Vorlagen für alle importierten Team-Bamberg-Seiten sowie Kopf- und Fußbereich. <strong>Ersetzt dabei die bisherigen Elementor-Texte und Layouts.</strong> Diese Inhalte werden vorher gesichert und können unten wiederhergestellt werden. Eingetragene Termine, Kontakt-Empfängeradresse und Menü bleiben erhalten. Andere WordPress-Seiten bleiben unverändert.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="team_bamberg_redesign">';
            if (team_bamberg_is_local_test()) {
                echo '<p><label><input type="checkbox" name="local_preview" value="1" checked> Alle Projektseiten für die Local-Vorschau freigeben und die Startseite aktivieren.</label></p>';
            }
            wp_nonce_field('team_bamberg_redesign'); submit_button('Neue Gestaltung übernehmen', 'primary', 'submit', false); echo '</form>';
        } else { echo '<p><strong>Die neue Gestaltung ist eingerichtet.</strong> Alle Inhalte können weiterhin direkt in Elementor bearbeitet werden.</p>'; }
        if (get_option('team_bamberg_design_backup')) {
            echo '<form style="margin-top:12px" method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="team_bamberg_restore_design">';
            wp_nonce_field('team_bamberg_restore_design'); submit_button('Bisherige Seiteninhalte wiederherstellen', 'secondary', 'submit', false); echo '</form>';
        }
        if (team_bamberg_is_local_test()) {
            $drafts = count(array_filter($state['pages'], function ($id) { return get_post_status($id) === 'draft'; }));
            echo '<h2>Vollständige Local-Vorschau</h2><p>' . (int) $drafts . ' Projektseiten sind noch Entwürfe. Für eine komplette Vorschau müssen sie in Local freigegeben sein; sonst führen ihre Links zu einer nicht gefundenen Seite.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="team_bamberg_preview_local">';
            wp_nonce_field('team_bamberg_preview_local'); submit_button('Alle Seiten in Local anschauen', 'primary', 'submit', false); echo '</form><p><a class="button" href="' . esc_url(home_url('/')) . '" target="_blank" rel="noopener noreferrer">Website öffnen</a></p>';
        }
        echo '<h2>Seiten bearbeiten</h2><table class="widefat striped"><thead><tr><th>Seite</th><th>Status</th><th>Bearbeiten</th></tr></thead><tbody>';
        foreach ($manifest['pages'] as $slug => $page) {
            $id = (int) ($state['pages'][$slug] ?? 0);
            if (!$id || !get_post($id)) { continue; }
            $status = get_post_status_object(get_post_status($id));
            echo '<tr><td>' . esc_html($page['title']) . '</td><td>' . esc_html($status ? $status->label : '') . '</td><td><a class="button" href="' . esc_url(team_bamberg_editor_url($id)) . '">Mit Elementor bearbeiten</a> <a href="' . esc_url(get_preview_post_link($id)) . '" target="_blank" rel="noopener noreferrer">Vorschau</a></td></tr>';
        }
        echo '</tbody></table>';
        if (team_bamberg_is_local_test()) {
            echo '<h2>Alles in Local anschauen</h2><p>Veröffentlicht die Entwürfe dieses Projekts in deiner lokalen Testinstallation, damit du alle Unterseiten aufrufen kannst. Andere Seiten bleiben unverändert.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="team_bamberg_publish_local">';
            wp_nonce_field('team_bamberg_publish_local'); submit_button('Alle Team-Bamberg-Seiten lokal veröffentlichen', 'secondary', 'submit', false); echo '</form>';
        }
        echo '<h2>Kopfbereich, Menü & Fußbereich</h2>';
        foreach ($manifest['parts'] as $part => $label) {
            $id = (int) ($state['parts'][$part] ?? 0);
            if ($id) { echo '<a class="button" style="margin-right:12px" href="' . esc_url(team_bamberg_editor_url($id)) . '">' . esc_html($label) . ' bearbeiten</a>'; }
        }
        echo '<h2>Startseite aktivieren</h2>';
        $home = (int) ($state['pages']['startseite'] ?? 0);
        if ($home && get_post_status($home) === 'publish') {
            echo '<p>Ersetzt die bisherige Startseiten-Zuordnung. Bestehende Seiten bleiben gespeichert.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="team_bamberg_set_home">';
            wp_nonce_field('team_bamberg_set_home'); submit_button('Team Bamberg als Startseite aktivieren', 'secondary', 'submit', false); echo '</form>';
        } else { echo '<p>Zuerst die Startseite in Elementor prüfen und veröffentlichen. Danach erscheint hier der Aktivierungsbutton.</p>'; }
    }
    echo '<h2>Vor dem öffentlichen Start prüfen</h2><ul style="list-style:disc;padding-left:22px">';
    foreach ($manifest['review_notes'] as $note) { echo '<li>' . esc_html($note) . '</li>'; }
    echo '</ul><p><strong>Kontakt:</strong> Die Anfragehilfe bereitet Text zum Kopieren oder für das E-Mail-Programm vor. Kein automatischer Versand. Die bestätigte Empfängeradresse im Widget „Team Bamberg Anfrage“ auf der Kontaktseite eintragen.</p><p><strong>Neue Termine:</strong> Auf der Termineseite im Widget „Team Bamberg Termine“ eintragen. Die Startseite übernimmt bestätigte kommende Termine automatisch. Alte Originalangaben stehen getrennt darunter.</p><p><strong>Bilder:</strong> Originaldateien und vorhandene Bildnutzungsrechte vor Veröffentlichung mit dem bisherigen Betreiber abgleichen.</p></div>';
}
function team_bamberg_resolve($value, $state) {
    static $cache = array();
    $key = md5(wp_json_encode(array($state['pages'], $state['media'], get_option('permalink_structure'))));
    if (!isset($cache[$key])) {
        $urls = array();
        foreach ($state['pages'] as $slug => $id) {
            $token = '@@link:' . $slug . '@@'; $url = get_permalink($id);
            $urls[$token . '?'] = $url . (strpos($url, '?') !== false ? '&' : '?');
            $urls[$token] = $url;
        }
        foreach ($state['media'] as $asset => $id) { $urls['@@asset:' . $asset . '@@'] = wp_get_attachment_url($id) ?: ''; }
        $cache[$key] = $urls;
    }
    return team_bamberg_resolve_value($value, $state, $cache[$key]);
}
function team_bamberg_resolve_value($value, $state, $urls) {
    if (is_array($value)) {
        if (isset($value['team_asset'])) {
            $id = (int) ($state['media'][$value['team_asset']] ?? 0);
            return array('id' => $id, 'url' => $urls['@@asset:' . $value['team_asset'] . '@@'] ?? '');
        }
        foreach ($value as $key => $item) { $value[$key] = team_bamberg_resolve_value($item, $state, $urls); }
    } elseif (is_string($value)) {
        $value = strtr($value, $urls);
    }
    return $value;
}
function team_bamberg_import_step() {
    if (!did_action('elementor/loaded')) { return new WP_Error('elementor', 'Elementor zuerst aktivieren.'); }
    $manifest = team_bamberg_manifest(); if (is_wp_error($manifest)) { return $manifest; }
    $state = get_option('team_bamberg_setup_state', array());
    if (!$state) { $state['design_version'] = TEAM_BAMBERG_THEME_VERSION; }
    $state += array('pages' => array(), 'parts' => array(), 'media' => array());
    // Allocate all page IDs before resolving internal links. Never reuse unrelated pages.
    foreach (array('pages', 'parts') as $group) {
        foreach ($manifest[$group] as $slug => $info) {
            $id = (int) ($state[$group][$slug] ?? 0);
            if ($id && get_post($id) && get_post_status($id) !== 'trash') { continue; }
            $part = $group === 'parts';
            $id = wp_insert_post(array('post_title' => $part ? $info : $info['title'], 'post_name' => $slug,
                'post_type' => $part ? 'elementor_library' : 'page', 'post_status' => $part ? 'publish' : 'draft',
                'post_content' => $part ? '' : wp_kses_post($info['search_text'])), true);
            if (is_wp_error($id)) { return $id; }
            update_post_meta($id, '_team_bamberg_pending', 1);
            $state[$group][$slug] = $id; update_option('team_bamberg_setup_state', $state, false);
        }
    }
    $batch = 0; $media_remaining = 0;
    foreach ($manifest['media'] as $key => $item) {
        $existing = (int) ($state['media'][$key] ?? 0);
        if ($existing && wp_get_attachment_url($existing)) { continue; }
        if ($batch >= 2) { $media_remaining++; continue; }
        $batch++;
        $file = basename($item['file']); $path = get_theme_file_path('/assets/media/' . $file);
        if (!is_readable($path) || hash_file('sha256', $path) !== $item['sha256']) { return new WP_Error('asset', 'Originaldatei fehlt oder ist beschädigt: ' . $file); }
        $upload = wp_upload_bits('team-bamberg-' . $file, null, file_get_contents($path));
        if (!empty($upload['error'])) { return new WP_Error('upload', $upload['error']); }
        $id = wp_insert_attachment(array('post_mime_type' => $item['mime'], 'post_title' => $item['title'], 'post_status' => 'inherit'), $upload['file'], 0, true);
        if (is_wp_error($id)) { return $id; }
        require_once ABSPATH . 'wp-admin/includes/image.php';
        if (strpos($item['mime'], 'image/') === 0) {
            // Several original photos have invalid EXIF pointers. Preserve their bytes;
            // skip EXIF parsing while WordPress generates its standard image sizes.
            add_filter('wp_read_image_metadata_types', '__return_empty_array');
            try { wp_update_attachment_metadata($id, wp_generate_attachment_metadata($id, $upload['file'])); }
            finally { remove_filter('wp_read_image_metadata_types', '__return_empty_array'); }
        }
        update_post_meta($id, '_wp_attachment_image_alt', $item['alt']);
        update_post_meta($id, '_team_bamberg_source_url', esc_url_raw($item['source_url']));
        $state['media'][$key] = $id; update_option('team_bamberg_setup_state', $state, false);
    }
    if ($media_remaining) {
        return array('done' => false, 'message' => 'Bilder und Dokumente: ' . count($state['media']) . ' / ' . count($manifest['media']));
    }
    $count = 0; $remaining = 0;
    foreach (array('pages', 'parts') as $group) {
        foreach ($state[$group] as $slug => $id) {
            if (!get_post_meta($id, '_team_bamberg_pending', true)) { continue; }
            if (get_post_meta($id, '_elementor_data', true)) { delete_post_meta($id, '_team_bamberg_pending'); continue; }
            if ($count++ >= 3) { $remaining++; continue; }
            $template = json_decode(file_get_contents(get_theme_file_path('/templates/' . sanitize_file_name($slug) . '.json')), true);
            if (!is_array($template) || !isset($template['content'])) { return new WP_Error('template', 'Ungültige Vorlage: ' . $slug); }
            update_post_meta($id, '_elementor_edit_mode', 'builder');
            update_post_meta($id, '_elementor_template_type', $group === 'parts' ? 'section' : 'wp-page');
            update_post_meta($id, '_elementor_version', ELEMENTOR_VERSION);
            update_post_meta($id, '_elementor_data', wp_slash(wp_json_encode(team_bamberg_resolve($template['content'], $state))));
            update_post_meta($id, '_elementor_page_settings', array('hide_title' => 'yes', 'background_background' => 'classic', 'background_color' => '#f1ede5'));
            update_post_meta($id, '_wp_page_template', 'default');
            if ($group === 'parts') { wp_set_object_terms($id, 'section', 'elementor_library_type'); }
            delete_post_meta($id, '_elementor_element_cache'); delete_post_meta($id, '_team_bamberg_pending');
        }
    }
    return array('done' => $remaining === 0, 'message' => $remaining ? 'Seiten werden gestaltet …' : 'Fertig! Die Website-Seiten sind als Entwürfe angelegt.');
}
add_action('wp_ajax_team_bamberg_import', function () {
    if (!current_user_can('manage_options')) { wp_send_json_error(array('message' => 'Keine Berechtigung.'), 403); }
    check_ajax_referer('team_bamberg_import', 'nonce');
    $result = team_bamberg_import_step();
    if (is_wp_error($result)) { wp_send_json_error(array('message' => $result->get_error_message()), 400); }
    wp_send_json_success($result);
});
add_action('admin_post_team_bamberg_set_home', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('team_bamberg_set_home');
    $state = get_option('team_bamberg_setup_state', array()); $id = (int) ($state['pages']['startseite'] ?? 0);
    if (!$id || get_post_status($id) !== 'publish') { wp_die('Bitte die Startseite zuerst veröffentlichen.'); }
    if (!isset($state['previous_homepage'])) { $state['previous_homepage'] = array('show_on_front' => get_option('show_on_front'), 'page_on_front' => get_option('page_on_front')); update_option('team_bamberg_setup_state', $state, false); }
    update_option('show_on_front', 'page'); update_option('page_on_front', $id);
    wp_safe_redirect(admin_url('admin.php?page=team-bamberg')); exit;
});
add_action('admin_post_team_bamberg_publish_local', function () {
    if (!current_user_can('manage_options') || !team_bamberg_is_local_test()) { wp_die('Diese Vorschauhilfe ist nur für eine lokale Testinstallation verfügbar.', '', array('response' => 403)); }
    check_admin_referer('team_bamberg_publish_local');
    $state = get_option('team_bamberg_setup_state', array());
    foreach ($state['pages'] ?? array() as $id) {
        if (get_post_status($id) === 'draft' && !get_post_meta($id, '_team_bamberg_pending', true)) {
            wp_update_post(array('ID' => (int) $id, 'post_status' => 'publish'));
            delete_post_meta($id, '_elementor_element_cache');
        }
    }
    wp_safe_redirect(admin_url('admin.php?page=team-bamberg')); exit;
});

// Explicit design replacement, with a reversible content backup. Normal imports preserve edits.
function team_bamberg_preserve_widget_settings($elements, $settings) {
    foreach ($elements as &$element) {
        $type = $element['widgetType'] ?? '';
        if (isset($settings[$type])) { $element['settings'] = array_merge($element['settings'], $settings[$type]); }
        $element['elements'] = team_bamberg_preserve_widget_settings($element['elements'] ?? array(), $settings);
    }
    unset($element);
    return $elements;
}
function team_bamberg_apply_redesign() {
    if (!did_action('elementor/loaded')) { return new WP_Error('elementor', 'Elementor zuerst aktivieren.'); }
    $state = get_option('team_bamberg_setup_state', array());
    if (($state['design_version'] ?? '') === TEAM_BAMBERG_THEME_VERSION) { return true; }
    $manifest = team_bamberg_manifest(); if (is_wp_error($manifest)) { return $manifest; }
    foreach ($manifest['media'] as $key => $item) {
        if (empty($state['media'][$key]) || !wp_get_attachment_url($state['media'][$key])) {
            return new WP_Error('import', 'Bitte zuerst den Import fortsetzen, damit alle Originalbilder vorhanden sind.');
        }
    }
    $replacement = array(); $backup = array();
    // Validate every managed page before writing any replacement.
    foreach (array('pages', 'parts') as $group) {
        foreach ($manifest[$group] as $slug => $info) {
            $id = (int) ($state[$group][$slug] ?? 0);
            if (!$id || !get_post($id) || get_post_status($id) === 'trash' || get_post_meta($id, '_team_bamberg_pending', true)) {
                return new WP_Error('import', 'Bitte zuerst den Website-Import abschließen.');
            }
            $template = json_decode(file_get_contents(get_theme_file_path('/templates/' . sanitize_file_name($slug) . '.json')), true);
            if (!is_array($template) || empty($template['content'])) { return new WP_Error('template', 'Ungültige Vorlage: ' . $slug); }
            $old = get_post_meta($id, '_elementor_data', true);
            $backup[$id] = array('data' => $old, 'page_settings' => get_post_meta($id, '_elementor_page_settings', true));
            $preserve = array();
            foreach (array('team-bamberg-events', 'team-bamberg-inquiry', 'team-bamberg-navigation') as $type) {
                $settings = team_bamberg_find_widget(json_decode($old, true) ?? array(), $type);
                if ($settings !== null) { $preserve[$type] = $settings; }
            }
            $replacement[$id] = team_bamberg_preserve_widget_settings(team_bamberg_resolve($template['content'], $state), $preserve);
        }
    }
    update_option('team_bamberg_design_backup', $backup, false);
    foreach ($replacement as $id => $content) {
        update_post_meta($id, '_elementor_data', wp_slash(wp_json_encode($content)));
        $settings = (array) get_post_meta($id, '_elementor_page_settings', true);
        $settings['background_background'] = 'classic'; $settings['background_color'] = '#f1ede5';
        update_post_meta($id, '_elementor_page_settings', $settings);
        delete_post_meta($id, '_elementor_element_cache'); delete_post_meta($id, '_elementor_css');
    }
    $state['design_version'] = TEAM_BAMBERG_THEME_VERSION;
    update_option('team_bamberg_setup_state', $state, false);
    \Elementor\Plugin::instance()->files_manager->clear_cache();
    return true;
}
function team_bamberg_restore_design() {
    $backup = get_option('team_bamberg_design_backup', array());
    $state = get_option('team_bamberg_setup_state', array());
    $managed = array_merge(array_values($state['pages'] ?? array()), array_values($state['parts'] ?? array()));
    foreach ($backup as $id => $item) {
        if (!in_array((int) $id, array_map('intval', $managed), true) || !get_post($id)) { continue; }
        update_post_meta($id, '_elementor_data', wp_slash($item['data']));
        update_post_meta($id, '_elementor_page_settings', $item['page_settings']);
        delete_post_meta($id, '_elementor_element_cache'); delete_post_meta($id, '_elementor_css');
    }
    unset($state['design_version']); update_option('team_bamberg_setup_state', $state, false);
    delete_option('team_bamberg_design_backup');
    if (did_action('elementor/loaded')) { \Elementor\Plugin::instance()->files_manager->clear_cache(); }
}
add_action('admin_post_team_bamberg_redesign', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('team_bamberg_redesign');
    $result = team_bamberg_apply_redesign();
    if (is_wp_error($result)) { wp_die(esc_html($result->get_error_message())); }
    if (!empty($_POST['local_preview']) && team_bamberg_is_local_test()) {
        $preview = team_bamberg_prepare_local_preview();
        if (is_wp_error($preview)) { wp_die(esc_html($preview->get_error_message())); }
    }
    wp_safe_redirect(admin_url('admin.php?page=team-bamberg')); exit;
});

function team_bamberg_prepare_local_preview() {
    if (!team_bamberg_is_local_test()) { return new WP_Error('local', 'Diese Vorschau ist nur in einer lokalen Testinstallation verfügbar.'); }
    $state = get_option('team_bamberg_setup_state', array());
    $manifest = team_bamberg_manifest(); if (is_wp_error($manifest)) { return $manifest; }
    foreach ($manifest['pages'] as $slug => $page) {
        $id = (int) ($state['pages'][$slug] ?? 0);
        if (!$id || !get_post($id) || get_post_status($id) === 'trash' || get_post_meta($id, '_team_bamberg_pending', true)) {
            return new WP_Error('import', 'Bitte zuerst den Website-Import abschließen.');
        }
    }
    foreach ($state['pages'] as $id) {
        if (get_post_status($id) === 'draft') { wp_update_post(array('ID' => (int) $id, 'post_status' => 'publish')); }
        delete_post_meta($id, '_elementor_element_cache'); delete_post_meta($id, '_elementor_css');
    }
    if (!isset($state['previous_homepage'])) {
        $state['previous_homepage'] = array('show_on_front' => get_option('show_on_front'), 'page_on_front' => get_option('page_on_front'));
        update_option('team_bamberg_setup_state', $state, false);
    }
    update_option('show_on_front', 'page'); update_option('page_on_front', (int) $state['pages']['startseite']);
    if (did_action('elementor/loaded')) { \Elementor\Plugin::instance()->files_manager->clear_cache(); }
    return true;
}
add_action('admin_post_team_bamberg_preview_local', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('team_bamberg_preview_local');
    $result = team_bamberg_prepare_local_preview();
    if (is_wp_error($result)) { wp_die(esc_html($result->get_error_message()), '', array('response' => 400)); }
    wp_safe_redirect(admin_url('admin.php?page=team-bamberg')); exit;
});
add_action('admin_post_team_bamberg_restore_design', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('team_bamberg_restore_design');
    team_bamberg_restore_design();
    wp_safe_redirect(admin_url('admin.php?page=team-bamberg')); exit;
});
