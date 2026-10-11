<?php
if (!defined('ABSPATH')) { exit; }

function team_bamberg_areas() {
    return array('csu-mitte' => 'Mitte', 'csu-gangolf' => 'Gangolf', 'csu-berg' => 'Berg', 'csu-wunderburg' => 'Wunderburg / Gereuth', 'csu-nord' => 'Nord', 'csu-ost' => 'Ost', 'csu-gartenstadt' => 'Gartenstadt', 'csu-gaustadt' => 'Gaustadt');
}
add_action('init', function () {
    register_taxonomy('team_bamberg_area', 'post', array('labels' => array('name' => 'CSU-Meldungen', 'singular_name' => 'CSU-Bereich', 'add_new_item' => 'CSU-Bereich hinzufügen'), 'public' => false, 'show_ui' => true, 'show_in_rest' => true, 'hierarchical' => true, 'rewrite' => false, 'show_admin_column' => true));
});
function team_bamberg_news_areas_setup() {
    foreach (array('bamberg-stadt' => 'Bamberg-Stadt') + team_bamberg_areas() as $slug => $name) {
        if (!term_exists($slug, 'team_bamberg_area')) { wp_insert_term($name, 'team_bamberg_area', array('slug' => $slug)); }
    }
}
function team_bamberg_clear_news_cache() {
    $state = get_option('team_bamberg_setup_state', array());
    foreach ($state['pages'] ?? array() as $id) { delete_post_meta($id, '_elementor_element_cache'); }
}
add_action('save_post_post', 'team_bamberg_clear_news_cache');
add_action('set_object_terms', function ($object, $terms, $ids, $taxonomy) { if ($taxonomy === 'team_bamberg_area') { team_bamberg_clear_news_cache(); } }, 10, 4);

