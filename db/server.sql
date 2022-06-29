
USE `clouddb`;

CREATE TABLE IF NOT EXISTS `azureservers` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`uid` varchar(100) NOT NULL,
    `account_id` INT,
  	`subscription` varchar(100) NOT NULL,
    `resource_group` varchar(100) NOT NULL,
    `region` varchar(100) NOT NULL,
    `availability_zone` varchar(100) NOT NULL,
    `images` varchar(100) NOT NULL,
	`instance_azure_spot` varchar(100) NOT NULL,
    `sizes` varchar(100) NOT NULL,
    `authentication_type` varchar(100) NOT NULL,
	`username` varchar(100) NOT NULL,
	`password` varchar(100) NOT NULL,
    `ssh_public_key_source` varchar(1000) NOT NULL,
    `key_pair_name` varchar(100) NOT NULL,
    `stored_keys` varchar(100) NOT NULL,
    `ssh_public_key` varchar(100) NOT NULL,
    `public_inbound_ports` varchar(100) NOT NULL,
    `http` varchar(100) NOT NULL,
    `https` varchar(100) NOT NULL,
    `ssh` varchar(100) NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

