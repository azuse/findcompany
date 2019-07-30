<?php
ini_set('display_errors',1);
error_reporting(E_ALL);
$url="http://api.map.baidu.com/geocoder?address=".$_GET['address']."&key=33X0NsFGdzK75bVRULnf3zGt4Os450GW&output=json";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
// Set so curl_exec returns the result instead of outputting it.
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
// Get the response and close the channel.
$response = curl_exec($ch);
curl_close($ch);
echo $response;
?>