<?php

ini_set('display_errors',1);
error_reporting(E_ALL);

$log = file("/crawler/crawler_log.txt");

foreach ($log as $line_num => $line) {
    echo $line;
}
?>