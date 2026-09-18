-- Oumeng Intelligence Monitor v2 / MariaDB 11.x
CREATE TABLE IF NOT EXISTS ci_oumeng_source (
 id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 canonical_url VARCHAR(2048) NOT NULL,
 url_hash CHAR(64) NOT NULL UNIQUE,
 host VARCHAR(255), source_class VARCHAR(32),
 first_seen_at DATETIME NOT NULL, last_seen_at DATETIME NOT NULL,
 last_crawled_at DATETIME, last_content_hash VARCHAR(64),
 INDEX idx_oumeng_source_last_crawl(last_crawled_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS ci_oumeng_snapshot (
 id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 url_hash CHAR(64) NOT NULL, canonical_url VARCHAR(2048) NOT NULL,
 content_hash VARCHAR(64) NOT NULL, captured_at DATETIME NOT NULL,
 title TEXT, markdown LONGTEXT,
 UNIQUE KEY uq_oumeng_snapshot(url_hash,content_hash), INDEX idx_oumeng_snapshot_time(captured_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS ci_oumeng_event (
 id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 event_fingerprint VARCHAR(64) NOT NULL UNIQUE, event_type VARCHAR(64), event_date DATE NULL,
 materiality INT NOT NULL DEFAULT 0, confidence INT NOT NULL DEFAULT 0, status VARCHAR(32) NOT NULL DEFAULT 'candidate',
 summary_de TEXT, entities_json LONGTEXT, first_seen_at DATETIME NOT NULL, last_seen_at DATETIME NOT NULL,
 source_count INT NOT NULL DEFAULT 1, alerted_at DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS ci_oumeng_event_evidence (
 id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 event_fingerprint VARCHAR(64) NOT NULL, url_hash CHAR(64) NOT NULL, content_hash VARCHAR(64) NOT NULL,
 source_role VARCHAR(32), evidence_json LONGTEXT,
 UNIQUE KEY uq_oumeng_event_evidence(event_fingerprint,url_hash,content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
