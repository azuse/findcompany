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

$options = json_decode($_POST['options'], true);
// print_r($options);
if ($options['hasContect'])
    $hasContect = " AND (contectPhone NOT LIKE '' OR contectTel NOT LIKE '') ";
else
    $hasContect = " ";

if ($options['hasAddress'])
    $hasAddress = " AND address NOT LIKE 'None' ";
else
    $hasAddress = "";

if ($options['hasHomePage'])
    $hasHomePage = " AND homePage NOT LIKE '' AND homePage NOT LIKE 'None' ";
else
    $hasHomePage = "";

if ($options['notLeagal'])
    $notLeagal = " AND contectPosition NOT LIKE '%法人%' ";
else
    $notLeagal = "";

if ($options['sort'] == 'timeDESC')
    $sort = " ORDER BY id DESC LIMIT ".$_POST['start'].",".$_POST['len']." ";
else if($options['sort'] == 'timeASC')
    $sort = " ORDER BY id ASC LIMIT ".$_POST['start'].",".$_POST['len']." ";
else
    $sort = " LIMIT ".$_POST['start'].",".$_POST['len']." ";

$city = " AND ( 0";
if ($options['shanghai'])
    $city = $city." OR location LIKE '%上海%' ";
if ($options['beijing'])
    $city = $city." OR location LIKE '%北京%' ";
if ($options['guangzhou'])
    $city = $city." OR location LIKE '%广州%' ";
if ($options['shenzhen'])
    $city = $city." OR location LIKE '%深圳%' ";
if ($options['otherCities'])
    $city = $city." OR (location NOT LIKE '%上海%' AND location NOT LIKE '%北京%' AND  location NOT LIKE '%广州%' AND location NOT LIKE '%深圳%') ";
if (!$options['shanghai'] && !$options['beijing'] && !$options['guangzhou'] && !$options['shenzhen'] && !$options['otherCities'])
    $city = $city." OR 1 ";
$city = $city.") ";
    
$keyWord = $_POST['keyword'];

$sql = "SELECT * FROM company WHERE company LIKE '%公司%' AND company LIKE '%".$keyWord."%'" .$hasContect.$hasAddress.$hasHomePage.$notLeagal.$city.$sort.";";
// echo $sql;
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

$sql = "SELECT COUNT(id) count FROM company WHERE company LIKE '%".$keyWord."%'" .$hasContect.$hasAddress.$hasHomePage.$notLeagal.$city.$sort.";";
mysqli_select_db( $conn, 'findcompany' );
$retval = mysqli_query( $conn, $sql );
if(! $retval )
{
    die('无法读取数据: ' . mysqli_error($conn));
}
while($row = mysqli_fetch_assoc($retval))
{
    $dataBuf["resultNumber"] = $row['count'];
}
mysqli_free_result($retval);
mysqli_close($conn);
echo json_encode($dataBuf);
?>