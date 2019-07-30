<?php
ini_set('display_errors',1);
error_reporting(E_ALL);
header("Access-Control-Allow-Origin: *");
header("maxPostSize:0");
header("Content-Type: application/json");
include("mysql.php");
$conn = mysqli_connect($dbhost, $dbuser, $dbpass);
if(! $conn )
{
    die('连接失败: ' . mysqli_error($conn));
}
// 设置编码，防止中文乱码
mysqli_query($conn , "set names utf8");

$company = $_GET['company'];
$sql = "SELECT * FROM maimai WHERE company LIKE '".$company."'";
mysqli_select_db( $conn, 'findcompany' );
$retval = mysqli_query( $conn, $sql );
if(! $retval )
{
    die('无法读取数据: ' . mysqli_error($conn));
}
global $dataBuf;
$i=0;
while($row = mysqli_fetch_assoc($retval))
{
    $dataBuf[$i]["name"] = $row['name'];
    $dataBuf[$i]["position"] = $row['position'];
    $dataBuf[$i]["major"] = $row['major'];
    $dataBuf[$i]["profession"] = $row['profession'];
    $dataBuf[$i]["mmid"] = $row['mmid'];

    $i++;
}
mysqli_free_result($retval);
mysqli_close($conn);
echo json_encode($dataBuf);
?>