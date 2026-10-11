<?php
if (!defined('ABSPATH')) { exit; }

class Firebow_Logo_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'firebow-logo'; }
    public function get_title() { return 'FireBow Logo'; }
    public function get_icon() { return 'eicon-image'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Original-Logo'));
        $this->add_control('image', array('label' => 'Logo auswählen', 'type' => \Elementor\Controls_Manager::MEDIA, 'description' => 'PNG oder WebP mit transparentem Hintergrund. Ohne Datei erscheint der Schriftzug FireBow.'));
        $this->end_controls_section();
    }
    protected function render() {
        $image = $this->get_settings_for_display('image');
        $id = (int) ($image['id'] ?? 0);
        if (!$id) { $shared = firebow_page_widget_settings('header', 'firebow-logo', true); $id = (int) ($shared['image']['id'] ?? get_theme_mod('custom_logo', 0)); }
        echo '<a class="fb-brand" href="' . esc_url(home_url('/')) . '" aria-label="FireBow – Startseite">';
        if ($id) { echo wp_get_attachment_image($id, 'medium', false, array('alt' => 'FireBow', 'class' => 'fb-brand-image')); }
        else { echo '<span class="fb-brand-word">Fire<span>Bow</span><i aria-hidden="true"></i></span>'; }
        echo '</a>';
    }
}

class Firebow_Teamphoto_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'firebow-teamphoto'; }
    public function get_title() { return 'FireBow Teamfoto'; }
    public function get_icon() { return 'eicon-image'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Euer Foto'));
        $this->add_control('image', array('label' => 'Foto auswählen', 'type' => \Elementor\Controls_Manager::MEDIA));
        $this->add_control('alt', array('label' => 'Bildbeschreibung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Jonas und Benedikt von FireBow'));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display(); $id = (int) ($s['image']['id'] ?? 0);
        if (!$id) { $shared = firebow_page_widget_settings('ueber-uns', 'firebow-teamphoto'); $id = (int) ($shared['image']['id'] ?? 0); }
        echo '<div class="fb-teamphoto">';
        if ($id) { echo wp_get_attachment_image($id, 'large', false, array('alt' => $s['alt'] ?? 'Jonas und Benedikt von FireBow')); }
        else { echo '<div class="fb-photo-placeholder"><div class="fb-initials" aria-hidden="true"><span>J</span><span>B</span></div><p>Jonas &amp; Benedikt</p><small>Euer Teamfoto kommt hierhin.</small></div>'; }
        echo '</div>';
    }
}

class Firebow_FAQ_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'firebow-faq'; }
    public function get_title() { return 'FireBow Fragen & Antworten'; }
    public function get_icon() { return 'eicon-accordion'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Fragen & Antworten'));
        $this->add_control('source', array('label' => 'Inhalte verwenden von', 'type' => \Elementor\Controls_Manager::SELECT, 'default' => 'this', 'options' => array('this' => 'Hier eintragen (FAQ-Seite)', 'shared' => 'Automatisch von der FAQ-Seite')));
        $repeater = new \Elementor\Repeater();
        $repeater->add_control('question', array('label' => 'Frage', 'type' => \Elementor\Controls_Manager::TEXT));
        $repeater->add_control('answer', array('label' => 'Antwort', 'type' => \Elementor\Controls_Manager::WYSIWYG));
        $this->add_control('items', array('type' => \Elementor\Controls_Manager::REPEATER, 'fields' => $repeater->get_controls(), 'title_field' => '{{{ question }}}', 'default' => array(), 'condition' => array('source' => 'this')));
        $this->add_control('limit', array('label' => 'Anzahl (0 = alle)', 'type' => \Elementor\Controls_Manager::NUMBER, 'default' => 0, 'min' => 0, 'max' => 100));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $source = ($s['source'] ?? 'this') === 'shared' ? firebow_page_widget_settings('faq', 'firebow-faq') : $s;
        $items = (array) ($source['items'] ?? array());
        if ((int) ($s['limit'] ?? 0) > 0) { $items = array_slice($items, 0, (int) $s['limit']); }
        echo '<div class="fb-faq-items">';
        foreach ($items as $item) {
            if (empty($item['question'])) { continue; }
            echo '<details class="fb-faq"><summary>' . esc_html($item['question']) . '</summary><div>' . wp_kses_post($item['answer'] ?? '') . '</div></details>';
        }
        echo '</div>';
    }
}

class Firebow_Navigation_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'firebow-navigation'; }
    public function get_title() { return 'FireBow Menü'; }
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
        $this->add_control('color', array('label' => 'Textfarbe', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .fb-nav' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $id = 'fb-menu-' . $this->get_id();
        echo '<nav class="fb-nav" data-fb-nav aria-label="Hauptnavigation"><button class="fb-nav-toggle" aria-expanded="false" aria-controls="' . esc_attr($id) . '">' . esc_html($s['mobile_label']) . ' <span aria-hidden="true">☰</span></button><div id="' . esc_attr($id) . '" class="fb-nav-links">';
        $current = get_permalink(get_queried_object_id());
        foreach ((array) $s['items'] as $item) {
            $url = $item['link']['url'] ?? '';
            $active = $current && url_to_postid($url) === get_queried_object_id();
            $external = !empty($item['link']['is_external']);
            echo '<a href="' . esc_url($url) . '"' . ($active ? ' aria-current="page"' : '') . ($external ? ' target="_blank" rel="noopener noreferrer"' : '') . '>' . esc_html($item['label'] ?? '') . ($external ? '<span class="fb-sr"> (öffnet in einem neuen Tab)</span>' : '') . '</a>';
        }
        echo '</div></nav>';
    }
}

