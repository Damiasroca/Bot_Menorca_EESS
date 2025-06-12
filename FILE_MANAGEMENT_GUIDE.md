# File Management Guide: New Menorca Bot System

## 🎯 **Essential Files for New System (KEEP)**

### **Core Application Files**
```
✅ main_bot_menorca.py              # Main bot application
✅ data_manager_menorca.py          # Data management layer  
✅ constants_menorca.py             # Configuration and constants
✅ notification_sender.py           # Price alerts system
✅ secret.py                        # Configuration secrets
```

### **Operational Scripts**
```
✅ downloads_menorca.sh             # Data download script
✅ bot_menorca_telegram_starter.sh  # Service management script
```

### **Dependencies & Documentation**
```
✅ requirements.txt                 # Python dependencies
✅ README_MENORCA_ADAPTATION.md     # Setup and usage guide
✅ MIGRATION_SUMMARY.md             # Implementation summary
```

### **Essential Directories**
```
✅ municipis_original/              # Raw JSON data (used by new system)
✅ logs/                           # Log files (auto-created)
```

---

## 🔄 **Migration Files (TEMPORARY - Delete after migration)**

### **Migration Tools**
```
🟡 migrate_database.py              # Database migration script
🟡 hybrid_data_manager.py           # Transition data manager
🟡 data_manager_compatibility_patch.py  # Compatibility patch
🟡 DATABASE_MIGRATION_GUIDE.md      # Migration instructions
```

**Action after successful migration:** These can be deleted once you've migrated successfully and the new system is stable.

---

## 📁 **Original Files - Backup vs Delete**

### **Keep as Backup (Rename)**
```
📦 main_bot.py → main_bot_original_backup.py
📦 data_manager.py → data_manager_original_backup.py  
📦 constants.py → constants_original_backup.py
📦 downloads.sh → downloads_original_backup.sh
📦 bot_telegram_starter.sh → bot_telegram_starter_original_backup.sh
```

### **Can Be Deleted (After Migration)**
```
❌ db.py                           # Replaced by data_manager_menorca.py
❌ main_database.py                # Functionality integrated in new system
❌ json_processing/                # Old data processing workflow (obsolete)
❌ municipis_modificats/           # Old processed data (superseded by new system)
```

### **Old Data Processing Directories (OBSOLETE)**

#### **📁 json_processing/** - Old Processing Workflow
```
❌ b.json, c.json, e.json          # Intermediate processing files
❌ combinat.json                   # Combined data file
❌ combinat_per_importar.csvdata.csv # CSV export
❌ dataTypesMetzineres.txt         # Old data types reference
```
**Reason to delete:** The new system processes JSON directly from `municipis_original/` through `data_manager_menorca.py`. These intermediate files are no longer needed.

#### **📁 municipis_modificats/** - Old Processed Data  
```
❌ alaior.json, ciutadella.json    # Processed municipality files
❌ mao.json, ferreries.json        # Modified versions of original data
❌ santlluis.json, merdal.json     # Old processed data format
❌ escastell.json                  # Municipality data
```
**Reason to delete:** The new system uses raw data from `municipis_original/` and processes it in real-time. These modified files represent an old processing step that's now handled automatically.

---

## 📂 **Directory Structure After Cleanup**

### **Production Directory (Final State)**
```
Bot_Menorca_EESS/
├── 📁 logs/                       # Log files (auto-created)
├── 📁 municipis_original/         # Raw JSON data (NEW SYSTEM USES THIS)
├── 📄 main_bot_menorca.py         # 🎯 MAIN BOT
├── 📄 data_manager_menorca.py     # 🗄️ DATA LAYER
├── 📄 constants_menorca.py        # ⚙️ CONFIGURATION
├── 📄 notification_sender.py      # 🔔 ALERTS
├── 📄 secret.py                   # 🔑 SECRETS
├── 📄 requirements.txt            # 📦 DEPENDENCIES
├── 🔧 downloads_menorca.sh        # 📥 DATA DOWNLOAD
├── 🔧 bot_menorca_telegram_starter.sh  # 🚀 SERVICE CONTROL
├── 📖 README_MENORCA_ADAPTATION.md     # 📚 DOCUMENTATION
├── 📖 MIGRATION_SUMMARY.md        # 📋 IMPLEMENTATION NOTES
└── 📁 backups/                    # 💾 ORIGINAL FILES (optional)
    ├── main_bot_original_backup.py
    ├── data_manager_original_backup.py
    ├── constants_original_backup.py
    ├── downloads_original_backup.sh
    └── bot_telegram_starter_original_backup.sh
```

