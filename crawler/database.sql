create database findcompany;
use findcompany;
CREATE TABLE `baiduzhaopin` (
  `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `sid` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `jobName` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `company` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `depart` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `education` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `employerType` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `experience` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `label` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `jobClass` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `salary` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `location` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `companyAddress` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `companyDescription` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `companySize` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `companyId` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `rowData` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `queryWord` text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `company` (
  `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `huazhan_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `company` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `tag` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `location` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `homePage` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `product` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `regCapital` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `contectName` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `contectPosition` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `contectPhone` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `contectTel` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `contectQq` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `contectEmail` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `contectAllJson` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `exhibitionJson` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `raw` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `favorite` int(11) NOT NULL DEFAULT '0',
  `addDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `addId` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `maimai` (
  `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `mmid` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `company` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `position` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `major` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `profession` text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `company_keyword` (
  `keyword_id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `company_id` int(11) DEFAULT NULL,
  `company_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `keyword` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `keyword_weight` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `findcompany`.`update_history` ( 
  `addId` INT NOT NULL, 
  `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , 
  `type` INT NOT NULL , 
  `result_count` INT NOT NULL , PRIMARY KEY (`addId`)
) ENGINE = InnoDB;


use findcompany;

drop procedure if exists search_all;
delimiter $$
create procedure search_all(
                            IN query TEXT CHARSET utf8,
                            IN sort TEXT CHARSET utf8, 
                            IN isasc INT, 
                            IN hasContect INT, 
                            IN hasAddress INT,
                            IN hasHomePage INT,
                            IN notLeagal INT,
                            IN iscompany INT,
                            IN start INT,
                            IN length INT)
begin
    drop table if exists tmp_company_result;
    create table tmp_company_result as (
        select 
                id
        from company 
        where (company LIKE concat("%",query,"%") or tag LIKE concat("%",query,"%") or description LIKE concat("%",query,"%"))
        and (case when iscompany = 1 then (company LIKE '%公司%') else 1 end)
        and (case when hasContect = 1 then (contectPhone NOT LIKE '' OR contectTel NOT LIKE '') else 1 end)
        and (case when hasAddress = 1 then (address NOT LIKE 'None' ) else 1 end)
        and (case when hasAddress = 1 then (address NOT LIKE 'None' ) else 1 end)
        and (case when hasHomePage = 1 then (homePage NOT LIKE '' AND homePage NOT LIKE 'None' ) else 1 end)
        and (case when notLeagal = 1 then (contectPosition NOT LIKE '%法人%' ) else 1 end)
    );



    drop table if exists tmp_keyword_result;
    create table tmp_keyword_result as
    (select company_id from company_keyword
    where keyword like concat("%",query,"%")
    group by company_id,keyword_weight
    );



    drop table if exists tmp_keyword_result_company;
    create table tmp_keyword_result_company as (
        select 
                id
        from company,tmp_keyword_result
        where company.id=tmp_keyword_result.company_id
        and (case when iscompany = 1 then (company LIKE '%公司%') else 1 end)
        and (case when hasContect = 1 then (contectPhone NOT LIKE '' OR contectTel NOT LIKE '') else 1 end)
        and (case when hasAddress = 1 then (address NOT LIKE 'None' ) else 1 end)
        and (case when hasAddress = 1 then (address NOT LIKE 'None' ) else 1 end)
        and (case when hasHomePage = 1 then (homePage NOT LIKE '' AND homePage NOT LIKE 'None' ) else 1 end)
        and (case when notLeagal = 1 then (contectPosition NOT LIKE '%法人%' ) else 1 end)
    );

    drop table if exists tmp_union;
    create table tmp_union
    select * from tmp_company_result
    union 
    select * from tmp_keyword_result_company;

    select distinct company.id, huazhan_id, company, 
                description, tag, location, 
                address, homePage, product, 
                regCapital, contectName, contectPosition, 
                contectPhone, contectTel, contectQq, 
                contectEmail, contectAllJson, exhibitionJson, 
                raw, favorite, addDate, 
                addId 
    from tmp_union, company, cities
    where tmp_union.id = company.id and company.location like concat("%", cities.city, "%")
    order by 
    (case when isasc = 1 then addDate end) asc,
    (case when isasc = 0 then addDate end) desc
    limit start,length;

    select distinct count(*) count from tmp_union, company, cities
    where tmp_union.id = company.id and company.location like concat("%", cities.city, "%");
    drop table if exists tmp_keyword_result, tmp_company_result, tmp_keyword_result_company, tmp_union, cities;
end
$$
delimiter ;

 drop procedure if exists clear_cities;
delimiter $$
create procedure clear_cities()
begin
    drop table if exists cities;
    create table cities(city text);
    truncate cities;
end
$$
delimiter ;

drop procedure if exists add_city;
delimiter $$
create procedure add_city(IN cityname TEXT)
begin
    insert into cities(city) values (cityname);
end
$$
delimiter ;

-- 正确的搜索顺序：
-- 清空/创建待搜索城市表
-- call clear_cities();
-- 根据需要添加城市
-- call add_city("城市名");
-- 执行搜索
-- call search_all( query       关键词["关键词"], 
--                  sort        排序列[id, company 公司名, location 地点, addDate 添加时间, addId 添加操作id], 
--                  isasc       是否正序[1 asc, 0 desc],
--                  hasContact  有联系人[1 有, 0 无限制],
--                  hasAddress  有地址[1 有, 0 无限制],
--                  hasHomepage 有主页[1 有, 0 无限制],
--                  notLeagal   联系人不是法人[1 不是法人, 0 无限制],
--                  iscompany   公司名称中含有公司两字（排除一些社会组织 杂志社）[1 公司名字含有‘公司’, 0 无限制],
--                  start       从总结果的第几行开始返回,
--                  len         返回的行数
--                  );
-- 此过程返回两个结果,先返回搜索结果的数据,后返回搜索结果的总个数 


-- 测试
-- drop table if exists cities;
-- create table cities(city text);
-- insert into cities(city) values ("");
-- call search_all("",1,1,1,1,1,1,1,1,10);