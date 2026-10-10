<?php
if (!defined('ABSPATH')) { exit; }
get_header();
echo '<main id="main" class="tb-page-fallback"><p>404</p><h1>Diese Seite wurde nicht gefunden.</h1><p>Über die Startseite geht es weiter.</p><a class="tb-button" href="' . esc_url(home_url('/')) . '">Zur Startseite →</a></main>';
get_footer();
