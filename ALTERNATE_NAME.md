# Alternate Repository Name: MAGI

## Current Name
**Rhyzomic-Intelligence-Node-RIN-**

## Recommended Alternate Name
**MAGI** (inspired by Neon Genesis Evangelion)

## Rationale

### Why MAGI Works Perfectly:

1. **Evangelion Connection**
   - In Neon Genesis Evangelion, the MAGI system is a trio of supercomputers (Melchior, Balthasar, Casper) that govern Tokyo-3
   - Each MAGI unit represents a different aspect of its creator (scientist, mother, woman)
   - Perfect metaphor for a distributed AI system with multiple subsystems working in harmony

2. **Biblical & Mythological Weight**
   - MAGI references the Three Wise Men (Biblical Magi) who brought wisdom from the East
   - Implies knowledge, intelligence, and guidance
   - Fits the "ancient wisdom meets cutting-edge technology" theme

3. **Technical Alignment**
   - The MAGI in Evangelion make decisions through consensus of three independent systems
   - Similar to RIN's architecture with The Cortex, The Sensorium, and The Memory working together
   - Reinforces the "organism" metaphor - multiple components forming a unified intelligence

4. **Brand Recognition**
   - Instantly recognizable to anime/tech enthusiasts
   - Short, memorable, and easy to type
   - Strong cultural cachet in the tech community

5. **Thematic Consistency**
   - Evangelion uses German/Biblical naming (SEELE, NERV, GEHIRN) like RIN's biological metaphors
   - Both emphasize autonomous systems, hidden knowledge, and opposition to centralized control
   - NERV fights Angels; MAGI helps run the city - both are sovereign infrastructure

### Alternative Evangelion-Inspired Names (In Order of Preference):

1. **MAGI** ⭐ Top Choice
   - The supercomputer triad governing Tokyo-3
   - Perfect for multi-component AI system

2. **GEHIRN** (German for "Brain")
   - The predecessor to NERV that created the Evangelion units
   - Emphasizes the cognitive/intelligence aspect
   - More technical, less mystical than MAGI

3. **SEELE** (German for "Soul")
   - The secret cabal controlling events from behind the scenes
   - Emphasizes sovereignty and hidden power
   - Might be too "shadow organization" themed

4. **NERV** (German for "Nerve")
   - The main organization in Evangelion
   - Perfect alignment with the biological metaphor
   - Already widely associated with Evangelion (trademark concerns?)

5. **WILLE** (German for "Will")
   - The anti-NERV organization from the Rebuild movies
   - Emphasizes autonomy and self-determination
   - Less well-known than MAGI or NERV

### Other Thematic Options:

**German Biological Terms (Evangelion Style):**
- **HERZ** (Heart) - Emotional core/engine
- **GEIST** (Spirit/Ghost) - Intelligence/essence
- **AUGE** (Eye) - Vision/surveillance (fits The Sensorium)
- **KÖRPER** (Body) - Physical infrastructure
- **ATEM** (Breath) - Life support systems

**Biblical/Esoteric (Evangelion Style):**
- **OPHANIM** - "The Wheels" covered in eyes (perfect for surveillance AI)
- **SERAPHIM** - Highest order of angels
- **ELOHIM** - Hebrew name for God
- **NEPHILIM** - The giants/offspring of divine beings

## Implementation Guide: Renaming to MAGI Without Breaking Anything

### The Strategy: Keep `rin` CLI, Rename Everything Else

The good news: **The `rin` command doesn't need to change!** It can remain as-is for backward compatibility while the repository name becomes MAGI.

#### Why This Works:

1. **The `rin` CLI is a filename** - It's a standalone script that users interact with
2. **Internal references to "rin"** (Python package, Docker services) can stay the same
3. **Only public-facing names need to change** - Repository name, documentation titles, branding

#### Step-by-Step Rename Process:

**Phase 1: Repository Rename (GitHub)**
```bash
# On GitHub:
# Settings → General → Repository name → Change to "MAGI"
# GitHub automatically creates redirects from old URLs to new URLs
# All existing clones, forks, and links continue to work
```

**Phase 2: Update Documentation (Branding Only)**

