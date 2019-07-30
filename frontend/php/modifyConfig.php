<?php
ini_set('display_errors',1);
error_reporting(E_ALL);

$func = $_POST['func'];
$scriptDir = "/crawler/";
if($func == 'read')
{
    $string = file_get_contents($scriptDir."crawler_config.json");
    echo $string;
}
if($func == 'write')
{
    $string = file_get_contents($scriptDir."crawler_config.json");
    $keywords = json_decode($_POST['keywords'], true);
    $time_sleep = $_POST['time_sleep'];
    $json = json_decode($string, true);
    $json['BAIDU']['keywords'] = $keywords;
    $json['HUAZHAN']['keywords'] = $keywords;
    $json['BAIDU']['time_sleep'] = $time_sleep;
    $json['HUAZHAN']['time_sleep'] = $time_sleep;
    $json['MAIMAI']['time_sleep'] = $time_sleep;
    $string = json_encode($json);
    file_put_contents($scriptDir."crawler_config.json", $string);
    echo "success";
}

?>