<?php
abstract class VacationDriver {
    protected $cfg = array();
    protected $rcmail,$user,$message,$subject,$enabled;

    abstract public function _get();
    abstract public function init();
    abstract protected function setVacation();

    // Provide easy access for the drivers to frequently used objects
    public function __construct() {
        $this->rcmail = rcmail::get_instance();
        $this->user = $this->rcmail->user;
        $this->identity = $this->user->get_identity();
        $this->cfg = $this->rcmail->config->get( strtolower( get_class($this) ) );
    }

    /*
     * @return boolean True on succes, false on failure
     */
    final public function save() {
        $this->enabled = get_input_value('_vacation_enabled', RCUBE_INPUT_POST) ? 1 : 0;
        $this->subject = get_input_value('_vacation_subject', RCUBE_INPUT_POST);
        $this->message = get_input_value('_vacation_message', RCUBE_INPUT_POST);

        // This method performs the actual work
        return $this->setVacation();

    }
}?>
