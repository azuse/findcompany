<?php
ini_set('display_errors',1);
error_reporting(E_ALL);
header("Access-Control-Allow-Origin: *");
header("maxPostSize:0");
header("Content-Type: application/json");
header("charset: utf-8");
include("mysql.php");
$conn = mysqli_connect($dbhost, $dbuser, $dbpass);
if(! $conn )
{
    die('连接失败: ' . mysqli_error($conn));
}
// 设置编码，防止中文乱码
mysqli_query($conn , "set names utf8");

mysqli_select_db( $conn, 'findcompany' );

$sql = "select * from update_history order by addId desc";
$retval = mysqli_query( $conn, $sql );
if(! $retval )
{
    die('无法读取数据: ' . mysqli_error($conn));
}
global $dataBuf;
global $i;
$i = 0;
while($row = mysqli_fetch_assoc($retval))
{
    $dataBuf[$i]["addId"] = $row["addId"];
    $dataBuf[$i]["date"] = $row["date"];
    $dataBuf[$i]["type"] = $row["type"];
    $dataBuf[$i]["result_count"] = $row["result_count"];
    $i++;
}
mysqli_free_result($retval);


echo json_encode($dataBuf);

?>