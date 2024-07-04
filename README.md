# gpx

GPX is a web application to access GitHub Project boards using modern web technologies.
Built with FastAPI and HTMX, GPX provides a simpler interface for managing GitHub Projects (v2),
and ultimately aims to use GitHub Projects as a storage layer for more sophisticated project management (ongoing).

## Features

- [x] **GitHub Integration**: Connect with your GitHub account to access and manage your projects.
- [x] **Project Overview**: View all your GitHub projects in a simple, responsive dashboard.
- [ ] **Project Editor**: Edit project details, add items, and manage project status directly from the web interface.
- [x] **Real-time Updates**: Utilizes HTMX for instant updates without full page reloads.
- [x] **Responsive Design**: Built with Tailwind CSS for a mobile-friendly, adaptive layout.

## Installation

To try it out for alpha testing, visit <s>[gpx.onrender.com](https://gpx.onrender.com)</s> [gpx-production.up.railway.app](https://gpx-production.up.railway.app)

- App link: [github.com/apps/gpx-projects](https://github.com/apps/gpx-projects)

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTMX, Hyperscript, Tailwind CSS
- **Authentication**: GitHub OAuth
- **API**: GitHub GraphQL API

## Getting Started

### Prerequisites

To develop your own fork you will need:

- Python 3.10 or higher
- Poetry (for dependency management)
- A GitHub account and OAuth App credentials

### Development

1. Clone the repository:
   ```
   git clone https://github.com/lmmx/gpx.git
   cd gpx
   ```

2. Install dependencies:
   ```
   poetry install
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   SESSION_SECRET_KEY=your_session_secret_key
   ```

4. Run the FastAPI server on port 8000 (with hot reloading):
   ```
   serve
   ```

5. Open your browser and navigate to `http://localhost:8000`

## Usage

1. Log in with your GitHub account.
2. View your projects on the dashboard.
3. Click on a project to open the project editor.
4. Add, edit, or remove items from your project.
5. Changes are automatically synced with your GitHub Projects.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [HTMX](https://htmx.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [GitHub API](https://docs.github.com/en/graphql)