class Firebow_Inquiry_Widget extends \Elementor\Widget_Base {
    protected function is_dynamic_content(): bool { return true; }
    public function get_name() { return 'firebow-inquiry'; }
    public function get_title() { return 'FireBow Anfrage'; }
    public function get_icon() { return 'eicon-mail'; }
    public function get_categories() { return array('general'); }
    protected function register_controls() {
        $this->start_controls_section('content', array('label' => 'Kontaktweg'));
        $this->add_control('email', array('label' => 'Kontakt-E-Mail', 'type' => \Elementor\Controls_Manager::TEXT, 'input_type' => 'email', 'default' => 'jonas.bogensperger@firebow.net', 'description' => 'Empfänger für WordPress-Mailversand. SMTP beim Hoster einrichten und Zustellung testen.'));
        $this->add_control('button_text', array('label' => 'Beschriftung', 'type' => \Elementor\Controls_Manager::TEXT, 'default' => 'Nachricht senden →'));
        $this->add_control('privacy_link', array('label' => 'Datenschutzseite', 'type' => \Elementor\Controls_Manager::URL));
        $this->end_controls_section();
        $this->start_controls_section('style', array('label' => 'Farben', 'tab' => \Elementor\Controls_Manager::TAB_STYLE));
        $this->add_control('button_background', array('label' => 'Buttonfarbe', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .fb-button' => 'background-color: {{VALUE}};')));
        $this->add_control('button_color', array('label' => 'Buttontext', 'type' => \Elementor\Controls_Manager::COLOR, 'selectors' => array('{{WRAPPER}} .fb-button' => 'color: {{VALUE}};')));
        $this->end_controls_section();
    }
    protected function render() {
        $s = $this->get_settings_for_display();
        $email = sanitize_email($s['email'] ?? '');
        if (!is_email($email)) { $email = ''; }
        $id = 'fb-form-' . $this->get_id();
        $privacy = $s['privacy_link']['url'] ?? '';
        ?>
        <div class="fb-inquiry" data-fb-inquiry data-endpoint="<?php echo esc_url(admin_url('admin-ajax.php')); ?>">
            <?php if (!$email) { ?><p class="fb-inquiry-note">Das Formular wird noch eingerichtet. Bitte ergänze im Elementor-Widget die Kontaktadresse.</p><?php } ?>
            <?php if ($email) { ?><p class="fb-inquiry-note">Du kannst uns auch direkt <a href="<?php echo esc_attr('mailto:' . $email); ?>">per E-Mail kontaktieren</a>.</p><?php } ?>
            <noscript><p>Für den Formularversand bitte JavaScript aktivieren oder den direkten Kontaktweg nutzen.</p></noscript>
            <form method="post" action="<?php echo esc_url(admin_url('admin-ajax.php')); ?>"><fieldset disabled data-configured="<?php echo $email ? 'yes' : 'no'; ?>">
                <input type="hidden" name="action" value="firebow_contact">
                <input type="hidden" name="_wpnonce" value="<?php echo esc_attr(wp_create_nonce('firebow_contact')); ?>">
                <div class="fb-form-row"><label for="<?php echo esc_attr($id); ?>-name">Dein Name <span>(optional)</span><input id="<?php echo esc_attr($id); ?>-name" name="name" autocomplete="name" maxlength="120" placeholder="Wie dürfen wir dich ansprechen?"></label><label for="<?php echo esc_attr($id); ?>-email">Deine E-Mail *<input id="<?php echo esc_attr($id); ?>-email" name="email" type="email" autocomplete="email" required maxlength="254" placeholder="Für unsere Rückmeldung"></label></div>
                <label for="<?php echo esc_attr($id); ?>-subject">Worum geht’s? *<select id="<?php echo esc_attr($id); ?>-subject" name="subject" required><option value="Allgemeine Anfrage">Eine allgemeine Frage</option><option value="Website">Eine Website gestalten</option><option value="Buchungssystem">Termine online buchbar machen</option><option value="Formular">Ein Formular einrichten</option><option value="SEO">Online besser gefunden werden</option></select></label>
                <label for="<?php echo esc_attr($id); ?>-message">Deine Nachricht *<textarea id="<?php echo esc_attr($id); ?>-message" name="message" rows="6" required minlength="10" maxlength="5000" placeholder="Erzähl uns ein bisschen mehr …"></textarea></label>
                <div class="fb-honeypot" aria-hidden="true"><label for="<?php echo esc_attr($id); ?>-website">Dieses Feld leer lassen<input id="<?php echo esc_attr($id); ?>-website" name="website" tabindex="-1" autocomplete="off"></label></div>
                <p class="fb-inquiry-note">Beim Absenden werden deine Angaben zur Bearbeitung deiner Anfrage an FireBow übermittelt. Bitte keine sensiblen Angaben senden. <?php if ($privacy) { ?><a href="<?php echo esc_url($privacy); ?>">Informationen zum Datenschutz</a><?php } ?></p>
                <button class="fb-button" type="submit"><?php echo esc_html($s['button_text'] ?? 'Nachricht senden →'); ?></button><p class="fb-inquiry-note">* Pflichtfelder</p>
            </fieldset></form>
            <p class="fb-result-status" role="status" aria-live="polite" aria-atomic="true"></p>
        </div>
        <?php
    }
}
