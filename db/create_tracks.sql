CREATE DATABASE IF NOT EXISTS `musicsyncdb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `musicsyncdb`;

CREATE TABLE IF NOT EXISTS `tracks` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
  	`url` varchar(500) NOT NULL,
  	`blob_url` varchar(500) NOT NULL,
    `name` varchar(100) NOT NULL,
    `album` varchar(100) NOT NULL,
    `artist` varchar(100) NOT NULL,
    `playlist_id` INT NOT NULL,
    `account_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

select * from tracks;
