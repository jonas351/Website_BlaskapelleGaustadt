<?php
if (!defined('ABSPATH')) { exit; }

add_action('admin_menu', function () {
    add_menu_page('Gaustadt Website', 'Gaustadt', 'manage_options', 'gaustadt', 'gaustadt_setup_screen', 'dashicons-format-audio', 25);
});
add_action('admin_notices', function () {
    if (current_user_can('manage_options') && !get_option('gaustadt_setup_state')) {
        echo '<div class="notice notice-info"><p><strong>Gaustadt für Elementor:</strong> <a href="' . esc_url(admin_url('admin.php?page=gaustadt')) . '">Hier die Vereinswebsite einrichten</a>.</p></div>';
    }
});

function gaustadt_setup_screen() {
    if (!current_user_can('manage_options')) { return; }
    $state = get_option('gaustadt_setup_state', array());
    $labels = array('startseite' => 'Startseite', 'kapelle' => 'Die Kapelle', 'termine' => 'Termine', 'galerie' => 'Galerie', 'mitmachen' => 'Mitmachen', 'kontakt' => 'Kontakt', 'impressum' => 'Impressum', 'datenschutz' => 'Datenschutz');
    echo '<div class="wrap" style="max-width:1050px"><h1>Deine Gaustadt Website</h1><p>Texte, Bilder, Termine und Gestaltung direkt in Elementor bearbeiten. Elementor Free reicht aus.</p>';
    if (!empty($_GET['gaustadt_done'])) { echo '<div class="notice notice-success"><p>Starterseiten angelegt. Du kannst sie jetzt mit Elementor bearbeiten.</p></div>'; }
    if (!empty($_GET['gaustadt_home'])) { echo '<div class="notice notice-success"><p>Die veröffentlichte Gaustadt-Startseite ist jetzt als Startseite eingestellt.</p></div>'; }
    if (!did_action('elementor/loaded')) {
        $installed = file_exists(WP_PLUGIN_DIR . '/elementor/elementor.php');
        $url = $installed ? wp_nonce_url(admin_url('plugins.php?action=activate&plugin=elementor%2Felementor.php'), 'activate-plugin_elementor/elementor.php') : wp_nonce_url(admin_url('update.php?action=install-plugin&plugin=elementor'), 'install-plugin_elementor');
        echo '<h2>1. Elementor bereitstellen</h2><p>Installiere und aktiviere das kostenlose Plugin „Elementor Website Builder“ aus dem WordPress-Pluginverzeichnis.</p><a class="button button-primary" href="' . esc_url($url) . '">' . ($installed ? 'Elementor aktivieren' : 'Elementor installieren') . '</a><p>Danach zu diesem Bereich zurückkehren.</p></div>';
        return;
    }
    echo '<h2>Starterseiten</h2><p>Der Import überschreibt keine vorhandenen Seiten. Er kann wiederholt werden; bereits importierte Seiten und deine Änderungen bleiben erhalten. Die Seiten werden als <strong>Entwürfe</strong> angelegt, damit du die Platzhalter vor Veröffentlichung ersetzen kannst.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="gaustadt_import">';
    wp_nonce_field('gaustadt_import');
    submit_button($state ? 'Fehlende Starterseiten ergänzen' : 'Website-Seiten anlegen', 'primary', 'submit', false);
    echo '</form>';
    if (!empty($state['pages'])) {
        echo '<h2>Deine Seiten bearbeiten</h2><p>Seite öffnen, Inhalte anklicken und links ändern. Mit <strong>Veröffentlichen</strong> bzw. <strong>Aktualisieren</strong> speichern.</p><table class="widefat striped"><thead><tr><th>Seite</th><th>Status</th><th>Bearbeiten</th></tr></thead><tbody>';
        foreach ($labels as $slug => $label) {
            $id = (int) ($state['pages'][$slug] ?? 0);
            if (!$id || !get_post($id)) { continue; }
            $status = get_post_status($id);
            $status_object = get_post_status_object($status);
            echo '<tr><td>' . esc_html($label) . '</td><td>' . esc_html($status_object ? $status_object->label : $status) . '</td><td><a class="button" href="' . esc_url(gaustadt_editor_url($id)) . '">Mit Elementor bearbeiten</a> <a href="' . esc_url(get_preview_post_link($id)) . '" target="_blank" rel="noopener noreferrer">Vorschau</a></td></tr>';
        }
        echo '</tbody></table><h2>Kopf- und Fußbereich</h2><p>Hier geändert, überall aktualisiert. Auch das Menü ist in Elementor bearbeitbar: Widget <strong>Gaustadt Menü</strong> anklicken.</p>';
        foreach (array('header' => 'Kopfbereich & Menü', 'footer' => 'Fußbereich') as $part => $label) {
            if (!empty($state['parts'][$part])) { echo '<a class="button" style="margin-right:10px" href="' . esc_url(gaustadt_editor_url($state['parts'][$part])) . '">' . esc_html($label) . ' bearbeiten</a>'; }
        }
        echo '<h2>Als Startseite verwenden</h2>';
        $home = (int) ($state['pages']['startseite'] ?? 0);
        if ($home && get_post_status($home) === 'publish') {
            echo '<p>Diese Aktion ersetzt die bisherige Startseiten-Zuordnung. Bestehende Seiten werden nicht gelöscht.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="gaustadt_set_home">';
            wp_nonce_field('gaustadt_set_home');
            submit_button('Gaustadt als Startseite aktivieren', 'secondary', 'submit', false);
            echo '</form>';
        } else { echo '<p>Zuerst die Startseite in Elementor prüfen und veröffentlichen. Danach erscheint hier der Aktivierungsbutton.</p>'; }
        echo '<h2>Die häufigsten Änderungen</h2><ul style="list-style:disc;padding-left:22px"><li><strong>Text:</strong> Text anklicken und links ersetzen.</li><li><strong>Foto:</strong> Bild anklicken → Bild auswählen → eigene Datei hochladen.</li><li><strong>Termin:</strong> Termineseite öffnen → Widget „Gaustadt Termine“ anklicken → „Element hinzufügen“ → Datum, Ort und Uhrzeit eintragen → speichern. Die Startseite übernimmt den nächsten Auftritt automatisch, sobald die Termineseite veröffentlicht ist.</li><li><strong>Kontakt-E-Mail:</strong> Kontaktseite → Widget „Gaustadt Anfrage“ → Eure Kontakt-E-Mail. Die angezeigte Kontaktadresse verwendet denselben Wert nach Veröffentlichung der Seite.</li><li><strong>Farben:</strong> Das gewünschte Element auswählen → Stil. Grün, Creme und Gold sowie das Textlogo sind weiterhin vorläufig.</li></ul>';
        echo '<div class="notice notice-warning inline"><p><strong>Vor dem öffentlichen Start:</strong> Platzhalter, Probenangaben, Impressum und Datenschutz vervollständigen. Die Beispielbilder sind Illustrationen. Die Anfragehilfe bereitet eine Nachricht vor, versendet aber nichts automatisch. Ein direkter Formularversand ist nicht enthalten.</p></div>';
    }
    echo '</div>';
}

