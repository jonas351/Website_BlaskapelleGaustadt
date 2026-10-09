<?php
if (!defined('ABSPATH')) { exit; }
define('GAUSTADT_THEME_VERSION', '1.0.0');
// Supplied layouts use device fonts; avoid requests to external font services.
add_filter('elementor/frontend/print_google_fonts', '__return_false');
add_filter('elementor/fonts/additional_fonts', function ($fonts) {
    $fonts['Gaustadt Serif'] = 'system';
    return $fonts;
});

add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('gallery', 'caption', 'style', 'script'));
    add_theme_support('custom-logo');
    add_post_type_support('page', 'elementor');
});

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('gaustadt-theme', get_stylesheet_uri(), array(), GAUSTADT_THEME_VERSION);
    wp_enqueue_script('gaustadt-interactions', get_theme_file_uri('/assets/site.js'), array('jquery'), GAUSTADT_THEME_VERSION, true);
    if (did_action('elementor/loaded')) {
        $state = get_option('gaustadt_setup_state', array());
        foreach (array('header', 'footer') as $part) {
            if (!empty($state['parts'][$part])) {
                $css = new \Elementor\Core\Files\CSS\Post((int) $state['parts'][$part]);
                $css->enqueue();
            }
        }
    }
});

function gaustadt_render_part($part) {
    $state = get_option('gaustadt_setup_state', array());
    $id = (int) ($state['parts'][$part] ?? 0);
    if ($id && get_post($id) && did_action('elementor/loaded')) {
        echo \Elementor\Plugin::instance()->frontend->get_builder_content_for_display($id, true); // Elementor renders its own stored, authorized content.
        return;
    }
    echo '<div class="bg-fallback"><a href="' . esc_url(home_url('/')) . '">' . esc_html(get_bloginfo('name')) . '</a>';
    if (current_user_can('manage_options')) {
        echo ' · <a href="' . esc_url(admin_url('admin.php?page=gaustadt')) . '">Gaustadt einrichten</a>';
    }
    echo '</div>';
}

function gaustadt_editor_url($id) {
    return admin_url('post.php?post=' . absint($id) . '&action=elementor');
}

function gaustadt_find_widget($elements, $type) {
    foreach ((array) $elements as $element) {
        if (($element['widgetType'] ?? '') === $type) { return $element['settings'] ?? array(); }
        $found = gaustadt_find_widget($element['elements'] ?? array(), $type);
        if ($found !== null) { return $found; }
    }
    return null;
}

function gaustadt_page_widget_settings($slug, $type) {
    $state = get_option('gaustadt_setup_state', array());
    $id = (int) ($state['pages'][$slug] ?? 0);
    // Do not expose unpublished Elementor drafts through shared widgets.
    if (!$id || get_post_status($id) !== 'publish') { return array(); }
    $data = json_decode(get_post_meta($id, '_elementor_data', true), true);
    return gaustadt_find_widget($data ?? array(), $type) ?? array();
}

add_action('elementor/document/after_save', function ($document) {
    $state = get_option('gaustadt_setup_state', array());
    $id = (int) $document->get_main_id();
    if (!in_array($id, array((int) ($state['pages']['kontakt'] ?? 0), (int) ($state['pages']['termine'] ?? 0)), true)) { return; }
    // Shared contact text can appear in cached native Elementor text widgets on other pages.
    foreach (array_merge($state['pages'] ?? array(), $state['parts'] ?? array()) as $page) {
        delete_post_meta((int) $page, '_elementor_element_cache');
    }
});

add_shortcode('gaustadt_email', function () {
    $settings = gaustadt_page_widget_settings('kontakt', 'gaustadt-inquiry');
    $email = sanitize_email($settings['email'] ?? '');
    if (!$email || !is_email($email)) { return '<span class="bg-placeholder">[Kontakt-E-Mail ergänzen]</span>'; }
    return '<a href="' . esc_attr('mailto:' . $email) . '">' . esc_html($email) . '</a>';
});

require_once get_theme_file_path('/includes/setup.php');
add_action('elementor/widgets/register', function ($manager) {
    require_once get_theme_file_path('/includes/widgets.php');
    $manager->register(new Gaustadt_Navigation_Widget());
    $manager->register(new Gaustadt_Events_Widget());
    $manager->register(new Gaustadt_Inquiry_Widget());
});
