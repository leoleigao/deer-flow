# Table Guide UI

The Table Guide UI provides an interactive web interface for generating comprehensive documentation and analysis for database tables using AI-powered research agents.

## Overview

The Table Guide feature allows users to:
- Generate detailed table documentation including column descriptions, business meanings, and governance notes
- View sample SQL queries and usage examples
- Explore relationships with other tables
- Access this functionality through an intuitive web interface

## Getting Started

### Prerequisites

1. **Backend Server**: Ensure the FastAPI backend is running on port 8000
2. **Frontend Server**: Start the Next.js development server
3. **Environment Setup**: Configure the necessary environment variables

### Starting the Servers

```bash
# Start the backend (from project root)
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start the frontend (from web directory)
cd web
npm run dev
```

### Accessing the Interface

1. Open your browser and navigate to `http://localhost:3000/table-guide`
2. You'll see the Table Guide Generator interface

## Using the Interface

### Basic Workflow

1. **Enter Table Name**: Type a table name in the input field (e.g., `tracking.AdClickEvent`)
2. **Or Select Example**: Choose from the dropdown of available example tables
3. **Generate Guide**: Click the "Generate Guide" button
4. **View Results**: The generated guide will appear below with formatted markdown

### Interface States

The interface has four main states:

#### Idle State
- Clean form with empty input field
- Generate button is disabled until a table name is entered
- Example dropdown is available for quick selection

#### Loading State
- Generate button shows "Generating..." with a spinner
- All form controls are disabled during generation
- Loading typically takes 5-10 seconds

#### Success State
- Success message appears at the top
- Generated guide is displayed in a formatted card
- Reset button becomes available
- Guide includes sections like Key Columns, Business Meanings, Sample Queries

#### Error State
- Error message appears in a red alert box
- Form remains accessible for retry
- Common errors include table not found or API connection issues

### Features

#### Example Table Dropdown
- Populated dynamically from available fixture files
- Shows table name and description
- Automatically fills the input field when selected

#### Markdown Rendering
- Full markdown support with syntax highlighting
- Anchor links for easy navigation
- Responsive tables and code blocks
- Dark mode support

#### Keyboard Navigation
- Press Enter in the input field to generate guide
- Tab navigation through all form elements
- Accessible design following WCAG guidelines

## Stub Mode Operation

### What is Stub Mode?

The Table Guide UI operates in "stub mode" by default, which means:
- It uses local JSON fixture files instead of connecting to a real data warehouse
- No actual database queries are executed
- Responses are fast and predictable for development and testing

### Fixture Files

Fixture data is stored in `tests/fixtures/glean/` with the following structure:

```
tests/fixtures/glean/
├── tracking.AdClickEvent.json
├── marketing.CampaignSummary.json
├── sales.OrderHeader.json
└── ...
```

Each fixture file contains mock documentation for a table, including:
- Schema information
- Sample queries
- Business context
- Governance notes

### Available Example Tables

The following tables are available in stub mode:
- `tracking.AdClickEvent` - Ad click tracking data
- `marketing.CampaignSummary` - Marketing campaign summaries
- `sales.OrderHeader` - Sales order information
- `user.ProfileSnapshot` - User profile data
- `finance.InvoiceItem` - Financial invoice details
- `event.FunnelStep` - User funnel analytics
- `tracking.PageView` - Page view tracking

## Environment Configuration

### Environment Variables

The UI respects the following environment variables:

```bash
# API endpoint (defaults to http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Enable/disable the table guide UI (defaults to true in development)
NEXT_PUBLIC_ENABLE_TABLE_GUIDE_UI=true

# Analytics (optional)
AMPLITUDE_API_KEY=your_amplitude_key
```

### Development vs Production

- **Development**: Stub mode is enabled by default with local fixtures
- **Production**: Requires `USE_GLEAN_STUB=false` to connect to real data sources

## Troubleshooting

### Common Issues

#### "Failed to connect to the API server"
- **Cause**: Backend server is not running or not accessible
- **Solution**: Start the FastAPI server on port 8000
- **Check**: Visit `http://localhost:8000/docs` to verify the API is running

#### "No fixture data found for table: [table_name]"
- **Cause**: The requested table doesn't have a corresponding fixture file
- **Solution**: Use one of the available example tables or create a fixture file
- **Available tables**: Check the dropdown for valid options

#### Loading spinner never stops
- **Cause**: Network timeout or API error
- **Solution**: Check browser developer tools for network errors
- **Workaround**: Refresh the page and try again

#### Markdown not rendering properly
- **Cause**: Invalid markdown in the generated guide
- **Solution**: This is typically a backend issue with the guide generation
- **Check**: Verify the API response contains valid markdown

### Debug Mode

To enable debug logging:

1. Open browser developer tools (F12)
2. Check the Console tab for error messages
3. Check the Network tab for API request/response details

### API Endpoints

The UI interacts with these backend endpoints:

- `GET /api/table_guide?table={table_name}` - Generate table guide
- `GET /api/fixtures_index` - Get list of available tables

You can test these endpoints directly:
```bash
# Test table guide generation
curl "http://localhost:8000/api/table_guide?table=tracking.AdClickEvent"

# Test fixtures index
curl "http://localhost:8000/api/fixtures_index"
```

## Limitations

### Current Limitations

1. **Stub Mode Only**: Currently only works with local fixture data
2. **No Real-time Data**: Cannot connect to live databases in the current implementation
3. **Limited Tables**: Only pre-defined fixture tables are available
4. **No Caching**: Each request regenerates the guide (no client-side caching)
5. **Single Table**: Cannot analyze multiple tables simultaneously

### Future Enhancements

- Real database connectivity
- Table comparison features
- Export to PDF/Word
- Collaborative editing
- Version history
- Custom template support

## Accessibility

The Table Guide UI follows accessibility best practices:

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Color Contrast**: Meets WCAG AA standards
- **Focus Management**: Clear focus indicators and logical tab order
- **Error Handling**: Descriptive error messages and validation

## Performance

### Optimization Features

- **Lazy Loading**: Components load only when needed
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode**: Automatic theme switching based on system preference
- **Fast Rendering**: Optimized markdown rendering with syntax highlighting

### Performance Metrics

- **Initial Load**: < 2 seconds on modern browsers
- **Guide Generation**: 5-10 seconds (depending on table complexity)
- **Lighthouse Score**: Targets 90+ for performance, accessibility, and best practices

## Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `cd web && npm install`
3. Start development server: `npm run dev`
4. Make changes and test locally

### Testing

```bash
# Run unit tests
npm run test:unit

# Run E2E tests (when Cypress is configured)
npm run cypress:headless

# Run linting
npm run lint
```

### Code Style

- Follow existing TypeScript/React patterns
- Use Tailwind CSS for styling
- Add proper TypeScript types
- Include JSDoc comments for complex functions

## Support

For issues and questions:

1. Check this documentation first
2. Search existing GitHub issues
3. Create a new issue with detailed reproduction steps
4. Include browser version, OS, and error messages 