function gaustadt_import_asset($file, &$state) {
    $existing = (int) ($state['media'][$file] ?? 0);
    if ($existing && wp_get_attachment_url($existing)) { return array('id' => $existing, 'url' => wp_get_attachment_url($existing)); }
    $source = get_theme_file_path('/assets/' . $file . '.png');
    if (!is_readable($source)) { return new WP_Error('missing_asset', 'Bilddatei fehlt: ' . $file); }
    $upload = wp_upload_bits('gaustadt-' . $file . '.png', null, file_get_contents($source));
    if (!empty($upload['error'])) { return new WP_Error('upload_failed', $upload['error']); }
    $id = wp_insert_attachment(array('post_mime_type' => 'image/png', 'post_title' => $file === 'brass' ? 'Trompeten-Illustration' : 'Musik-Illustration – Foto folgt', 'post_status' => 'inherit'), $upload['file'], 0, true);
    if (is_wp_error($id)) { return $id; }
    require_once ABSPATH . 'wp-admin/includes/image.php';
    wp_update_attachment_metadata($id, wp_generate_attachment_metadata($id, $upload['file']));
    update_post_meta($id, '_wp_attachment_image_alt', $file === 'brass' ? 'Illustration einer goldenen Trompete' : 'Musik-Illustration, kein tatsächliches Vereinsfoto');
    $state['media'][$file] = $id;
    update_option('gaustadt_setup_state', $state, false);
    return array('id' => $id, 'url' => $upload['url']);
}

function gaustadt_resolve_template($value, $state, $assets) {
    if (is_array($value)) {
        if (isset($value['bg_asset'])) { return $assets[$value['bg_asset']] ?? array('id' => 0, 'url' => ''); }
        foreach ($value as $key => $item) { $value[$key] = gaustadt_resolve_template($item, $state, $assets); }
    } elseif (is_string($value)) {
        foreach ($state['pages'] as $slug => $id) {
            $token = '@@link:' . $slug . '@@';
            $url = get_permalink($id);
            // Draft/plain permalinks already contain ?page_id=; append additional query parameters safely.
            $value = str_replace($token . '?', $url . (strpos($url, '?') !== false ? '&' : '?'), $value);
            $value = str_replace($token, $url, $value);
        }
        $value = str_replace('@@home@@', home_url('/'), $value);
    }
    return $value;
}