---

## 🚀 **Migration Steps with File Management**

### **Step 1: Backup Original Files**
```bash
# Create backup directory
mkdir -p backups

# Backup original files
cp main_bot.py backups/main_bot_original_backup.py
cp data_manager.py backups/data_manager_original_backup.py
cp constants.py backups/constants_original_backup.py
cp downloads.sh backups/downloads_original_backup.sh
cp bot_telegram_starter.sh backups/bot_telegram_starter_original_backup.sh

# Optional: Backup old processing directories (if you want to be extra safe)
# cp -r json_processing backups/
# cp -r municipis_modificats backups/
```

### **Step 2: Run Migration**
```bash
# Run database migration
python3 migrate_database.py
```

### **Step 3: Test New System**
```bash
# Test new bot
./bot_menorca_telegram_starter.sh start
./bot_menorca_telegram_starter.sh status
```

### **Step 4: Clean Up (After successful testing)**
```bash
# Remove old files that are no longer needed
rm db.py
rm main_database.py

# Remove old data processing directories (SAFE TO DELETE)
rm -rf json_processing/
rm -rf municipis_modificats/

# Remove migration files (keep if you might migrate again)
rm migrate_database.py
rm hybrid_data_manager.py
rm data_manager_compatibility_patch.py
rm DATABASE_MIGRATION_GUIDE.md

# Optional: Remove original files (if you're confident)
# rm main_bot.py data_manager.py constants.py downloads.sh bot_telegram_starter.sh
```

---

## 📋 **File-by-File Decision Matrix**

| File/Directory | Action | Reason |
|------|--------|--------|
| `main_bot_menorca.py` | ✅ **KEEP** | Core new bot application |
| `data_manager_menorca.py` | ✅ **KEEP** | Core data management |
| `constants_menorca.py` | ✅ **KEEP** | Core configuration |
| `notification_sender.py` | ✅ **KEEP** | Core alerts system |
| `secret.py` | ✅ **KEEP** | Core secrets (updated) |
| `downloads_menorca.sh` | ✅ **KEEP** | Core data acquisition |
| `bot_menorca_telegram_starter.sh` | ✅ **KEEP** | Core service management |
| `requirements.txt` | ✅ **KEEP** | Core dependencies |
| `README_MENORCA_ADAPTATION.md` | ✅ **KEEP** | Essential documentation |
| `MIGRATION_SUMMARY.md` | ✅ **KEEP** | Essential documentation |
| `municipis_original/` | ✅ **KEEP** | Raw data source for new system |
| `logs/` | ✅ **KEEP** | Log files directory |
| `migrate_database.py` | 🟡 **TEMP** | Delete after migration |
| `hybrid_data_manager.py` | 🟡 **TEMP** | Delete after migration |
| `data_manager_compatibility_patch.py` | 🟡 **TEMP** | Delete after migration |
| `DATABASE_MIGRATION_GUIDE.md` | 🟡 **TEMP** | Delete after migration |
| `main_bot.py` | 📦 **BACKUP** | Backup then can delete |
| `data_manager.py` | 📦 **BACKUP** | Backup then can delete |
| `constants.py` | 📦 **BACKUP** | Backup then can delete |
| `downloads.sh` | 📦 **BACKUP** | Backup then can delete |
| `bot_telegram_starter.sh` | 📦 **BACKUP** | Backup then can delete |
| `db.py` | ❌ **DELETE** | Replaced by new system |
| `main_database.py` | ❌ **DELETE** | Replaced by new system |
| `json_processing/` | ❌ **DELETE** | Old processing workflow (obsolete) |
| `municipis_modificats/` | ❌ **DELETE** | Old processed data (superseded) |

