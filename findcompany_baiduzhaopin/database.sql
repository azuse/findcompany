create database findcompany;
use findcompany;
CREATE TABLE `baiduzhaopin` (
  `id` int(11) NOT NULL,
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
  `id` int(11) NOT NULL,
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
  `id` int(11) NOT NULL,
  `mmid` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `company` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `position` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `major` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `profession` text COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `company_keyword` (
  `keyword_id` int(11) NOT NULL,
  `company_id` int(11) DEFAULT NULL,
  `company_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `keyword` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `keyword_weight` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `findcompany`.`update_history` ( 
  `addId` INT NOT NULL , 
  `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , 
  `type` INT NOT NULL , 
  `result_count` INT NOT NULL , PRIMARY KEY (`addId`)
) ENGINE = InnoDB;
