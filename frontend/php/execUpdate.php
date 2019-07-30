<?php

ini_set('display_errors',1);
error_reporting(E_ALL);

$scriptDir = "/crawler";
$mainScript = "crawler_main.py";
$huazhanScript = "crawler_huazhanyun.py";
$descriptionScript = "crawler_huazhanyun_description.py";
$hireinfoScript = "crawler_huazhanyun_hireinfo.py";
$maimaiScript = "crawler_maimai.py";

$updateType = $_GET['type'];
if($updateType == "main") #1
{
    $command = "cd ".$scriptDir." && nohup python3 ".$mainScript." 1>/dev/null 2>&1 &";
    $output = shell_exec($command);
    echo "success";

}
if($updateType == "huazhan") #2
{
    $command = "cd ".$scriptDir." && nohup python3 ".$huazhanScript." 1>/dev/null 2>&1 &";
    $output = shell_exec($command);

    echo "success";

}
if($updateType == "description") #3
{
    $command = "cd ".$scriptDir." && nohup python3 ".$descriptionScript." 1>/dev/null 2>&1 &";
    $output = shell_exec($command);
    echo "success";

}
if($updateType == "hireinfo") #4
{
    $command = "cd ".$scriptDir." && nohup python3 ".$hireinfoScript." 1>/dev/null 2>&1 &";
    $output = shell_exec($command);
    echo "success";

}
if($updateType == "maimai") #5
{
    $command = "cd ".$scriptDir." && nohup python3 ".$maimaiScript." 1>/dev/null 2>&1 &";
    $output = shell_exec($command);
    echo "success";

}


?>