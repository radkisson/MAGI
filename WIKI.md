# RIN Wiki Documentation

## Overview

The RIN project maintains a [GitHub Wiki](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/wiki) as a community-driven documentation resource. The wiki is separate from the main repository documentation and serves as a collaborative space for:

- **User-contributed guides**: Advanced configuration, deployment scenarios, and custom integrations
- **Troubleshooting solutions**: Community-discovered fixes and workarounds
- **Use cases and examples**: Real-world deployment stories and best practices
- **Extended tutorials**: Step-by-step guides for complex workflows

## Accessing the Wiki

### Via Web Interface

Visit the wiki directly at:
https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/wiki

You can browse, search, and read all wiki pages through the GitHub web interface.

### Via Git Repository

The wiki is also accessible as a Git repository, allowing you to:
- Clone the wiki for offline access
- Make bulk edits locally
- Track wiki changes with version control
- Contribute via command-line tools

**Clone the wiki repository:**

```bash
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.wiki.git
cd Rhyzomic-Intelligence-Node-RIN-.wiki
```

## Contributing to the Wiki

### Web-Based Editing

1. **Navigate** to the [Wiki](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/wiki)
2. **Click "Edit"** on any page (requires GitHub account)
3. **Make your changes** using Markdown syntax
4. **Provide a commit message** describing your changes
5. **Click "Save Page"**

### Git-Based Editing

1. **Clone the wiki repository** (see above)
2. **Edit pages** using your favorite text editor
3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add guide for Kubernetes deployment"
   git push origin master
   ```

### Creating New Pages

**Via Web:**
- Click "New Page" in the wiki sidebar
- Enter the page name and content
- Save the page

**Via Git:**
- Create a new `.md` file in the wiki repository
- Commit and push the file
- The page will appear in the wiki automatically

## Wiki Structure Recommendations

While the wiki is community-driven and flexible, we recommend organizing content into the following categories:

### 📚 User Guides
- Installation variations (cloud providers, bare metal, etc.)
- Configuration recipes for specific use cases
- Integration guides (external services, APIs, etc.)

### 🔧 Troubleshooting
- Common issues and solutions
- Platform-specific fixes (Windows, macOS, Linux)
- Performance optimization tips

### 💡 Use Cases
- Real-world deployment examples
- Success stories and case studies
- Architecture patterns and best practices

### 🚀 Advanced Topics
- Custom tool development
- Model fine-tuning and optimization
- Multi-node deployments
- Security hardening

## Wiki vs. Main Documentation

### Use the **Wiki** for:
- Community-contributed content
- Experimental configurations
- Platform-specific guides
- Personal experiences and tips
- Quick reference guides

### Use the **Main Repository** (`docs/`) for:
- Official documentation
- Core feature documentation
- Architecture specifications
- API references
- Security and compliance documentation

## Guidelines for Wiki Contributors

1. **Be Clear**: Use simple language and provide context
2. **Be Accurate**: Test your instructions before publishing
3. **Be Respectful**: Follow the community code of conduct
4. **Use Markdown**: Format content with proper headings, code blocks, and lists
5. **Link Resources**: Reference relevant pages and external documentation
6. **Update Outdated Content**: If you find outdated information, update it
7. **Discuss Major Changes**: For significant restructuring, open a GitHub Discussion first

## Wiki Accessibility

The RIN wiki repository is **publicly accessible** and can be:
- ✅ Cloned via HTTPS or SSH
- ✅ Read without authentication
- ✅ Edited by users with GitHub accounts
- ✅ Forked for personal documentation

**Repository URL**: `https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.wiki.git`

## Support

If you have questions about contributing to the wiki:
- **Discussions**: [GitHub Discussions](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/discussions)
- **Issues**: For wiki-specific technical issues, open an [Issue](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues)

---

**The wiki is a living document, maintained by the community, for the community.** 📖✨
