# Personal Finance Tracker

A Streamlit-based web application for tracking personal finances, managing expenses and income, and visualizing financial data.

## Features

- **Dashboard**: View financial summaries, expense distribution by category, and income vs. expenses over time
- **Transaction Management**: Add, edit, and delete financial transactions
- **Category Management**: Create and manage custom expense and income categories
- **Transaction Filtering**: Filter transactions by date range, category, and transaction type
- **Data Visualization**: Interactive charts and graphs for financial analysis

## Technologies Used

- **Python**: Core programming language
- **Streamlit**: Web application framework
- **SQLite**: Database for storing financial data
- **Pandas**: Data manipulation and analysis
- **Plotly Express**: Interactive data visualization

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
uv sync
```

3. Run the application:

```bash
streamlit run app/main.py
```

## Usage

### Dashboard

The dashboard provides an overview of your financial situation with:
- Income, expenses, and balance metrics
- Pie chart showing expense distribution by category
- Bar chart comparing monthly income vs. expenses

### Adding Transactions

1. Navigate to the "Add Transaction" page
2. Select transaction type (income or expense)
3. Enter the date, amount, category, and description
4. Click "Add Transaction"

### Viewing Transactions

1. Navigate to the "View Transactions" page
2. Filter transactions by date range, category, or transaction type
3. Edit or delete transactions using the transaction ID

### Managing Categories

1. Navigate to the "Manage Categories" page
2. View existing categories
3. Add new expense or income categories

## Data Structure

The application uses SQLite with two main tables:
- **transactions**: Stores all financial transactions
- **categories**: Stores expense and income categories

## License

This project is open source and available under the MIT License.

## Version

Personal Finance Tracker v1.0
# home-media-server
