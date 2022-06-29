USE `clouddb`;
drop table azurelogs;

CREATE TABLE IF NOT EXISTS `azurelogs` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`azureservers_id` varchar(100) NOT NULL,
    `account_id` INT,
  	`service` varchar(100) NOT NULL,
    `creation_date` varchar(100) NOT NULL,
    `creation_time` varchar(100) NOT NULL,
    `uptime` varchar(100) NOT NULL,
    `status` varchar(100) NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

select * from azurelogs;