Files to update (only user-facing text, not code):
- `README.md` - Change title to "MAGI" with subtitle "(formerly Rhyzomic Intelligence Node)"
- `DESIGN.md` - Update project name at top
- `CHANGELOG.md` - Add entry about the rebrand
- `CLI_REFERENCE.md` - Note that CLI command remains `./rin` for compatibility
- `docs/*.md` - Update headers and references

**Phase 3: Keep These UNCHANGED (Critical for Compatibility)**

Do NOT change:
- ✅ The `rin` CLI script filename - Users already have this in their systems
- ✅ The `src/rin/` Python package - Would break imports and installations
- ✅ Docker service names (`rin-cortex`, `rin-memory`, etc.) - Would break existing deployments
- ✅ The `setup.py` package name `"rin"` - PyPI package name stays consistent
- ✅ Environment variables starting with `RIN_` - Would break existing configs

**Phase 4: Add Aliases for Discoverability**

Optional enhancements:
```bash
# Create a symlink so users can use either command:
ln -s rin magi

# Now both work:
./rin start
./magi start  # Same thing!
```

### What Changes vs. What Stays:

| Item | Action | Reason |
|------|--------|--------|
| Repository name on GitHub | CHANGE to "MAGI" | Public branding |
| README.md title | CHANGE to "MAGI" | Public branding |
| Documentation headers | CHANGE to "MAGI" | Public branding |
| CLI script `./rin` | KEEP as "rin" | Backward compatibility |
| Python package `src/rin/` | KEEP as "rin" | Import compatibility |
| Docker service names | KEEP as "rin-*" | Deployment compatibility |
| Environment variables | KEEP as "RIN_*" | Config compatibility |
| setup.py package name | KEEP as "rin" | PyPI compatibility |

### Example README Header After Rename:

```markdown
# MAGI
## Multi-Agent General Intelligence
### (formerly Rhyzomic Intelligence Node)

**Version**: 1.3.0 (Stable)  
**Status**: Active Development  
**Classification**: Sovereign AI Infrastructure

> *Like the MAGI system from Neon Genesis Evangelion, this is a distributed supercomputer 
> made of independent subsystems working in harmony to provide autonomous intelligence.*

## Overview

Commercial AI models (ChatGPT, Claude) are "Brains in a Jar"—intelligent but disconnected, 
censored, and reliant on their creators for input. MAGI is a sovereign, self-hosted entity...
```

### CLI Reference Note:

Add this to the CLI documentation:

```markdown
## Note on the `rin` Command

The CLI command remains `./rin` for backward compatibility, even though the project 
is now called MAGI. Think of it as:
- **MAGI** = The project name (the what)
- **rin** = The command name (the how)

Just like how you use `git` to work with GitHub, you use `rin` to work with MAGI.
```

### Migration Path for Users:

```bash
# Existing users - nothing changes:
cd Rhyzomic-Intelligence-Node-RIN-  # Old directory name works
./rin start                          # Same command

# New users cloning fresh:
git clone https://github.com/radkisson/MAGI.git
cd MAGI
./rin start                          # Same command, new repo name
```

### Architectural Metaphor Update:

The MAGI theme maps perfectly to the existing architecture:

| Evangelion MAGI | RIN Subsystem | Function |
|-----------------|---------------|----------|
| **Melchior** (Scientist) | The Cortex | Logical reasoning, problem-solving |
| **Balthasar** (Mother) | The Memory | Nurturing context, long-term recall |
| **Casper** (Woman) | The Sensorium | Perception, intuition, sensing the world |

The system makes decisions through consensus of its three aspects, just like the MAGI in Evangelion.

---

## Summary

**Recommended Approach:**
1. Rename repository to **MAGI** on GitHub
2. Update user-facing documentation to use "MAGI" branding
3. **Keep all technical identifiers unchanged** (`rin` command, Python package, Docker services)
4. Add a subtitle: "formerly Rhyzomic Intelligence Node" for context
5. Optionally create `./magi` symlink for discoverability

This gives you the Evangelion-inspired branding you want while maintaining 100% backward compatibility with existing deployments and user muscle memory.
