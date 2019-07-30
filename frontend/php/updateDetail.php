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

$addId = $_GET['addId'];
$sql = "select * from company where addId=".$addId." order by id desc";
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
    $dataBuf["data"][$i]['id']=$row['id'];
    $dataBuf["data"][$i]['huazhan_id']=$row['huazhan_id'];
    $dataBuf["data"][$i]['company']=$row['company'];
    $dataBuf["data"][$i]['description']=$row['description'];
    $dataBuf["data"][$i]['tag']=$row['tag'];
    $dataBuf["data"][$i]['location']=$row['location'];
    $dataBuf["data"][$i]['address']=$row['address'];
    $dataBuf["data"][$i]['homePage']=$row['homePage'];
    $dataBuf["data"][$i]['product']=$row['product'];
    $dataBuf["data"][$i]['regCapital']=$row['regCapital'];
    $dataBuf["data"][$i]['contectName']=$row['contectName'];
    $dataBuf["data"][$i]['contectPosition']=$row['contectPosition'];
    $dataBuf["data"][$i]['contectPhone']=$row['contectPhone'];
    $dataBuf["data"][$i]['contectTel']=$row['contectTel'];
    $dataBuf["data"][$i]['contectQq']=$row['contectQq'];
    $dataBuf["data"][$i]['contectEmail']=$row['contectEmail'];
    $dataBuf["data"][$i]['contectAllJson']=$row['contectAllJson'];
    $dataBuf["data"][$i]['exhibitionJson']=$row['exhibitionJson'];
    $dataBuf["data"][$i]['raw']=$row['raw'];
    $dataBuf["data"][$i]['favorite']=$row['favorite'];
    $dataBuf["data"][$i]['addDate']=$row['addDate'];
    $i++;
}
mysqli_free_result($retval);

echo json_encode($dataBuf);

?>