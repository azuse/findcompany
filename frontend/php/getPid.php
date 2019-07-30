<?php

ini_set('display_errors',1);
error_reporting(E_ALL);

$pid = file("/crawler/mainPID.txt", FILE_IGNORE_NEW_LINES);
$running = posix_kill($pid[0], 0);

$dataBuf['pid'] = $pid;
$dataBuf['now'] = time();
$dataBuf['running'] = $running;
if(posix_get_last_error()!=0){
    $dataBuf['posix_strerror'] = posix_strerror(posix_get_last_error());
}

echo json_encode($dataBuf);


?>