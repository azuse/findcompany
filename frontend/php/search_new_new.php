<?php
// ini_set('display_errors',1);
// error_reporting(E_ALL);
header("Access-Control-Allow-Origin: *");
header("maxPostSize:0");
header("Content-Type: application/json");
header("charset: utf-8");
set_time_limit(30);

$url = "http://127.0.0.1:5000/api/search";
$data = array("start" => $_POST["start"], "len" => $_POST["len"], "keyword" => $_POST["keyword"], "options" => $_POST["options"]);

// use key 'http' even if you send the request to https://...
$options = array(
    'http' => array(
        'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
        'method'  => 'POST',
        'content' => http_build_query($data),
        'timeout' => 5
    )
);
$context  = stream_context_create($options);
$result = file_get_contents($url, false, $context);
if ($result === FALSE) { 
    $data = [];
    $data['error'] = 1;
    $result = json_encode($data); 
}

echo $result;

?>