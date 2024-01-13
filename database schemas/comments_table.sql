CREATE TABLE `comments` (
  `id` INT PRIMARY KEY,
  `user` TEXT,
  `article_id` INT,
  `comment` TEXT,
  `comment_title` TEXT,
  `comment_date` TIMESTAMP
);
