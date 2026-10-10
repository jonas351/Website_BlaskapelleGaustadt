<?php
if (!defined('ABSPATH')) { exit; }
define('TEAM_BAMBERG_THEME_VERSION', '1.1.0');
add_filter('elementor/frontend/print_google_fonts', '__return_false');
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form', 'gallery', 'caption', 'style', 'script'));
    add_post_type_support('page', 'elementor');
});
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('team-bamberg-theme', get_stylesheet_uri(), array(), TEAM_BAMBERG_THEME_VERSION);
    wp_enqueue_script('team-bamberg-interactions', get_theme_file_uri('/assets/site.js'), array('jquery'), TEAM_BAMBERG_THEME_VERSION, true);
    if (did_action('elementor/loaded')) {
        $state = get_option('team_bamberg_setup_state', array());
        foreach (array('header', 'footer') as $part) {
            if (!empty($state['parts'][$part])) {
                (new \Elementor\Core\Files\CSS\Post((int) $state['parts'][$part]))->enqueue();
            }
        }
    }
});
function team_bamberg_editor_url($id) { return admin_url('post.php?post=' . absint($id) . '&action=elementor'); }
function team_bamberg_render_part($part) {
    $state = get_option('team_bamberg_setup_state', array());
    $id = (int) ($state['parts'][$part] ?? 0);
    if ($id && get_post($id) && did_action('elementor/loaded')) {
        echo \Elementor\Plugin::instance()->frontend->get_builder_content_for_display($id, true);
        return;
    }
    echo '<div class="tb-fallback"><a href="' . esc_url(home_url('/')) . '">' . esc_html(get_bloginfo('name')) . '</a>';
    if (current_user_can('manage_options')) { echo ' · <a href="' . esc_url(admin_url('admin.php?page=team-bamberg')) . '">Team Bamberg einrichten</a>'; }
    echo '</div>';
}
function team_bamberg_find_widget($elements, $type) {
    foreach ((array) $elements as $element) {
        if (($element['widgetType'] ?? '') === $type) { return $element['settings'] ?? array(); }
        $found = team_bamberg_find_widget($element['elements'] ?? array(), $type);
        if ($found !== null) { return $found; }
    }
    return null;
}
function team_bamberg_page_widget_settings($slug, $type) {
    $state = get_option('team_bamberg_setup_state', array());
    $id = (int) ($state['pages'][$slug] ?? 0);
    if (!$id || get_post_status($id) !== 'publish') { return array(); }
    return team_bamberg_find_widget(json_decode(get_post_meta($id, '_elementor_data', true), true), $type) ?? array();
}
add_action('elementor/document/after_save', function ($document) {
    $state = get_option('team_bamberg_setup_state', array());
    if ((int) $document->get_main_id() !== (int) ($state['pages']['termine'] ?? 0)) { return; }
    foreach (array_merge($state['pages'] ?? array(), $state['parts'] ?? array()) as $id) { delete_post_meta((int) $id, '_elementor_element_cache'); }
});
require_once get_theme_file_path('/includes/setup.php');
add_action('elementor/widgets/register', function ($manager) {
    require_once get_theme_file_path('/includes/widgets.php');
    $manager->register(new TeamBamberg_Navigation_Widget());
    $manager->register(new TeamBamberg_Events_Widget());
    $manager->register(new TeamBamberg_Inquiry_Widget());
    $manager->register(new TeamBamberg_Archive_Filter_Widget());
});
