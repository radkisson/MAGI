# Repository Rename: MAGI

## Previous Name
**Rhyzomic-Intelligence-Node-RIN-** (deprecated)

## New Name
**MAGI** (Multi-Agent General Intelligence)

**Inspired by Neon Genesis Evangelion** - The MAGI system: three supercomputers (Melchior, Balthasar, Casper) that work in harmony to govern Tokyo-3.

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

## Implementation Completed

This document details the completed rename from RIN (Rhyzomic Intelligence Node) to MAGI (Multi-Agent General Intelligence).

### Changes Made:

#### 1. **Docker Services** ✅
All container names updated from `rin-*` to `magi-*`:
- `rin-cortex` → `magi-cortex`
- `rin-router` → `magi-router`
- `rin-vision` → `magi-vision`
- `rin-digestion` → `magi-digestion`
- `rin-nervous-system` → `magi-nervous-system`
- `rin-memory` → `magi-memory`
- `rin-reflex-automation` → `magi-reflex-automation`
- `rin-browser` → `magi-browser`
- `rin-mcp-bridge` → `magi-mcp-bridge`
- `rin-youtube-mcp` → `magi-youtube-mcp`

#### 2. **Environment Variables** ✅
Updated all environment references:
- Comments updated from "RIN" to "MAGI"
- `LITELLM_MASTER_KEY` prefix changed from `sk-rin-` to `sk-magi-`
- `OPENROUTER_APP_NAME` default changed to "MAGI"

#### 3. **Documentation** ✅
All documentation updated with MAGI branding:
- README.md title and references
- DESIGN.md project name
- CLI_REFERENCE.md descriptions
- All docs/*.md files
- CHANGELOG.md entry added

#### 4. **Python Package** ✅
Removed `src/rin/` directory - legacy code no longer used in Docker-based architecture

#### 5. **CLI Command** ℹ️
The `./rin` command filename **remains unchanged** for backward compatibility.
- Think of it as: **MAGI** = project name, **rin** = command name
- Similar to how `git` is the command for GitHub
- Users can optionally create a symlink: `ln -s rin magi`

### What Was NOT Changed (Intentionally):

- ✅ CLI script filename (`./rin`) - backward compatibility
- ✅ Repository history and existing clones - GitHub auto-redirects

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
