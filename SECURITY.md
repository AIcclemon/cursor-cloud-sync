# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions of Cursor Cloud Sync:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Cursor Cloud Sync seriously. If you discover a security vulnerability, please help us maintain the security of our project by reporting it responsibly.

### How to Report

**Please do NOT create a public issue for security vulnerabilities.**

Instead, please report security vulnerabilities by:

1. **Email**: Send details to the project maintainers
2. **GitHub Security Advisories**: Use GitHub's private vulnerability reporting feature at:
   `https://github.com/AIcclemon/cursor-cloud-sync/security/advisories/new`

### What to Include

When reporting a vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential impact and severity of the vulnerability
- **Environment**: Your operating system, Python version, and tool version
- **Proof of Concept**: If applicable, provide a minimal example

### Response Timeline

- **Initial Response**: Within 48 hours of receiving the report
- **Assessment**: We'll assess the vulnerability within 5 business days
- **Updates**: Regular updates on our progress
- **Resolution**: Security fixes will be prioritized and released as quickly as possible

### Security Considerations

Cursor Cloud Sync handles sensitive data including:

- **Google Drive API credentials**
- **OAuth tokens**
- **User configuration files**
- **Cursor IDE settings**

Common security concerns to report:

- **Credential exposure**: Any way credentials could be leaked
- **Path traversal**: Issues with file path handling
- **Injection attacks**: Command injection or similar vulnerabilities
- **Authentication bypass**: Ways to bypass OAuth or API authentication
- **Data corruption**: Ways malicious data could corrupt user settings

### Safe Harbor

We support safe harbor for security researchers who:

- Make a good faith effort to avoid privacy violations and disruption
- Only interact with accounts they own or with explicit permission
- Do not access or modify others' data
- Report vulnerabilities promptly
- Allow reasonable time for fixes before public disclosure

### Security Best Practices for Users

To keep your installation secure:

1. **Keep Updated**: Always use the latest version of Cursor Cloud Sync
2. **Protect Credentials**: Never share your `credentials.json` or `token.json` files
3. **Use Official Sources**: Only download from the official GitHub repository
4. **Review Permissions**: Regularly review your Google Drive API permissions
5. **Monitor Logs**: Check `sync.log` for any suspicious activity
6. **Secure Environment**: Run the tool on a secure, trusted system

### Security Features

Cursor Cloud Sync includes several security features:

- **OAuth 2.0**: Secure authentication with Google Drive
- **Credential Isolation**: Credentials stored separately from code
- **Path Validation**: Input validation for file paths
- **Permission Checks**: File permission verification
- **Encrypted Transport**: All API calls use HTTPS

### Acknowledgments

We appreciate the security research community's efforts in keeping our project safe. Security researchers who responsibly disclose vulnerabilities will be acknowledged in our release notes (unless they prefer to remain anonymous).

### Questions

If you have questions about this security policy, please create a discussion on GitHub or contact the maintainers.