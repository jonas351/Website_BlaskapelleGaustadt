<?php
if (!defined('ABSPATH')) { exit; }
get_header();
echo '<main id="main" class="bg-page-fallback">';
if (have_posts()) {
    while (have_posts()) {
        the_post();
        echo '<article><h1><a href="' . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a></h1>';
        the_content();
        echo '</article>';
    }
    the_posts_pagination();
} else { echo '<h1>Hier entsteht unsere Vereinswebsite.</h1>'; }
echo '</main>';
get_footer();
