<?php
if (!defined('ABSPATH')) { exit; }
define('FIREBOW_THEME_VERSION', '1.1.0');
add_filter('elementor/frontend/print_google_fonts', '__return_false');
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('gallery', 'caption', 'style', 'script'));
    add_theme_support('custom-logo');
    add_post_type_support('page', 'elementor');
});
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('firebow-theme', get_stylesheet_uri(), array(), FIREBOW_THEME_VERSION);
    wp_enqueue_script('firebow-interactions', get_theme_file_uri('/assets/site.js'), array('jquery'), FIREBOW_THEME_VERSION, true);
    if (did_action('elementor/loaded')) {
        $state = get_option('firebow_setup_state', array());
        foreach (array('header', 'footer') as $part) {
            if (!empty($state['parts'][$part])) {
                $css = new \Elementor\Core\Files\CSS\Post((int) $state['parts'][$part]);
                $css->enqueue();
            }
        }
    }
});
function firebow_start_url() {
    $state = get_option('firebow_setup_state', array());
    $id = (int) ($state['pages']['startseite'] ?? 0);
    if ($id && get_post_type($id) === 'page') {
        if (get_post_status($id) === 'publish') { return get_permalink($id); }
        if (get_post_status($id) !== 'trash' && current_user_can('edit_post', $id)) {
            return get_preview_post_link($id);
        }
    }
    return home_url('/');
}
// Upgrades change rendering and the bundled emblem without overwriting user content.
add_action('admin_init', function () {
    if (!current_user_can('manage_options') || get_option('firebow_cached_theme_version') === FIREBOW_THEME_VERSION) { return; }
    $state = get_option('firebow_setup_state', array());
    foreach (array_merge($state['pages'] ?? array(), $state['parts'] ?? array()) as $id) {
        delete_post_meta((int) $id, '_elementor_element_cache');
    }
    if (did_action('elementor/loaded')) { \Elementor\Plugin::instance()->files_manager->clear_cache(); }
    update_option('firebow_cached_theme_version', FIREBOW_THEME_VERSION, false);
});
function firebow_render_part($part) {
    $state = get_option('firebow_setup_state', array());
    $id = (int) ($state['parts'][$part] ?? 0);
    if ($id && get_post($id) && did_action('elementor/loaded')) {
        echo \Elementor\Plugin::instance()->frontend->get_builder_content_for_display($id, true);
        return;
    }
    echo '<div class="fb-fallback"><a href="' . esc_url(firebow_start_url()) . '">FireBow</a>';
    if (current_user_can('manage_options')) { echo ' · <a href="' . esc_url(admin_url('admin.php?page=firebow')) . '">Website einrichten</a>'; }
    echo '</div>';
}
function firebow_find_widget($elements, $type) {
    foreach ((array) $elements as $element) {
        if (($element['widgetType'] ?? '') === $type) { return $element['settings'] ?? array(); }
        $found = firebow_find_widget($element['elements'] ?? array(), $type);
        if ($found !== null) { return $found; }
    }
    return null;
}
function firebow_page_widget_settings($slug, $type, $part = false) {
    $state = get_option('firebow_setup_state', array());
    $id = (int) ($state[$part ? 'parts' : 'pages'][$slug] ?? 0);
    if (!$id || get_post_status($id) !== 'publish') { return array(); }
    return firebow_find_widget(json_decode(get_post_meta($id, '_elementor_data', true), true) ?? array(), $type) ?? array();
}
add_shortcode('firebow_email', function () {
    $settings = firebow_page_widget_settings('kontakt', 'firebow-inquiry');
    $email = sanitize_email($settings['email'] ?? '');
    if (!is_email($email)) { return '<span>[Kontakt-E-Mail ergänzen]</span>'; }
    return '<a href="' . esc_attr('mailto:' . $email) . '">' . esc_html($email) . '</a>';
});
add_action('elementor/document/after_save', function ($document) {
    $state = get_option('firebow_setup_state', array());
    if ((int) $document->get_main_id() !== (int) ($state['pages']['kontakt'] ?? 0)) { return; }
    foreach (array_merge($state['pages'] ?? array(), $state['parts'] ?? array()) as $id) { delete_post_meta((int) $id, '_elementor_element_cache'); }
});
require_once get_theme_file_path('/includes/setup.php');
require_once get_theme_file_path('/includes/contact.php');
add_action('elementor/widgets/register', function ($manager) {
    require_once get_theme_file_path('/includes/widgets.php');
    $manager->register(new Firebow_Navigation_Widget());
    $manager->register(new Firebow_Inquiry_Widget());
    $manager->register(new Firebow_Logo_Widget());
    $manager->register(new Firebow_Teamphoto_Widget());
    $manager->register(new Firebow_FAQ_Widget());
});
