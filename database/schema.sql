-- ====================================================================
-- Database Schema for the LinkedIn Agent Logger
-- ====================================================================
--
-- This script creates the `logs` table used by the `mysql_logger.py` module.
-- You can run this script manually against your target database.
--

-- Drop the table if it exists (optional, for a clean slate)
-- DROP TABLE IF EXISTS `logs`;

-- Create the `logs` table
CREATE TABLE IF NOT EXISTS `logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique identifier for each log entry',
    `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp of the log entry',
    `level` VARCHAR(20) NOT NULL COMMENT 'Log level (e.g., INFO, ERROR, DEBUG)',
    `source` VARCHAR(255) NOT NULL COMMENT 'Source of the log (e.g., rss_feed, mcp_client_agent)',
    `message` TEXT NOT NULL COMMENT 'The main log message',
    `details` JSON DEFAULT NULL COMMENT 'A JSON object for additional structured data',
)

    
    -- -- Indexes for faster querying
    -- INDEX `idx_timestamp` (`timestamp`),
    -- INDEX `idx_level` (`level`),
    -- INDEX `idx_source` (`source`)
