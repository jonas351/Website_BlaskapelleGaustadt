<?php
if (!defined('ABSPATH')) { exit; }

class TeamBamberg_News_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'team-bamberg-news'; }
    public function get_title() { return 'CSU Bamberg Meldungen'; }
    public function get_icon() { return 'eicon-posts-grid'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Meldungen'));
        $this->add_control('area', array('label' => 'Bereich', 'type' => \Elementor\Controls_Manager::SELECT, 'default' => 'all', 'options' => array('all' => 'Alle CSU-Meldungen') + team_bamberg_areas()));
        $this->add_control('limit', array('label' => 'Anzahl pro Seite', 'type' => \Elementor\Controls_Manager::NUMBER, 'default' => 3, 'min' => 1, 'max' => 24));
        $this->add_control('filters', array('label' => 'Ortsverbandsfilter und Blättern', 'type' => \Elementor\Controls_Manager::SWITCHER, 'default' => ''));
        $this->add_control('empty_title', array('label' => 'Überschrift ohne Meldungen', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Neue Meldungen folgen.'));
        $this->add_control('empty_text', array('label' => 'Text ohne Meldungen', 'type' => \Elementor\Controls_Manager::TEXTAREA, 'default' => 'Hier erscheinen die nächsten veröffentlichten Nachrichten. Für Fragen erreichen Sie uns über die Kontaktseite.'));
        $this->add_control('instructions', array('type' => \Elementor\Controls_Manager::RAW_HTML, 'raw' => 'Neue Meldung unter Beiträge → Erstellen anlegen. Unter CSU-Meldungen Bamberg-Stadt oder den Ortsverband auswählen. Nur veröffentlichte Beiträge dieses Bereichs werden angezeigt.'));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display(); $areas = team_bamberg_areas();
        $area = $s['area'] ?? 'all';
        if ($area !== 'all' && !isset($areas[$area])) { $area = 'all'; }
        $filters = ($s['filters'] ?? '') === 'yes' && $area === 'all';
        $selected = isset($_GET['ort']) && is_string($_GET['ort']) ? sanitize_key(wp_unslash($_GET['ort'])) : '';
        if ($filters && isset($areas[$selected])) { $area = $selected; }
        $paged = $filters && isset($_GET['meldungen_seite']) && is_scalar($_GET['meldungen_seite']) ? max(1, absint($_GET['meldungen_seite'])) : 1;
        if ($filters) {
            $id = 'tb-news-area-' . $this->get_id();
            echo '<form class="tb-news-filter" method="get" action="' . esc_url(get_permalink()) . '"><label for="' . esc_attr($id) . '">Meldungen aus<select id="' . esc_attr($id) . '" name="ort"><option value="">Ganz Bamberg</option>';
            // Preserve plain WordPress page IDs as well as pretty permalinks.
            foreach ($areas as $slug => $name) { echo '<option value="' . esc_attr($slug) . '"' . selected($area, $slug, false) . '>' . esc_html($name) . '</option>'; }
            echo '</select></label>';
            if (!get_option('permalink_structure')) { echo '<input type="hidden" name="page_id" value="' . (int) get_queried_object_id() . '">'; }
            echo '<button class="tb-button" type="submit">Anzeigen →</button></form>';
        }
        $query = new WP_Query(array('post_type' => 'post', 'post_status' => 'publish', 'posts_per_page' => min(24, max(1, (int) ($s['limit'] ?? 3))), 'paged' => $paged, 'ignore_sticky_posts' => true, 'orderby' => 'date', 'order' => 'DESC', 'tax_query' => array(array('taxonomy' => 'team_bamberg_area', 'field' => 'slug', 'terms' => $area === 'all' ? array_merge(array('bamberg-stadt'), array_keys($areas)) : array($area)))));
        if (!$query->have_posts()) {
            echo '<div class="tb-news-empty"><span class="tb-news-empty-mark" aria-hidden="true">→</span><div><h3>' . esc_html($s['empty_title']) . '</h3><p>' . nl2br(esc_html($s['empty_text'])) . '</p></div></div>'; return;
        }
        echo '<div class="tb-news-grid">';
        while ($query->have_posts()) {
            $query->the_post(); $terms = get_the_terms(get_the_ID(), 'team_bamberg_area');
            $label = $terms && !is_wp_error($terms) ? $terms[0]->name : 'Bamberg-Stadt';
            echo '<article class="tb-news-card"><a class="tb-news-image" href="' . esc_url(get_permalink()) . '" tabindex="-1" aria-hidden="true">';
            if (has_post_thumbnail()) { echo get_the_post_thumbnail(get_the_ID(), 'large'); }
            else { echo '<span class="tb-news-placeholder">CSU<br><small>' . esc_html($label) . '</small></span>'; }
            echo '</a><div class="tb-news-copy"><p class="tb-news-meta">' . esc_html($label) . ' · <time datetime="' . esc_attr(get_the_date('c')) . '">' . esc_html(get_the_date('j. F Y')) . '</time></p><h3><a href="' . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a></h3><p>' . esc_html(wp_trim_words(wp_strip_all_tags(get_the_excerpt()), 24)) . '</p><a class="tb-text-link" href="' . esc_url(get_permalink()) . '">Weiterlesen →<span class="tb-sr"> ' . esc_html(get_the_title()) . '</span></a></div></article>';
        }
        echo '</div>'; wp_reset_postdata();
        if ($filters && $query->max_num_pages > 1) {
            echo '<nav class="tb-news-pages" aria-label="Meldungen blättern">';
            $base = str_replace('999999999', '%#%', add_query_arg('meldungen_seite', 999999999, get_permalink()));
            echo wp_kses_post(paginate_links(array('base' => $base, 'format' => '', 'current' => $paged, 'total' => $query->max_num_pages, 'add_args' => isset($areas[$selected]) ? array('ort' => $selected) : array(), 'prev_text' => '← Zurück', 'next_text' => 'Weiter →')));
            echo '</nav>';
        }
    }
}

class TeamBamberg_Hero_Media_Widget extends \Elementor\Widget_Base {
    public function get_name() { return 'team-bamberg-hero-media'; }
    public function get_title() { return 'CSU Bamberg Foto / Drohnenfilm'; }
    public function get_icon() { return 'eicon-video-camera'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Bamberg-Einstieg'));
        $this->add_control('poster', array('label' => 'Bamberg-Foto / Vorschaubild', 'type' => \Elementor\Controls_Manager::MEDIA));
        $this->add_control('video', array('label' => 'Eigenes Video (optional)', 'type' => \Elementor\Controls_Manager::MEDIA, 'media_types' => array('video'), 'description' => 'MP4 oder WebM aus der eigenen Mediathek. Nur Material mit geklärten Nutzungsrechten verwenden. Ohne Video bleibt das Foto sichtbar.'));
        $this->add_control('autoplay', array('label' => 'Stumm automatisch abspielen', 'type' => \Elementor\Controls_Manager::SWITCHER, 'default' => '', 'description' => 'Bei reduzierter Bewegung oder Datensparmodus bleibt das Vorschaubild stehen.'));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display(); $poster = $s['poster'] ?? array();
        $video_id = absint($s['video']['id'] ?? 0);
        $video = $video_id && in_array(get_post_mime_type($video_id), array('video/mp4', 'video/webm'), true) ? wp_get_attachment_url($video_id) : '';
        echo '<div class="tb-hero-media" data-tb-hero-media data-autoplay="' . (($s['autoplay'] ?? '') === 'yes' ? 'yes' : 'no') . '">';
        if (!empty($poster['id'])) { echo wp_get_attachment_image(absint($poster['id']), 'full', false, array('loading' => 'eager', 'fetchpriority' => 'high', 'decoding' => 'async')); }
        elseif (!empty($poster['url'])) { echo '<img src="' . esc_url($poster['url']) . '" alt="Bamberg" loading="eager" fetchpriority="high">'; }
        if ($video) {
            echo '<video muted loop playsinline preload="none" data-src="' . esc_url($video) . '" aria-hidden="true"></video><button class="tb-video-toggle" type="button" aria-label="Bamberg-Video abspielen" aria-pressed="false" hidden>Video abspielen</button>';
        }
        echo '</div>';
    }
}
