<?php
if (!defined('ABSPATH')) { exit; }

// The recipient comes only from the published contact page, never from submitted fields.
function gaustadt_submit_inquiry($input, $address) {
    if (!isset($input['_wpnonce']) || !is_scalar($input['_wpnonce']) || !wp_verify_nonce((string) $input['_wpnonce'], 'gaustadt_contact')) {
        return new WP_Error('nonce', 'Bitte lade die Seite neu und versuche es noch einmal.', array('status' => 403));
    }
    foreach (array('name', 'email', 'subject', 'message', 'website') as $key) {
        if (isset($input[$key]) && !is_string($input[$key])) { return new WP_Error('invalid', 'Bitte prüfe deine Eingaben.', array('status' => 400)); }
    }
    if (!empty($input['website'])) { return new WP_Error('spam', 'Die Anfrage konnte nicht verarbeitet werden.', array('status' => 400)); }
    $settings = gaustadt_page_widget_settings('kontakt', 'gaustadt-inquiry');
    $recipient = sanitize_email($settings['email'] ?? '');
    if (!is_email($recipient)) { return new WP_Error('configuration', 'Das Kontaktformular ist noch nicht eingerichtet. Bitte nutze den anderen Kontaktweg.', array('status' => 503)); }
    $name = trim($input['name'] ?? ''); $email = trim($input['email'] ?? '');
    $subject = $input['subject'] ?? ''; $message = trim($input['message'] ?? '');
    $subjects = array('Allgemeine Anfrage', 'Auftrittsanfrage', 'Mitmachen', 'Unterstützung');
    if (mb_strlen($name) > 120 || strlen($email) > 254 || !is_email($email) || preg_match('/[\r\n]/', $email)
        || !in_array($subject, $subjects, true) || mb_strlen($message) < 10 || mb_strlen($message) > 5000) {
        return new WP_Error('invalid', 'Bitte gib eine gültige E-Mail und eine Nachricht mit 10 bis 5000 Zeichen an.', array('status' => 400));
    }
    // Short-lived abuse counters contain a keyed hash, no raw IP or message content.
    // Use REMOTE_ADDR only; an untrusted forwarding header must not bypass the limit.
    $key = 'gaustadt_contact_' . hash_hmac('sha256', (string) $address, wp_salt('nonce'));
    $count = (int) get_transient($key);
    if ($count >= 5) { return new WP_Error('rate', 'Zu viele Versuche. Bitte versuche es in einer Stunde erneut.', array('status' => 429)); }
    set_transient($key, $count + 1, HOUR_IN_SECONDS);
    $body = 'Anliegen: ' . $subject . "\nName: " . sanitize_text_field($name) . "\nE-Mail: " . $email . "\n\n" . sanitize_textarea_field($message);
    // WordPress/SMTP supplies From; the visitor is Reply-To, avoiding sender spoofing.
    $sent = wp_mail($recipient, 'Blaskapelle Gaustadt: ' . $subject, $body, array('Content-Type: text/plain; charset=UTF-8', 'Reply-To: ' . $email));
    if (!$sent) { return new WP_Error('mail', 'Der Versand hat nicht funktioniert. Bitte kontaktiere uns direkt per E-Mail.', array('status' => 502)); }
    return true; // Accepted by the mail transport; delivery to the inbox is not guaranteed.
}

function gaustadt_contact_ajax() {
    $result = gaustadt_submit_inquiry(wp_unslash($_POST), $_SERVER['REMOTE_ADDR'] ?? '');
    if (is_wp_error($result)) {
        $data = $result->get_error_data();
        wp_send_json_error(array('message' => $result->get_error_message()), (int) ($data['status'] ?? 400));
    }
    wp_send_json_success(array('message' => 'Danke! Deine Nachricht wurde an unser E-Mail-System zum Versand übergeben.'));
}
add_action('wp_ajax_gaustadt_contact', 'gaustadt_contact_ajax');
add_action('wp_ajax_nopriv_gaustadt_contact', 'gaustadt_contact_ajax');
