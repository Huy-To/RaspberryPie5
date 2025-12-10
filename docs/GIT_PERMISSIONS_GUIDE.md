# Git Permissions Fix Guide

## Problem

When you pull from GitHub, Git doesn't preserve executable permissions on `.sh` files. This means you have to manually run `chmod +x` on every script after every pull.

## Solution

We've created an automated solution that fixes permissions automatically!

---

## Option 1: Automatic Fix (Recommended)

### Git Hooks (Automatic After Pull)

Git hooks automatically run `fix_permissions.sh` after every `git pull` or `git checkout`.

**Setup (one-time):**

```bash
cd ~/RaspberryPie5

# Easiest way - run the setup script
chmod +x setup_git_hooks.sh
./setup_git_hooks.sh
```

**That's it!** Now every time you run `git pull`, permissions will be fixed automatically.

**Alternative manual setup:**

```bash
# Make git hooks executable
chmod +x .git/hooks/post-merge
chmod +x .git/hooks/post-checkout

# Make fix_permissions.sh executable
chmod +x fix_permissions.sh
```

**Note:** Git hooks are not tracked by Git, so you need to set them up once on each machine/clone.

---

## Option 2: Manual Fix (After Every Pull)

Run the fix script manually after pulling:

```bash
cd ~/RaspberryPie5
./fix_permissions.sh
```

Or if it's not executable yet:

```bash
chmod +x fix_permissions.sh
./fix_permissions.sh
```

---

## Option 3: Add to Your Workflow

Add this to your `.bashrc` or `.zshrc`:

```bash
# Auto-fix permissions after git pull
git() {
    command git "$@"
    if [ "$1" = "pull" ] || [ "$1" = "checkout" ]; then
        if [ -f "./fix_permissions.sh" ]; then
            bash ./fix_permissions.sh 2>/dev/null
        fi
    fi
}
```

---

## What `fix_permissions.sh` Does

The script:
1. ✅ Finds all `.sh` files recursively
2. ✅ Finds all `.py` files recursively
3. ✅ Makes them executable
4. ✅ Shows which files were fixed
5. ✅ Skips `.git` directories

**Example output:**
```
🔧 Fixing script permissions...
================================
📝 Making all .sh files executable...
   ✅ Made executable: ./run.sh
   ✅ Made executable: ./run_api.sh
   ✅ Made executable: ./run_enroll.sh
   ✅ Made executable: ./scripts/setup.sh
🐍 Making all .py files executable...
   ✅ Made executable: ./src/raspberry_pi_face_detection.py
   ✅ Made executable: ./src/enroll_face.py

✅ Fixed permissions for 6 file(s)
```

---

## Quick Reference

### After Git Pull

**If git hooks are set up:**
```bash
git pull
# Permissions fixed automatically! ✅
```

**If git hooks are NOT set up:**
```bash
git pull
./fix_permissions.sh
```

### One-Time Setup

```bash
# Make git hooks executable
chmod +x .git/hooks/post-merge
chmod +x .git/hooks/post-checkout

# Make fix script executable
chmod +x fix_permissions.sh

# Test it
./fix_permissions.sh
```

---

## Troubleshooting

### Problem: Git hooks not running

**Check:**
1. **Hooks exist:**
   ```bash
   ls -l .git/hooks/post-merge
   ls -l .git/hooks/post-checkout
   ```

2. **Hooks are executable:**
   ```bash
   chmod +x .git/hooks/post-merge
   chmod +x .git/hooks/post-checkout
   ```

3. **Test manually:**
   ```bash
   bash .git/hooks/post-merge
   ```

### Problem: fix_permissions.sh not executable

**Solution:**
```bash
chmod +x fix_permissions.sh
./fix_permissions.sh
```

### Problem: Still need to chmod manually

**Solution:** Use the git hooks or add to your workflow (see Option 3 above)

---

## Files Created

1. **`fix_permissions.sh`** - Main script to fix permissions
2. **`.git/hooks/post-merge`** - Runs after `git pull`
3. **`.git/hooks/post-checkout`** - Runs after `git checkout`
4. **`.gitattributes`** - Updated to preserve executable permissions

---

## Summary

✅ **Automatic:** Set up git hooks once, then permissions fix automatically  
✅ **Manual:** Run `./fix_permissions.sh` after every pull  
✅ **Comprehensive:** Fixes all `.sh` and `.py` files recursively  
✅ **Safe:** Skips `.git` directories and already-executable files  

---

**See Also:**
- [FIX_ERRORS.md](../FIX_ERRORS.md) - Other common errors
- [README.md](../README.md) - Main documentation

