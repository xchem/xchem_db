--
-- Add field comment to reviewresponses2
--
ALTER TABLE `review_responses_new` ADD COLUMN `comment` longtext NULL;
--
-- Create model SWStatuschange
--
CREATE TABLE `xchem_db_swstatuschange` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `date` date NOT NULL, `activation` bool NOT NULL, `source_well_id` integer NOT NULL);
--
-- Create model PlateOpening
--
CREATE TABLE `xchem_db_plateopening` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `date` date NOT NULL, `reason` longtext NULL, `plate_id` integer NOT NULL);
ALTER TABLE `xchem_db_swstatuschange` ADD CONSTRAINT `xchem_db_swstatuscha_source_well_id_e63d62ff_fk_xchem_db_` FOREIGN KEY (`source_well_id`) REFERENCES `xchem_db_sourcewell` (`id`);
ALTER TABLE `xchem_db_plateopening` ADD CONSTRAINT `xchem_db_plateopenin_plate_id_3adbfd48_fk_xchem_db_` FOREIGN KEY (`plate_id`) REFERENCES `xchem_db_libraryplate` (`id`);
