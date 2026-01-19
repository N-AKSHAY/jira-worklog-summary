# Security Policy

## Supported Versions

We actively support the latest version of the application. Security updates will be applied to the current version.

## Reporting a Vulnerability

If you discover a security vulnerability in this application, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. Contact the maintainer directly: **Akshay NP** at Stabilix Solutions
3. Provide details about the vulnerability:
   - Description of the issue
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Best Practices

### For Developers

- Never commit sensitive information (API keys, secrets, tokens) to the repository
- Use environment variables for configuration
- Keep dependencies up to date
- Follow secure coding practices
- Validate all user inputs
- Use HTTPS in production
- Implement proper session management

### For Deployment

- Use secure session cookies (HttpOnly, Secure, SameSite)
- Set appropriate CORS policies
- Use environment-specific configuration
- Regularly update dependencies
- Monitor for security advisories
- Use strong secret keys for session management

## OAuth Security

- OAuth credentials must be stored securely
- Never expose OAuth client secrets
- Use secure redirect URIs
- Implement proper state parameter validation
- Handle OAuth errors gracefully

## Data Privacy

- This application processes Jira worklog data
- User authentication is handled via OAuth 2.0
- Session data is stored securely
- No sensitive data should be logged

## Contact

For security concerns, please contact:
**Akshay NP** - Stabilix Solutions
