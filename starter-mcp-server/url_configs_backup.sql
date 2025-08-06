PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE url_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    profile_type TEXT NOT NULL,
                    description TEXT,
                    scraping_difficulty TEXT,
                    has_official_api BOOLEAN,
                    api_pricing TEXT,
                    recommendation TEXT,
                    key_data_points TEXT,
                    target_data TEXT,
                    rationale TEXT,
                    cost_analysis TEXT,
                    category TEXT,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
INSERT INTO url_configs VALUES(1,'DEXScreener','https://dexscreener.com','Degen Gambler','Real-time DEX trading data and token discovery platform','Medium',1,'Free tier: 300 requests/minute, Paid: $50-500/month','High Priority - Essential for degen trading','[]','[]','Primary platform for discovering new tokens and monitoring price movements','API recommended for high-frequency data','DEX Analytics',10,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(2,'PooCoin','https://poocoin.app','Degen Gambler','BSC token charts and trading analytics','Hard',0,'No official API','Medium Priority - BSC specific','[]','[]','Popular for BSC token analysis and memecoin tracking','Scraping required, moderate complexity','BSC Analytics',7,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(3,'DEXTools','https://www.dextools.io','Degen Gambler','Multi-chain DEX analytics and trading tools','Hard',1,'Premium: $25-100/month','High Priority - Multi-chain coverage','[]','[]','Comprehensive multi-chain DEX analytics','API subscription recommended','Multi-chain Analytics',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(4,'Birdeye','https://birdeye.so','Degen Gambler','Solana ecosystem analytics and token discovery','Medium',1,'Free tier available, Premium: $50-200/month','High Priority - Solana focus','[]','[]','Leading Solana analytics platform','Free tier sufficient for basic use','Solana Analytics',8,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(5,'Pump.fun','https://pump.fun','Degen Gambler','Solana memecoin launchpad and trading platform','Medium',0,'No official API','High Priority - Memecoin launches','[]','[]','Primary platform for Solana memecoin launches','Scraping required, real-time monitoring needed','Memecoin Launchpad',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(6,'GMGN.AI','https://gmgn.ai','Degen Gambler','AI-powered crypto trading insights and alpha discovery','Very Hard',0,'No official API','Medium Priority - Alpha insights','[]','[]','AI-driven insights for trading opportunities','Complex scraping, may require advanced techniques','AI Analytics',6,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(7,'Token Sniffer','https://tokensniffer.com','Gem Hunter','Token security analysis and rug pull detection','Medium',1,'Free tier: 100 requests/day, Paid: $20-100/month','High Priority - Security analysis','[]','[]','Essential for identifying safe investment opportunities','API recommended for automated screening','Security Analysis',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(8,'Solsniffer','https://solsniffer.com','Gem Hunter','Solana token security and analysis platform','Medium',0,'No official API','High Priority - Solana security','[]','[]','Specialized Solana token security analysis','Scraping required, moderate complexity','Solana Security',8,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(9,'Moralis','https://moralis.io','Gem Hunter','Web3 development platform with comprehensive blockchain APIs','Easy',1,'Free tier: 40k requests/month, Paid: $49-999/month','High Priority - Comprehensive data','[]','[]','Comprehensive blockchain data for fundamental analysis','API-first approach, cost-effective','Blockchain APIs',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(10,'CoinLaunch','https://coinlaunch.space','Gem Hunter','New cryptocurrency project discovery and analysis','Medium',0,'No official API','Medium Priority - Early projects','[]','[]','Early discovery of promising new projects','Scraping required, moderate frequency','Project Discovery',6,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(11,'Messari','https://messari.io','Traditional Investor','Professional crypto research and market intelligence','Medium',1,'Free tier: 20 requests/minute, Pro: $24-99/month','High Priority - Professional research','[]','[]','High-quality research and institutional-grade data','API subscription recommended for regular use','Research Platform',10,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(12,'Token Terminal','https://tokenterminal.com','Traditional Investor','Crypto project fundamentals and financial metrics','Medium',1,'Free tier available, Pro: $50-200/month','High Priority - Fundamental analysis','[]','[]','Traditional financial analysis applied to crypto','API access recommended for comprehensive data','Fundamental Analysis',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(13,'CryptoRank','https://cryptorank.io','Traditional Investor','Comprehensive crypto project database and analytics','Medium',1,'Free tier: 100 requests/day, Paid: $29-199/month','High Priority - Comprehensive database','[]','[]','Comprehensive project database for due diligence','API recommended for bulk data access','Project Database',8,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(14,'Glassnode','https://glassnode.com','Traditional Investor','On-chain analytics and market intelligence','Hard',1,'Free tier limited, Advanced: $39-799/month','High Priority - On-chain analysis','[]','[]','Leading on-chain analytics for institutional investors','Premium subscription required for full access','On-chain Analytics',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(15,'DeFiLlama','https://defillama.com','DeFi Yield Farmer','DeFi TVL tracking and protocol analytics','Easy',1,'Free and open source','High Priority - Essential DeFi data','[]','[]','Most comprehensive DeFi analytics platform','Free API, excellent for automation','DeFi Analytics',10,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(16,'De.Fi','https://de.fi','DeFi Yield Farmer','DeFi portfolio tracking and yield optimization','Medium',1,'Free tier available, Premium features paid','High Priority - Portfolio management','[]','[]','Comprehensive DeFi portfolio management','Free tier sufficient for basic tracking','Portfolio Management',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(17,'APY.Vision','https://apy.vision','DeFi Yield Farmer','Liquidity pool analytics and impermanent loss tracking','Medium',1,'Free tier: 100 requests/day, Pro: $20-100/month','High Priority - LP analysis','[]','[]','Specialized LP and yield farming analytics','API recommended for detailed analysis','LP Analytics',8,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(18,'Yearn Finance','https://yearn.fi','DeFi Yield Farmer','Automated yield farming and vault strategies','Medium',1,'Free API access','High Priority - Yield strategies','[]','[]','Leading automated yield farming platform','Free API, excellent for yield tracking','Yield Farming',9,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(19,'Beefy Finance','https://beefy.finance','DeFi Yield Farmer','Multi-chain yield optimization platform','Medium',1,'Free API access','High Priority - Multi-chain yields','[]','[]','Comprehensive multi-chain yield farming','Free API, good for cross-chain analysis','Multi-chain Yield',8,'2025-07-24 02:41:44','2025-07-24 02:41:44');
INSERT INTO url_configs VALUES(20,'Dune Analytics','https://dune.com','DeFi Yield Farmer','Blockchain data analytics and custom dashboards','Medium',1,'Free tier: 1k queries/month, Plus: $390/month','High Priority - Custom analytics','[]','[]','Powerful custom analytics for DeFi research','Free tier for basic use, paid for automation','Custom Analytics',7,'2025-07-24 02:41:44','2025-07-24 02:41:44');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('url_configs',20);
CREATE INDEX idx_profile_type 
                ON url_configs(profile_type)
            ;
CREATE INDEX idx_category 
                ON url_configs(category)
            ;
COMMIT;
