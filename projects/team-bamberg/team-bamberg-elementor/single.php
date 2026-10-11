<?php
if (!defined('ABSPATH')) { exit; }
get_header();
echo '<main id="main" class="tb-article">';
while (have_posts()) {
    the_post();
    $state = get_option('team_bamberg_setup_state', array());
    $news = get_permalink((int) ($state['pages']['aktuelles'] ?? 0)) ?: home_url('/');
    echo '<article><header class="tb-article-head"><p><a href="' . esc_url($news) . '">← Alle Meldungen</a></p><p class="tb-news-meta"><time datetime="' . esc_attr(get_the_date('c')) . '">' . esc_html(get_the_date('j. F Y')) . '</time></p><h1>' . esc_html(get_the_title()) . '</h1>';
    if (has_post_thumbnail()) { the_post_thumbnail('full', array('class' => 'tb-article-image')); }
    echo '</header><div class="tb-article-body">'; the_content(); echo '</div></article>';
}
echo '</main>'; get_footer();
