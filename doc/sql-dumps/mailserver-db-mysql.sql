SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `mailserver`
--

-- --------------------------------------------------------

--
-- Table structure for table `virtual_aliases`
--

CREATE TABLE IF NOT EXISTS `virtual_aliases` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_id` int(11) NOT NULL,
  `source` varchar(100) NOT NULL,
  `destination` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `domain_id` (`domain_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `virtual_aliases`
--


-- --------------------------------------------------------

--
-- Table structure for table `virtual_domains`
--

CREATE TABLE IF NOT EXISTS `virtual_domains` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `virtual_domains`
--

INSERT INTO `virtual_domains` (`id`, `name`) VALUES
(1, 'example.com');

-- --------------------------------------------------------

--
-- Table structure for table `virtual_users`
--

CREATE TABLE IF NOT EXISTS `virtual_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_id` int(11) NOT NULL,
  `password` varchar(32) NOT NULL,
  `email` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `domain_id` (`domain_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=4309 ;

--
-- Dumping data for table `virtual_users`
--

INSERT INTO `virtual_users` (`id`, `domain_id`, `password`, `email`) VALUES
(1, 1, 'aeb88d08a2a42d36c0dad3ccb47d5e27', 'mail@example.com');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `virtual_aliases`
--
ALTER TABLE `virtual_aliases`
  ADD CONSTRAINT `virtual_aliases_ibfk_1` FOREIGN KEY (`domain_id`) REFERENCES `virtual_domains` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `virtual_users`
--
ALTER TABLE `virtual_users`
  ADD CONSTRAINT `virtual_users_ibfk_1` FOREIGN KEY (`domain_id`) REFERENCES `virtual_domains` (`id`) ON DELETE CASCADE;
