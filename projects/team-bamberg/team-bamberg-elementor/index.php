<?php
if (!defined('ABSPATH')) { exit; }
get_header();
echo '<main id="main" class="tb-page-fallback">';
echo '<h1>' . (is_search() ? 'Suche: ' . esc_html(get_search_query()) : 'Beiträge') . '</h1>';
if (have_posts()) {
    while (have_posts()) {
        the_post();
        echo '<article><h2><a href="' . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a></h2>';
        the_excerpt();
        echo '</article>';
    }
    the_posts_pagination();
} else { echo '<p>Keine passenden Inhalte gefunden.</p>'; }
echo '</main>';
get_footer();
