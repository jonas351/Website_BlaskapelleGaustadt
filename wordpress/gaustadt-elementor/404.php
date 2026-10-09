<?php
if (!defined('ABSPATH')) { exit; }
get_header();
echo '<main id="main" class="bg-page-fallback"><p>404 · Kurz aus dem Takt</p><h1>Hier spielt die Musik leider nicht.</h1><p>Diese Seite wurde nicht gefunden.</p><a class="bg-button" href="' . esc_url(home_url('/')) . '">Zur Startseite →</a></main>';
get_footer();
