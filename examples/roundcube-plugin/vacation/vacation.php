<?php
/*
 * Note: This code is basically a cleanup up, stripped down copy of
 *       Jasper Slits' original work for the rcubevacation plugin.
 *
 * The changes from the original include:
 *
 *      - Removal of unneeded fields (forwards, keepcopy, ...)
 *      - Some style and JS related changes
 *      - Indentation and whitespace cleanup
 *
 * The original file header contained:
 *
 *     Vacation plugin that adds a new tab to the settings section
 *     to enable forward / out of office replies.
 *
 *     @package plugins
 *     @uses    rcube_plugin
 *     @author  Jasper Slits <jaspersl@gmail.com>
 *     @version 1.6
 *     @license GPL
 *     @link    https://sourceforge.net/projects/rcubevacation/
 *
 */

// Load available drivers.
require 'lib/vacationdriver.class.php';
require 'lib/virtual.class.php';

class vacation extends rcube_plugin {
    public $task = 'settings';
    private $v = "";

    public function init() {
        $this->add_texts('localization/', array('vacation'));
        $this->load_config();
        $driver = rcmail::get_instance()->config->get("driver");

        $this->register_action('plugin.vacation', array($this, 'vacation_init'));
        $this->register_action('plugin.vacation-save', array($this, 'vacation_save'));
        $this->register_handler('plugin.vacation_form', array($this, 'vacation_form'));
        $this->include_script('vacation.js');

        $this->v = VacationDriverFactory::Create( $driver );
    }

    public function vacation_init() {
        $this->add_texts('localization/',array('vacation'));
        $rcmail = rcmail::get_instance();
        $rcmail->output->set_pagetitle($this->gettext('vacation'));
        $rcmail->output->send('vacation.vacation');
    }

    public function vacation_save() {
        $rcmail = rcmail::get_instance();
        $this->v->init();
        if ( $this->v->save() ) {
            $rcmail->output->show_message($this->gettext("success_changed"), 'confirmation');
        } else {
            $rcmail->output->show_message($this->gettext("failed"), 'error');
        }
        $this->vacation_init();
    }

    public function vacation_form() {
        $rcmail = rcmail::get_instance();

        $this->v->init();
        $settings = $this->v->_get();

        $rcmail->output->add_script("var settings_account=true;");
        $rcmail->output->set_env('product_name', $rcmail->config->get('product_name'));

        $attrib = "";
        $attrib_str = create_attrib_string($attrib, array('style', 'class', 'id', 'cellpadding', 'cellspacing', 'border', 'summary'));

        $out = '<table' . $attrib_str . ">\n\n";

        $field_id = 'vacation_enabled';
        $input_autoresponderenabled = new html_checkbox(array('name' => '_vacation_enabled', 'id' => $field_id, 'value' => 1));
        $out .= sprintf("<tr><td class=\"title\"><label for=\"%s\">%s</label>:</td><td>%s</td></tr>\n",
            $field_id,
            rep_specialchars_output($this->gettext('autoreplyenabled')),
            $input_autoresponderenabled->show($settings['enabled']));

        $field_id = 'vacation_subject';
        $input_autorespondersubject = new html_inputfield(array('name' => '_vacation_subject', 'id' => $field_id, 'size' => 50));
        $out .= sprintf("<tr><td valign=\"top\" class=\"title\"><label for=\"%s\">%s</label>:</td><td>%s</td></tr>\n",
            $field_id,
            rep_specialchars_output($this->gettext('autoreplysubject')),
            $input_autorespondersubject->show($settings['subject']));

        $field_id = 'vacation_message';
        $input_autorespondermessage = new html_textarea(array('name' => '_vacation_message', 'id' => $field_id, 'cols' => 48, 'rows' => 15));
        $out .= sprintf("<tr><td valign=\"top\" class=\"title\"><label for=\"%s\">%s</label>:</td><td>%s</td></tr>\n",
            $field_id,
            rep_specialchars_output($this->gettext('autoreplymessage')),
            $input_autorespondermessage->show($settings['message']));

        $out .= "\n</table>";

        $rcmail->output->add_gui_object('vacationform', 'vacation-form');
        return $out;
    }
}

/*
 * Using factory method to create an instance of the driver
 *
 */

class VacationDriverFactory {

    /*
     * @param string driver class to be loaded
     * @return object specific driver
     *
     *
     */

    public static function Create( $driver ) {
        $driver = strtolower($driver);

        if (! file_exists("plugins/vacation/lib/".$driver.".class.php")) {
            raise_error(array(
                'code' => 600,
                'type' => 'php',
                'file' => __FILE__,
                'message' => "Vacation plugin: Driver {$driver} does not exist"
            ),true, true);
        }
        return new $driver;
    }
}

?>
