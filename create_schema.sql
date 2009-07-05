CREATE DATABASE IF NOT EXISTS gpr;

use gpr;

DROP TABLE IF EXISTS filtered_results;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS files;

CREATE TABLE files (
    id              INT NOT NULL AUTO_INCREMENT,
    filename        VARCHAR(512),
    loaded          TIMESTAMP,
    PRIMARY KEY (id)       
) ENGINE=InnoDB;

CREATE TABLE results (
    rid           INT NOT NULL AUTO_INCREMENT,
    file_id       INT NOT NULL, 
    `Block`       FLOAT,
    `Column`      FLOAT,
    `Row`         FLOAT,
    `Name`        VARCHAR(255),
    `ID`          VARCHAR(255),
    `X`           FLOAT,
    `Y`           FLOAT,
    `Dia.`        FLOAT,
    `F635 Median` FLOAT,
    `F635 Mean` FLOAT,
    `F635 SD` FLOAT,
    `F635 CV` FLOAT,
    `B635` FLOAT,
    `B635 Median` FLOAT,
    `B635 Mean` FLOAT,
    `B635 SD` FLOAT,
    `B635 CV` FLOAT,
    `% > B635+1SD` FLOAT,
    `% > B635+2SD` FLOAT,
    `F635 % Sat.` FLOAT,
    `F532 Median` FLOAT,
    `F532 Mean` FLOAT,
    `F532 SD`                    FLOAT,  
    `F532 CV`                    FLOAT,
    `B532`                       FLOAT,
    `B532 Median`                FLOAT,
    `B532 Mean`                  FLOAT,
    `B532 SD`                    FLOAT,
    `B532 CV`                    FLOAT,
    `% > B532+1SD`               FLOAT,
    `% > B532+2SD`               FLOAT,
    `F532 % Sat.`                FLOAT,
    `Ratio of Medians (635/532)` FLOAT,
    `Ratio of Means (635/532)`   FLOAT,
    `Median of Ratios (635/532)` FLOAT,
    `Mean of Ratios (635/532)`   FLOAT,
    `Ratios SD (635/532)`        FLOAT,
    `Rgn Ratio (635/532)`        FLOAT,
    `Rgn R2 (635/532)`           FLOAT,
    `F Pixels`                   FLOAT,
    `B Pixels`                   FLOAT,
    `Circularity`                FLOAT,
    `Sum of Medians (635/532)`   FLOAT,
    `Sum of Means (635/532)`     FLOAT,
    `Log Ratio (635/532)`        FLOAT,
    `F635 Median - B635`         FLOAT,
    `F532 Median - B532`         FLOAT,
    `F635 Mean - B635`           FLOAT,
    `F532 Mean - B532`           FLOAT,
    `F635 Total Intensity`       FLOAT,
    `F532 Total Intensity`       FLOAT,
    `SNR 635`                    FLOAT,
    `SNR 532` FLOAT,
    `Flags` FLOAT,
    `Normalize` FLOAT,
    `Autoflag` FLOAT,
    `RefNumber` FLOAT,
    `ControlType` VARCHAR(500),
    `GeneName`    VARCHAR(500),
    `TopHit`      VARCHAR(500),
    `Description` VARCHAR(500),
    PRIMARY KEY (rid),
    FOREIGN KEY (file_id) REFERENCES files(id)
) ENGINE=InnoDB;

CREATE TABLE filtered_results (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    file_id INT NOT NULL,
    `Ratio of Medians (635/532)` float NOT NULL,
    `F635 Median - B635` float NOT NULL,
    description     TEXT,
    PRIMARY KEY (id)
--    CONSTRAINT UNIQUE (name, file_id)
) ENGINE=InnoDB;


