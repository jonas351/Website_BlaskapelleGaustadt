<?php
if (!defined('ABSPATH')) { exit; }

class TeamBamberg_Navigation_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'team-bamberg-navigation'; }
    public function get_title() { return 'Team Bamberg Menü'; }
    public function get_icon() { return 'eicon-nav-menu'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Menüpunkte'));
        $repeater = new \Elementor\Repeater();
        $repeater->add_control('label', array('label' => 'Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Seite'));
        $repeater->add_control('link', array('label' => 'Link', 'type' => \Elementor\Controls_Manager::URL));
        $this->add_control('items', array('type' => \Elementor\Controls_Manager::REPEATER, 'fields' => $repeater->get_controls(), 'title_field' => '{{{ label }}}', 'default' => array()));
        $this->add_control('mobile_label', array('label' => 'Mobile Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Menü'));
        $this->add_control('show_search', array('label' => 'Website-Suche anzeigen', 'type' => \Elementor\Controls_Manager::SWITCHER, 'default' => 'yes'));
        $this->end_controls_section();
        $this->start_controls_section('style', array('label' => 'Farben', 'tab' => \Elementor\Controls_Manager::TAB_STYLE));
        $this->add_control('color', array('label' => 'Textfarbe', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .tb-nav' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $id = 'tb-menu-' . $this->get_id();
        echo '<nav class="tb-nav" data-tb-nav aria-label="Hauptnavigation"><button class="tb-nav-toggle" aria-expanded="false" aria-controls="' . esc_attr($id) . '">' . esc_html($s['mobile_label']) . ' <span aria-hidden="true">☰</span></button><div id="' . esc_attr($id) . '" class="tb-nav-links">';
        $current = get_permalink(get_queried_object_id());
        foreach ((array) $s['items'] as $item) {
            $url = $item['link']['url'] ?? '';
            $active = $current && url_to_postid($url) === get_queried_object_id();
            $external = !empty($item['link']['is_external']);
            echo '<a href="' . esc_url($url) . '"' . ($active ? ' aria-current="page"' : '') . ($external ? ' target="_blank" rel="noopener noreferrer"' : '') . '>' . esc_html($item['label'] ?? '') . ($external ? '<span class="tb-sr"> (öffnet in einem neuen Tab)</span>' : '') . '</a>';
        }
        if (($s['show_search'] ?? '') === 'yes') {
            echo '<details class="tb-search"><summary aria-label="Website durchsuchen">⌕</summary><form role="search" method="get" action="' . esc_url(home_url('/')) . '"><label class="tb-sr" for="' . esc_attr($id) . '-search">Suchbegriff</label><input type="search" id="' . esc_attr($id) . '-search" name="s" placeholder="Website durchsuchen …" required><button type="submit">Suchen</button></form></details>';
        }
        echo '</div></nav>';
    }
}

class TeamBamberg_Events_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'team-bamberg-events'; }
    public function get_title() { return 'Team Bamberg Termine'; }
    public function get_icon() { return 'eicon-calendar'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Termine'));
        $this->add_control('source', array('label' => 'Termine verwenden von', 'type' => \Elementor\Controls_Manager::SELECT, 'default' => 'this', 'options' => array('this' => 'Hier eintragen (Termineseite)', 'shared' => 'Automatisch von der Termineseite')));
        $repeater = new \Elementor\Repeater();
        $repeater->add_control('title', array('label' => 'Veranstaltung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Neue Veranstaltung'));
        $repeater->add_control('date', array('label' => 'Datum', 'type' => \Elementor\Controls_Manager::DATE_TIME, 'picker_options' => array('enableTime' => false, 'dateFormat' => 'Y-m-d'), 'description' => 'Nur bestätigte Termine eintragen.'));
        $repeater->add_control('time', array('label' => 'Uhrzeit', 'type' => \Elementor\Controls_Manager::TEXT, 'placeholder' => '18:00'));
        $repeater->add_control('place', array('label' => 'Ort', 'type' => \Elementor\Controls_Manager::TEXT));
        $repeater->add_control('description', array('label' => 'Weitere Informationen', 'type' => \Elementor\Controls_Manager::TEXTAREA));
        $repeater->add_control('link', array('label' => 'Veranstaltung oder Tickets (optional)', 'type' => \Elementor\Controls_Manager::URL));
        $this->add_control('events', array('type' => \Elementor\Controls_Manager::REPEATER, 'fields' => $repeater->get_controls(), 'title_field' => '{{{ title }}}', 'default' => array(), 'condition' => array('source' => 'this')));
        $this->add_control('single', array('label' => 'Nur nächsten Termin anzeigen', 'type' => \Elementor\Controls_Manager::SWITCHER, 'default' => ''));
        $this->add_control('show_past', array('label' => 'Vergangene Veranstaltungen anzeigen', 'type' => \Elementor\Controls_Manager::SWITCHER, 'default' => 'yes', 'condition' => array('single!' => 'yes')));
        $this->add_control('empty_title', array('label' => 'Überschrift ohne Termine', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Neue Termine folgen.'));
        $this->add_control('empty_text', array('label' => 'Text ohne Termine', 'type' => \Elementor\Controls_Manager::TEXTAREA, 'default' => 'Bestätigte kommende Veranstaltungen werden hier veröffentlicht.'));
        $this->end_controls_section();
        $this->start_controls_section('style', array('label' => 'Farben', 'tab' => \Elementor\Controls_Manager::TAB_STYLE));
        $this->add_control('card_background', array('label' => 'Kartenhintergrund', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .tb-event, {{WRAPPER}} .tb-empty-events' => 'background-color: {{VALUE}};')));
        $this->add_control('heading_color', array('label' => 'Überschriften', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} h3' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    private function card($event) {
        $date = new \DateTimeImmutable($event['date'], wp_timezone());
        echo '<article class="tb-event"><div class="tb-event-date"><strong>' . esc_html($date->format('d')) . '</strong><span>' . esc_html(wp_date('M', $date->getTimestamp())) . '</span></div><div><h3>' . esc_html($event['title'] ?? '') . '</h3><p><time datetime="' . esc_attr($event['date']) . '">' . esc_html(wp_date('l, j. F Y', $date->getTimestamp())) . '</time>';
        if (!empty($event['time'])) { echo ' · ' . esc_html($event['time']) . ' Uhr'; }
        echo '</p><p>' . esc_html($event['place'] ?? '') . '</p><p>' . nl2br(esc_html($event['description'] ?? '')) . '</p>';
        if (!empty($event['link']['url'])) { echo '<a href="' . esc_url($event['link']['url']) . '" target="_blank" rel="noopener noreferrer">Zur Veranstaltung →<span class="tb-sr"> (öffnet in einem neuen Tab)</span></a>'; }
        echo '</div></article>';
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $source = ($s['source'] ?? 'this') === 'shared' ? team_bamberg_page_widget_settings('termine', 'team-bamberg-events') : $s;
        $upcoming = array(); $past = array(); $today = current_time('Y-m-d');
        foreach ((array) ($source['events'] ?? array()) as $event) {
            $raw = substr($event['date'] ?? '', 0, 10);
            $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $raw, wp_timezone());
            if (!$date || $date->format('Y-m-d') !== $raw || empty($event['title'])) { continue; }
            $event['date'] = $raw;
            if ($raw >= $today) { $upcoming[] = $event; } else { $past[] = $event; }
        }
        usort($upcoming, function ($a, $b) { return strcmp($a['date'] . ($a['time'] ?? ''), $b['date'] . ($b['time'] ?? '')); });
        usort($past, function ($a, $b) { return strcmp($b['date'] . ($b['time'] ?? ''), $a['date'] . ($a['time'] ?? '')); });
        if ($upcoming) {
            echo '<div class="tb-event-list">';
            foreach (($s['single'] ?? '') === 'yes' ? array_slice($upcoming, 0, 1) : $upcoming as $event) { $this->card($event); }
            echo '</div>';
        } else {
            echo '<div class="tb-empty-events"><span class="tb-empty-symbol" aria-hidden="true">→</span><h3>' . esc_html($s['empty_title']) . '</h3><p>' . nl2br(esc_html($s['empty_text'])) . '</p></div>';
        }
        if (($s['show_past'] ?? '') === 'yes' && ($s['single'] ?? '') !== 'yes' && $past) {
            echo '<h3 class="tb-past-heading">Vergangene Veranstaltungen</h3><div class="tb-event-list">';
            foreach ($past as $event) { $this->card($event); }
            echo '</div>';
        }
    }
}

class TeamBamberg_Inquiry_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'team-bamberg-inquiry'; }
    public function get_title() { return 'Team Bamberg Anfrage'; }
    public function get_icon() { return 'eicon-mail'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Kontaktweg'));
        $this->add_control('email', array('label' => 'Empfänger-E-Mail', 'type' => \Elementor\Controls_Manager::TEXT, 'input_type' => 'email', 'description' => 'Bestätigte Empfängeradresse eintragen. Die Nachricht wird vorbereitet, nicht automatisch versendet.'));
        $this->add_control('button_text', array('label' => 'Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Anfrage vorbereiten →'));
        $this->add_control('privacy_link', array('label' => 'Datenschutzseite', 'type' => \Elementor\Controls_Manager::URL));
        $this->end_controls_section();
        $this->start_controls_section('style', array('label' => 'Farben', 'tab' => \Elementor\Controls_Manager::TAB_STYLE));
        $this->add_control('button_background', array('label' => 'Buttonfarbe', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .tb-button' => 'background-color: {{VALUE}};')));
        $this->add_control('button_color', array('label' => 'Buttontext', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .tb-button' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $email = sanitize_email($s['email'] ?? '');
        if (!is_email($email)) { $email = ''; }
        $id = 'tb-form-' . $this->get_id();
        $privacy = $s['privacy_link']['url'] ?? '';
        ?>
        <div class="tb-inquiry" data-tb-inquiry data-email="<?php echo esc_attr($email); ?>">
            <p class="tb-inquiry-note"><?php echo $email ? 'Bereite deine Anfrage vor und öffne sie anschließend in deinem E-Mail-Programm.' : 'Bereite deine Nachricht vor. Du kannst den Text anschließend kopieren. Eine bestätigte Empfängeradresse muss noch ergänzt werden.'; ?></p>
            <noscript><p>Zum Vorbereiten der Nachricht wird JavaScript benötigt. Die Telefonnummern stehen auf dieser Seite.</p></noscript>
            <form><fieldset disabled>
                <div class="tb-form-row"><label for="<?php echo esc_attr($id); ?>-name">Dein Name *<input id="<?php echo esc_attr($id); ?>-name" name="name" autocomplete="name" required maxlength="120" placeholder="Vor- und Nachname"></label><label for="<?php echo esc_attr($id); ?>-email">Deine E-Mail *<input id="<?php echo esc_attr($id); ?>-email" name="email" type="email" autocomplete="email" required maxlength="254" placeholder="Für unsere Rückmeldung"></label></div>
                <label for="<?php echo esc_attr($id); ?>-subject">Worum geht’s? *<select id="<?php echo esc_attr($id); ?>-subject" name="subject" required><option value="Allgemeine Anfrage">Eine allgemeine Frage</option><option value="Stadtpolitik">Eine Frage zur Stadtpolitik</option><option value="Mitmachen">Mitglied werden</option><option value="Unterstützung">Die CSU Bamberg unterstützen</option></select></label>
                <label for="<?php echo esc_attr($id); ?>-message">Deine Nachricht *<textarea id="<?php echo esc_attr($id); ?>-message" name="message" rows="6" required minlength="10" maxlength="5000" placeholder="Erzähl uns ein bisschen mehr …"></textarea></label>
                <p class="tb-inquiry-note">Deine Angaben werden nur im Browser zusammengestellt. Es wird noch nichts gesendet. <?php if ($privacy) { ?><a href="<?php echo esc_url($privacy); ?>">Datenschutz</a><?php } ?></p>
                <button class="tb-button" type="submit"><?php echo esc_html($s['button_text']); ?></button><p class="tb-inquiry-note">* Pflichtfelder</p>
            </fieldset></form>
            <section class="tb-inquiry-result" hidden aria-labelledby="<?php echo esc_attr($id); ?>-result">
                <h3 id="<?php echo esc_attr($id); ?>-result" tabindex="-1">Deine Nachricht ist vorbereitet.</h3><p>Es wurde noch nichts gesendet. Prüfe den Text und sende ihn anschließend an uns.</p>
                <textarea class="tb-prepared" rows="8" readonly aria-label="Vorbereitete Nachricht"></textarea>
                <div class="tb-result-actions"><button type="button" class="tb-button">Nachricht kopieren</button><?php if ($email) { ?><a data-tb-send href="<?php echo esc_attr('mailto:' . $email); ?>">E-Mail-Programm öffnen →</a><?php } ?></div>
                <p class="tb-result-status" role="status" aria-live="polite"></p>
            </section>
        </div>
        <?php
    }
}

class TeamBamberg_Archive_Filter_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'team-bamberg-archive-filter'; }
    public function get_title() { return 'Team Bamberg Archivsuche'; }
    public function get_icon() { return 'eicon-search'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Archivsuche'));
        $this->add_control('label', array('label' => 'Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Im Archiv suchen'));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $id = 'tb-archive-' . $this->get_id();
        echo '<div class="tb-archive-filter" data-tb-archive><label for="' . esc_attr($id) . '-query">' . esc_html($s['label']) . '<input type="search" id="' . esc_attr($id) . '-query" placeholder="Thema oder Antrag eingeben …"></label><label for="' . esc_attr($id) . '-year">Jahr<select id="' . esc_attr($id) . '-year"><option value="">Alle Jahre</option></select></label><p role="status" aria-live="polite"></p></div>';
    }
}
