<?php
if (!defined('ABSPATH')) { exit; }
get_header();
echo '<main id="main">';
while (have_posts()) {
    the_post();
    if (get_post_meta(get_the_ID(), '_elementor_edit_mode', true) !== 'builder') {
        echo '<article class="bg-page-fallback"><h1>' . esc_html(get_the_title()) . '</h1>';
        the_content();
        echo '</article>';
    } else { the_content(); }
}
echo '</main>';
get_footer();
