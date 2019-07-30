<?php
// ini_set('display_errors',1);
// error_reporting(E_ALL);
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
mysqli_query( $conn, "TRUNCATE `findcompany`.`company`;" );
mysqli_query( $conn, "TRUNCATE `findcompany`.`baiduzhaopin`;" );
mysqli_query( $conn, "TRUNCATE `findcompany`.`maimai`;" );
mysqli_query( $conn, "TRUNCATE `findcompany`.`company_keyword`;" );

mysqli_close($conn);
echo 'success';
?>