---

## 🧠 **Understanding the Data Flow Change**

### **Old System Workflow:**
```
Raw API Data → json_processing/ → municipis_modificats/ → Database
```

### **New System Workflow:**
```
Raw API Data → municipis_original/ → Direct Processing → Database
```

**Why the old directories are obsolete:**
- **`json_processing/`**: Contained intermediate processing steps that are now handled in-memory by `data_manager_menorca.py`
- **`municipis_modificats/`**: Contained pre-processed data that the new system generates on-the-fly

**Benefits of new approach:**
- ✅ **Simpler workflow** - fewer steps and files
- ✅ **Always fresh data** - no stale processed files
- ✅ **Better error handling** - processing errors are caught immediately
- ✅ **Less disk space** - no duplicate processed files

---

## 🛡️ **Safety Recommendations**

### **Conservative Approach (Recommended)**
1. **Keep original files** in `backups/` folder for 30 days
2. **Test new system thoroughly** before deleting anything
3. **Keep migration files** until you're 100% confident
4. **Document any customizations** you had in original files
5. **Backup old processing directories** before deletion (optional)

### **Aggressive Cleanup (Advanced Users)**
1. **Delete original files** immediately after migration
2. **Remove migration tools** after successful migration
3. **Delete old processing directories** immediately
4. **Keep only production files** in main directory

### **Rollback Plan**
If you need to go back to the original system:

```bash
# Stop new bot
./bot_menorca_telegram_starter.sh stop

# Restore original files
cp backups/main_bot_original_backup.py main_bot.py
cp backups/data_manager_original_backup.py data_manager.py
cp backups/constants_original_backup.py constants.py
cp backups/downloads_original_backup.sh downloads.sh
cp backups/bot_telegram_starter_original_backup.sh bot_telegram_starter.sh

# Restore old processing directories if backed up
# cp -r backups/json_processing .
# cp -r backups/municipis_modificats .

# Restore database if needed
mysql -u user -p database < backup_YYYYMMDD.sql

# Start original bot
python3 main_bot.py
```

---

## 📊 **Disk Space Savings**

After full cleanup, you'll save approximately:
- **Migration files**: ~50KB
- **Original files**: ~150KB  
- **json_processing/ directory**: ~30KB
- **municipis_modificats/ directory**: ~25KB
- **Redundant scripts**: ~25KB
- **Total savings**: ~280KB

**New system benefits**:
- ✅ Cleaner codebase
- ✅ Better performance
- ✅ Enhanced features
- ✅ Production-ready architecture
- ✅ Simplified data workflow

## 🎯 **Quick Commands for File Management**

```bash
# Quick backup of originals (including old directories)
mkdir backups
cp main_bot.py data_manager.py constants.py downloads.sh bot_telegram_starter.sh backups/
cp -r json_processing municipis_modificats backups/ # Optional extra safety

# Quick cleanup after migration (conservative)
rm db.py main_database.py

# Quick cleanup after migration (recommended)
rm db.py main_database.py
rm -rf json_processing/ municipis_modificats/

# Quick cleanup after migration (aggressive)
rm db.py main_database.py migrate_database.py hybrid_data_manager.py data_manager_compatibility_patch.py DATABASE_MIGRATION_GUIDE.md
rm -rf json_processing/ municipis_modificats/

# Ultimate cleanup (when confident)
rm main_bot.py data_manager.py constants.py downloads.sh bot_telegram_starter.sh
rm -rf json_processing/ municipis_modificats/
```

The new system is **production-ready** and contains all the functionality you need. The old data processing directories are **safe to delete** as they represent an obsolete workflow that's been replaced by the more efficient new system! 