function gaustadt_import_starters() {
    if (!did_action('elementor/loaded')) { return new WP_Error('missing_elementor', 'Bitte zuerst Elementor installieren und aktivieren.'); }
    $slugs = array('startseite', 'kapelle', 'termine', 'galerie', 'mitmachen', 'kontakt', 'impressum', 'datenschutz', 'header', 'footer');
    $templates = array();
    foreach ($slugs as $slug) {
        $file = get_theme_file_path('/templates/' . $slug . '.json');
        if (!is_readable($file)) { return new WP_Error('missing_template', 'Vorlage fehlt: ' . $slug); }
        $template = json_decode(file_get_contents($file), true);
        if (!is_array($template) || !isset($template['content'], $template['title'])) { return new WP_Error('invalid_template', 'Vorlage ist ungültig: ' . $slug); }
        $templates[$slug] = $template;
    }
    $state = get_option('gaustadt_setup_state', array());
    $state += array('pages' => array(), 'parts' => array(), 'media' => array());
    $assets = array();
    foreach (array('brass', 'together', 'illustration-1', 'illustration-2', 'illustration-3') as $asset) {
        $value = gaustadt_import_asset($asset, $state);
        if (is_wp_error($value)) { return $value; }
        $assets[$asset] = $value;
    }
    $created = array();
    foreach ($templates as $slug => $template) {
        $part = in_array($slug, array('header', 'footer'), true);
        $group = $part ? 'parts' : 'pages';
        $existing = (int) ($state[$group][$slug] ?? 0);
        if ($existing && get_post($existing) && get_post_status($existing) !== 'trash') { continue; }
        $id = wp_insert_post(array('post_title' => $template['title'], 'post_name' => $slug, 'post_type' => $part ? 'elementor_library' : 'page', 'post_status' => $part ? 'publish' : 'draft'), true);
        if (is_wp_error($id)) { return $id; }
        $state[$group][$slug] = $id;
        $created[$slug] = $id;
        update_option('gaustadt_setup_state', $state, false);
    }
    foreach ($created as $slug => $id) {
        $content = gaustadt_resolve_template($templates[$slug]['content'], $state, $assets);
        update_post_meta($id, '_elementor_edit_mode', 'builder');
        update_post_meta($id, '_elementor_template_type', in_array($slug, array('header', 'footer'), true) ? 'section' : 'wp-page');
        update_post_meta($id, '_elementor_version', ELEMENTOR_VERSION);
        update_post_meta($id, '_elementor_data', wp_slash(wp_json_encode($content)));
        delete_post_meta($id, '_elementor_element_cache');
        update_post_meta($id, '_elementor_page_settings', array('hide_title' => 'yes', 'background_background' => 'classic', 'background_color' => '#faf8f1'));
        update_post_meta($id, '_wp_page_template', 'default');
        if (in_array($slug, array('header', 'footer'), true)) { wp_set_object_terms($id, 'section', 'elementor_library_type'); }
    }
    update_option('gaustadt_setup_state', $state, false);
    return $state;
}

add_action('admin_post_gaustadt_import', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('gaustadt_import');
    $result = gaustadt_import_starters();
    if (is_wp_error($result)) { wp_die(esc_html($result->get_error_message()) . ' Bitte den Fehler beheben und erneut versuchen. Vorhandene Seiten bleiben erhalten.'); }
    wp_safe_redirect(admin_url('admin.php?page=gaustadt&gaustadt_done=1')); exit;
});
add_action('admin_post_gaustadt_set_home', function () {
    if (!current_user_can('manage_options')) { wp_die('Keine Berechtigung.', '', array('response' => 403)); }
    check_admin_referer('gaustadt_set_home');
    $state = get_option('gaustadt_setup_state', array());
    $id = (int) ($state['pages']['startseite'] ?? 0);
    if (!$id || get_post_status($id) !== 'publish') { wp_die('Bitte die Startseite zuerst veröffentlichen.'); }
    if (!isset($state['previous_homepage'])) {
        $state['previous_homepage'] = array('show_on_front' => get_option('show_on_front'), 'page_on_front' => get_option('page_on_front'));
        update_option('gaustadt_setup_state', $state, false);
    }
    update_option('show_on_front', 'page');
    update_option('page_on_front', $id);
    wp_safe_redirect(admin_url('admin.php?page=gaustadt&gaustadt_home=1')); exit;
});
