<?php
/*
 * Basic virtual vacation example plugin using the RESPONSE-PROJECT :-)
 * URL: http://feurix.org/projects/response/
 *
 * WARNING: Check the permissions of this file after editing it!
 *          No one except the user running roundcube (e.g. www-data, ...)
 *          should be able to read it.
 */

$rcmail_config['driver'] = 'virtual';

$rcmail_config['virtual']['default_enabled'] = 0;
$rcmail_config['virtual']['default_subject'] = "Out of Office";
$rcmail_config['virtual']['default_message'] = "Sorry, I'm on vacation this week.";

/* please change this */
$rcmail_config['virtual']['dsn'] = 'mysql://responserc:FIXME@localhost/response';

$rcmail_config['virtual']['sql_read'] =
          "SELECT `config`.`enabled` AS `enabled`, " .
          "`config`.`expires`        AS `expires`, " .
          "`config`.`subject`        AS `subject`, " .
          "`config`.`message`        AS `message` " .
          "FROM `autoresponse_config` `config` " .
          "WHERE `config`.`address` = '%address'";

/* TODO
 * As soon as we have a usable datetime widget the user may set an expiry date
 * on his own! For now, the hardcoded limit is one month in the future to
 * prevent lazy users forgetting about their autoresponse config.
 */
$rcmail_config['virtual']['sql_write'] =
        "INSERT INTO `autoresponse_config` " .
        "(`address`,`enabled`,`changed`,`expires`,`subject`,`message`) " .
        "VALUES ('%address', %enabled, NOW(), CURDATE() + INTERVAL 30 DAY, " .
        "'%subject', '%message') " .
        "ON DUPLICATE KEY UPDATE `enabled` = %enabled, `changed` = NOW(), " .
        "`expires` = CURDATE() + INTERVAL 30 DAY, `subject` = '%subject', " .
        "`message` = '%message'";
?>
