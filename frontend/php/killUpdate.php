<?php

ini_set('display_errors',1);
error_reporting(E_ALL);

$pid = file("/crawler/mainPID.txt", FILE_IGNORE_NEW_LINES);
$killed = posix_kill($pid[0], 9);

$dataBuf['pid'] = $pid[0];
$dataBuf['killed'] = $killed;


echo json_encode($dataBuf);
?>