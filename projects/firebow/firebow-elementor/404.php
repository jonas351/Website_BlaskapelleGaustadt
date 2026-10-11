<?php
if (!defined('ABSPATH')) { exit; }
get_header();
echo '<main id="main" class="fb-page-fallback"><p>404 · Link nicht gefunden</p><h1>Hier geht’s gerade nicht weiter.</h1><p>Diese Seite wurde nicht gefunden.</p><a class="fb-button" href="' . esc_url(home_url('/')) . '">Zur Startseite →</a></main>';
get_footer();
