<?php
if (!defined('ABSPATH')) { exit; }

class Gaustadt_Navigation_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'gaustadt-navigation'; }
    public function get_title() { return 'Gaustadt Menü'; }
    public function get_icon() { return 'eicon-nav-menu'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Menüpunkte'));
        $repeater = new \Elementor\Repeater();
        $repeater->add_control('label', array('label' => 'Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Seite'));
        $repeater->add_control('link', array('label' => 'Link', 'type' => \Elementor\Controls_Manager::URL));
        $this->add_control('items', array('type' => \Elementor\Controls_Manager::REPEATER, 'fields' => $repeater->get_controls(), 'title_field' => '{{{ label }}}', 'default' => array()));
        $this->add_control('mobile_label', array('label' => 'Mobile Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Menü'));
        $this->end_controls_section();
        $this->start_controls_section('style', array('label' => 'Farben', 'tab' => \Elementor\Controls_Manager::TAB_STYLE));
        $this->add_control('color', array('label' => 'Textfarbe', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .bg-nav' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $id = 'bg-menu-' . $this->get_id();
        echo '<nav class="bg-nav" data-bg-nav aria-label="Hauptnavigation"><button class="bg-nav-toggle" aria-expanded="false" aria-controls="' . esc_attr($id) . '">' . esc_html($s['mobile_label']) . ' <span aria-hidden="true">☰</span></button><div id="' . esc_attr($id) . '" class="bg-nav-links">';
        $current = get_permalink(get_queried_object_id());
        foreach ((array) $s['items'] as $item) {
            $url = $item['link']['url'] ?? '';
            $active = $current && url_to_postid($url) === get_queried_object_id();
            $external = !empty($item['link']['is_external']);
            echo '<a href="' . esc_url($url) . '"' . ($active ? ' aria-current="page"' : '') . ($external ? ' target="_blank" rel="noopener noreferrer"' : '') . '>' . esc_html($item['label'] ?? '') . ($external ? '<span class="bg-sr"> (öffnet in einem neuen Tab)</span>' : '') . '</a>';
        }
        echo '</div></nav>';
    }
}

class Gaustadt_Events_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'gaustadt-events'; }
    public function get_title() { return 'Gaustadt Termine'; }
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
        $this->add_control('single', array('label' => 'Nur nächsten Auftritt anzeigen', 'type' => \Elementor\Controls_Manager::SWITCHER, 'default' => ''));
        $this->add_control('show_past', array('label' => 'Vergangene Auftritte anzeigen', 'type' => \Elementor\Controls_Manager::SWITCHER, 'default' => 'yes', 'condition' => array('single!' => 'yes')));
        $this->add_control('empty_title', array('label' => 'Überschrift ohne Termine', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Hier ist bald Musik drin.'));
        $this->add_control('empty_text', array('label' => 'Text ohne Termine', 'type' => \Elementor\Controls_Manager::TEXTAREA, 'default' => 'Unsere nächsten bestätigten Auftritte werden hier veröffentlicht. Bis dahin gibt es Neuigkeiten auf Instagram.'));
        $this->add_control('instagram', array('label' => 'Instagram-Profil', 'type' => \Elementor\Controls_Manager::URL, 'default' => array('url' => 'https://www.instagram.com/bk.gaustadt/')));
        $this->end_controls_section();
        $this->start_controls_section('style', array('label' => 'Farben', 'tab' => \Elementor\Controls_Manager::TAB_STYLE));
        $this->add_control('card_background', array('label' => 'Kartenhintergrund', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .bg-event, {{WRAPPER}} .bg-empty-events' => 'background-color: {{VALUE}};')));
        $this->add_control('heading_color', array('label' => 'Überschriften', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} h3' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    private function card($event) {
        $date = new \DateTimeImmutable($event['date'], wp_timezone());
        echo '<article class="bg-event"><div class="bg-event-date"><strong>' . esc_html($date->format('d')) . '</strong><span>' . esc_html(wp_date('M', $date->getTimestamp())) . '</span></div><div><h3>' . esc_html($event['title'] ?? '') . '</h3><p><time datetime="' . esc_attr($event['date']) . '">' . esc_html(wp_date('l, j. F Y', $date->getTimestamp())) . '</time>';
        if (!empty($event['time'])) { echo ' · ' . esc_html($event['time']) . ' Uhr'; }
        echo '</p><p>' . esc_html($event['place'] ?? '') . '</p><p>' . nl2br(esc_html($event['description'] ?? '')) . '</p>';
        if (!empty($event['link']['url'])) { echo '<a href="' . esc_url($event['link']['url']) . '" target="_blank" rel="noopener noreferrer">Zur Veranstaltung ↗<span class="bg-sr"> (öffnet in einem neuen Tab)</span></a>'; }
        echo '</div></article>';
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $source = ($s['source'] ?? 'this') === 'shared' ? gaustadt_page_widget_settings('termine', 'gaustadt-events') : $s;
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
            echo '<div class="bg-event-list">';
            foreach (($s['single'] ?? '') === 'yes' ? array_slice($upcoming, 0, 1) : $upcoming as $event) { $this->card($event); }
            echo '</div>';
        } else {
            echo '<div class="bg-empty-events"><span class="bg-empty-symbol" aria-hidden="true">♫</span><h3>' . esc_html($s['empty_title']) . '</h3><p>' . nl2br(esc_html($s['empty_text'])) . '</p><a class="bg-button" href="' . esc_url($s['instagram']['url'] ?? 'https://www.instagram.com/bk.gaustadt/') . '" target="_blank" rel="noopener noreferrer">Aktuelles auf Instagram ↗<span class="bg-sr"> (öffnet in einem neuen Tab)</span></a></div>';
        }
        if (($s['show_past'] ?? '') === 'yes' && ($s['single'] ?? '') !== 'yes' && $past) {
            echo '<h3 class="bg-past-heading">Vergangene Auftritte</h3><div class="bg-event-list">';
            foreach ($past as $event) { $this->card($event); }
            echo '</div>';
        }
    }
}

class Gaustadt_Inquiry_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'gaustadt-inquiry'; }
    public function get_title() { return 'Gaustadt Anfrage'; }
    public function get_icon() { return 'eicon-mail'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Kontaktweg'));
        $this->add_control('email', array('label' => 'Eure Kontakt-E-Mail', 'type' => \Elementor\Controls_Manager::TEXT, 'input_type' => 'email', 'description' => 'Empfänger für den direkten Formularversand. SMTP beim Hoster einrichten und Zustellung testen. Ohne bestätigte Adresse bleibt der Versand deaktiviert.'));
        $this->add_control('instagram', array('label' => 'Instagram-Profil', 'type' => \Elementor\Controls_Manager::URL, 'default' => array('url' => 'https://www.instagram.com/bk.gaustadt/')));
        $this->add_control('button_text', array('label' => 'Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Nachricht senden →'));
        $this->add_control('privacy_link', array('label' => 'Datenschutzseite', 'type' => \Elementor\Controls_Manager::URL));
        $this->end_controls_section();
        $this->start_controls_section('style', array('label' => 'Farben', 'tab' => \Elementor\Controls_Manager::TAB_STYLE));
        $this->add_control('button_background', array('label' => 'Buttonfarbe', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .bg-button' => 'background-color: {{VALUE}};')));
        $this->add_control('button_color', array('label' => 'Buttontext', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .bg-button' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $email = sanitize_email($s['email'] ?? '');
        if (!is_email($email)) { $email = ''; }
        $id = 'bg-form-' . $this->get_id();
        $privacy = $s['privacy_link']['url'] ?? '';
        ?>
        <div class="bg-inquiry" data-bg-inquiry data-endpoint="<?php echo esc_url(admin_url('admin-ajax.php')); ?>">
            <?php if (!$email) { ?><p class="bg-inquiry-note">Das Formular wird noch eingerichtet. Bis dahin erreichst du uns auf <a href="<?php echo esc_url($s['instagram']['url'] ?? 'https://www.instagram.com/bk.gaustadt/'); ?>" target="_blank" rel="noopener noreferrer">Instagram</a>.</p><?php } ?>
            <?php if ($email) { ?><p class="bg-inquiry-note">Du kannst uns auch direkt <a href="<?php echo esc_attr('mailto:' . $email); ?>">per E-Mail kontaktieren</a>.</p><?php } ?>
            <noscript><p>Für den Formularversand bitte JavaScript aktivieren oder den direkten Kontaktweg nutzen.</p></noscript>
            <form method="post" action="<?php echo esc_url(admin_url('admin-ajax.php')); ?>"><fieldset disabled data-configured="<?php echo $email ? 'yes' : 'no'; ?>">
                <input type="hidden" name="action" value="gaustadt_contact">
                <input type="hidden" name="_wpnonce" value="<?php echo esc_attr(wp_create_nonce('gaustadt_contact')); ?>">
                <div class="bg-form-row"><label for="<?php echo esc_attr($id); ?>-name">Dein Name <span>(optional)</span><input id="<?php echo esc_attr($id); ?>-name" name="name" autocomplete="name" maxlength="120" placeholder="Wie dürfen wir dich ansprechen?"></label><label for="<?php echo esc_attr($id); ?>-email">Deine E-Mail *<input id="<?php echo esc_attr($id); ?>-email" name="email" type="email" autocomplete="email" required maxlength="254" placeholder="Für unsere Rückmeldung"></label></div>
                <label for="<?php echo esc_attr($id); ?>-subject">Worum geht’s? *<select id="<?php echo esc_attr($id); ?>-subject" name="subject" required><option value="Allgemeine Anfrage">Eine allgemeine Frage</option><option value="Auftrittsanfrage">Einen Auftritt anfragen</option><option value="Mitmachen">In der Kapelle mitmachen</option><option value="Unterstützung">Die Kapelle unterstützen</option></select></label>
                <label for="<?php echo esc_attr($id); ?>-message">Deine Nachricht *<textarea id="<?php echo esc_attr($id); ?>-message" name="message" rows="6" required minlength="10" maxlength="5000" placeholder="Erzähl uns ein bisschen mehr …"></textarea></label>
                <div class="bg-honeypot" aria-hidden="true"><label for="<?php echo esc_attr($id); ?>-website">Dieses Feld leer lassen<input id="<?php echo esc_attr($id); ?>-website" name="website" tabindex="-1" autocomplete="off"></label></div>
                <p class="bg-inquiry-note">Beim Absenden werden deine Angaben zur Bearbeitung deiner Anfrage an den Verein übermittelt. Bitte keine sensiblen Angaben senden. <?php if ($privacy) { ?><a href="<?php echo esc_url($privacy); ?>">Informationen zum Datenschutz</a><?php } ?></p>
                <button class="bg-button" type="submit">Nachricht senden →</button><p class="bg-inquiry-note">* Pflichtfelder</p>
            </fieldset></form>
            <p class="bg-result-status" role="status" aria-live="polite" aria-atomic="true"></p>
        </div>
        <?php
    }
}

class Gaustadt_Logo_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'gaustadt-logo'; }
    public function get_title() { return 'Gaustadt Vereinslogo'; }
    public function get_icon() { return 'eicon-image'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Originalwappen'));
        $this->add_control('image', array('label' => 'Vereinslogo hochladen', 'type' => \Elementor\Controls_Manager::MEDIA));
        $this->end_controls_section();
    }
    protected function render() {
        $image = $this->get_settings_for_display('image');
        $id = !empty($image['id']) ? (int) $image['id'] : (int) get_theme_mod('custom_logo', 0);
        echo '<a class="bg-club-brand" href="' . esc_url(home_url('/')) . '" aria-label="Blaskapelle St. Josef Gaustadt – Startseite">';
        if ($id) { echo wp_get_attachment_image($id, 'medium', false, array('class' => 'bg-club-logo', 'alt' => 'Wappen der Blaskapelle St. Josef Gaustadt e. V.')); }
        else { echo '<span class="bg-logo-colors" aria-hidden="true"><i></i><i></i><i></i></span>'; }
        echo '</a>';
    }
}
