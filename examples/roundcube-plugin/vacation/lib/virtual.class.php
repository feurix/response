<?php
/*
 * Note: This code is basically a cleanup up, stripped down copy of
 *       Jasper Slits' original work for the rcubevacation plugin.
 *
 * The changes from the original include:
 *
 *      - Getting rid of the variable holding the database name.
 *        This is not needed and can be placed directly into the DSN.
 *      - Removing hardcoded SQL queries, putting them into the
 *        configuration file instead. (sql_read, sql_write)
 *      - Changing parameter names of SQL queries
 *      - Add default values for enabled, subject and message to config
 *      - Again, indentation and whitespace cleanup...
 *
 */

class Virtual extends VacationDriver {
    private $db;

    public function init() {
        if (empty($this->cfg['dsn'])) {
            $this->db = $this->rcmail->db;
            $dsn = MDB2::parseDSN($this->rcmail->config->get('db_dsnw'));
        } else {
            $this->db = new rcube_mdb2($this->cfg['dsn'], '', FALSE);
            $this->db->db_connect('w');
            $this->db->set_debug((bool)$this->rcmail->config->get('sql_debug'));
            $dsn = MDB2::parseDSN($this->cfg['dsn']);
        }
    }

    /*
     * @return Array Values for the form
     */
    public function _get() {
        $vacArr = array("enabled"=>0, "subject"=>"", "body"=>"");

        $sql = $this->cfg['sql_read'];
        $sql = str_replace('%address', $this->user->data['username'], $sql);
        $res = $this->db->query($sql);

        if ($row = $this->db->fetch_assoc($res)) {
            $vacArr['enabled'] = $row['enabled'];
            $vacArr['subject'] = $row['subject'];
            $vacArr['message'] = $row['message'];
        } else {
            $vacArr['enabled'] = $this->cfg['default_enabled'];
            $vacArr['subject'] = $this->cfg['default_subject'];
            $vacArr['message'] = $this->cfg['default_message'];
        }
        return $vacArr;
    }

    /*
     * @return boolean True on success, false on failure
     */
    public function setVacation() {
        $sql = $this->cfg['sql_write'];

        if ($this->enabled && ($this->message == "" || $this->subject == ""))
            return FALSE;

        $sql = str_replace('%address', $this->user->data['username'], $sql);
        $sql = str_replace('%enabled', $this->enabled, $sql);

        /* May contain quotes, so let's handle them sanely. */
        $sql = str_replace('%subject', mysql_real_escape_string($this->subject), $sql);
        $sql = str_replace('%message', mysql_real_escape_string($this->message), $sql);

        $this->db->query($sql);

        return TRUE;
    }

    public function __destruct() {
        if (! empty($this->cfg['dsn']) && is_resource($this->db)) {
            $this->db = null;
        }
    }
}

?>
