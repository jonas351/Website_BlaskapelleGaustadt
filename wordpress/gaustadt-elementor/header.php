<?php if (!defined('ABSPATH')) { exit; } ?>
<!doctype html><html <?php language_attributes(); ?>>
<head><meta charset="<?php bloginfo('charset'); ?>"><meta name="viewport" content="width=device-width, initial-scale=1"><?php wp_head(); ?></head>
<body <?php body_class(); ?>><?php wp_body_open(); ?>
<a class="bg-skip" href="#main">Zum Inhalt springen</a>
<header class="bg-site-header" aria-label="Kopfbereich"><?php gaustadt_render_part('header'); ?></header>
