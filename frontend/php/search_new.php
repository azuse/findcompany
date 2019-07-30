<?php
$msc_all = microtime(true);

ini_set('display_errors',1);
error_reporting(E_ALL);
header("Access-Control-Allow-Origin: *");
header("maxPostSize:0");
header("Content-Type: application/json");
header("charset: utf-8");
include("mysql.php");
$conn = mysqli_connect($dbhost, $dbuser, $dbpass);
// $_POST = json_decode('{"start":"0","len":"20","keyword":"","options":"{\"hasContect\":1,\"hasAddress\":1,\"hasHomePage\":1,\"notLeagal\":1,\"inFavorite\":1,\"notFavorite\":1,\"sort\":\"timeDESC\",\"shanghai\":0,\"beijing\":0,\"guangzhou\":0,\"shenzhen\":0,\"otherCities\":0}"}', true);
if(! $conn )
{
    die('连接失败: ' . mysqli_error($conn));
}
// 设置编码，防止中文乱码
mysqli_query($conn , "set names utf8");

$options = json_decode($_POST['options'], true);
if ($options['hasContect'])
    $hasContect = 1;
else
    $hasContect = 0;

if ($options['hasAddress'])
    $hasAddress = 1;
else
    $hasAddress = 0;

if ($options['hasHomePage'])
    $hasHomePage = 1;
else
    $hasHomePage = 0;

if ($options['notLeagal'])
    $notLeagal = 1;
else
    $notLeagal = 0;

if ($options['sort'] == 'timeDESC')
{
    $sort = 'id';
    $isasc = 0;
}
else if($options['sort'] == 'timeASC')
{
    $sort = 'id';
    $isasc = 1;
}

$isCompany = 1;
$start = $_POST['start'];
$len = $_POST['len'];
$keyWord = $_POST['keyword'];
global $dataBuf;
global $count;
$count = 0;
$i=0;

mysqli_select_db( $conn, 'findcompany' );

mysqli_query( $conn, "call clear_cities()");
if ($options['shanghai'])
    mysqli_query( $conn, "call add_city('上海')");
if ($options['beijing'])
    mysqli_query( $conn, "call add_city('北京')");
if ($options['guangzhou'])
    mysqli_query( $conn, "call add_city('广州')");
if ($options['shenzhen'])
    mysqli_query( $conn, "call add_city('深圳')");
if ($options['otherCities'])
    mysqli_query( $conn, "call add_city('')");
if (!$options['shanghai'] && !$options['beijing'] && !$options['guangzhou'] && !$options['shenzhen'] && !$options['otherCities'])
    mysqli_query( $conn, "call add_city('')");

$msc = microtime(true);
$sql = sprintf("call search_all('%s',%d,%d,%d,%d,%d,%d,%d,%d,%d);", $keyWord, $sort, $isasc, $hasContect, $hasAddress, $hasHomePage, $notLeagal, $isCompany, $start, $len);
$msc = microtime(true)-$msc;
$dataBuf["mysqlquery"] = $sql;
$dataBuf["mysqltime"] = $msc;
$dataBuf["time at mysql"] = microtime(true) - $msc_all;
$retval1 = mysqli_query( $conn, $sql );

$msc = microtime(true);
while($row = mysqli_fetch_assoc($retval1))
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
mysqli_free_result($retval1);
$dataBuf['result1'] = microtime(true) - $msc;

$msc = microtime(true);
mysqli_next_result($conn);
$retval2 = mysqli_use_result($conn);
$row = mysqli_fetch_assoc($retval2);
$dataBuf['result2'] = microtime(true) - $msc;

mysqli_close($conn);
$dataBuf["resultNumber"] = $row['count'];

$msc_all = microtime(true)-$msc_all;
$dataBuf["time"] = $msc_all;

echo json_encode($dataBuf);
?>