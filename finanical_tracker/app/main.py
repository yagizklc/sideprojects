from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from database import (
    add_category,
    add_transaction,
    delete_transaction,
    get_categories,
    get_transaction_by_id,
    get_transactions,
    init_db,
    update_transaction,
)
from widgets import load_widgets, show_notification

# Initialize database
conn = init_db()


def init_session_state() -> None:
    if "notification" not in st.session_state:
        st.session_state.notification = {"show": False, "message": "", "type": ""}
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "transaction_to_edit" not in st.session_state:
        st.session_state.transaction_to_edit = None
    if "current_transaction_type" not in st.session_state:
        st.session_state.current_transaction_type = None
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"


# Function to set notification
def set_notification(message, type="success"):
    st.session_state.notification = {"show": True, "message": message, "type": type}


# Function to update categories based on transaction type
def update_category_options():
    st.session_state.categories = get_categories(
        st.session_state.current_transaction_type
    )


# Function to handle page navigation
def on_page_change():
    st.session_state.page = st.session_state.navigation


def render_dashboard():
    st.header("Financial Dashboard")

    # Date filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    # Convert to string format for SQLite query
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Get filtered transactions
    transactions = get_transactions(start_date_str, end_date_str)

    if not transactions.empty:
        # Summary metrics
        income = transactions[transactions["transaction_type"] == "income"][
            "amount"
        ].sum()
        expenses = transactions[transactions["transaction_type"] == "expense"][
            "amount"
        ].sum()
        balance = income - expenses

        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Income", f"${income:.2f}")
        col2.metric("Expenses", f"${expenses:.2f}")
        col3.metric("Balance", f"${balance:.2f}")

        # Expenses by category
        st.subheader("Expenses by Category")
        expenses_by_category = (
            transactions[transactions["transaction_type"] == "expense"]
            .groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        if not expenses_by_category.empty:
            fig = px.pie(
                expenses_by_category,
                values="amount",
                names="category",
                title="Expense Distribution",
            )
            st.plotly_chart(fig)
        else:
            st.info("No expense data available for the selected period.")

        # Income vs Expenses over time
        st.subheader("Income vs Expenses")
        transactions["date"] = pd.to_datetime(transactions["date"])
        transactions["month"] = transactions["date"].dt.strftime("%Y-%m")

        monthly_summary = (
            transactions.groupby(["month", "transaction_type"])["amount"]
            .sum()
            .reset_index()
        )
        monthly_pivot = (
            monthly_summary.pivot(
                index="month", columns="transaction_type", values="amount"
            )
            .reset_index()
            .fillna(0)
        )

        if "income" in monthly_pivot.columns and "expense" in monthly_pivot.columns:
            fig = px.bar(
                monthly_pivot,
                x="month",
                y=["income", "expense"],
                title="Monthly Income vs Expenses",
                labels={"value": "Amount", "month": "Month", "variable": "Type"},
                barmode="group",
            )
            st.plotly_chart(fig)
        else:
            st.info("Not enough data for income vs expense comparison.")
    else:
        st.info("No transaction data available. Please add some transactions.")


def render_add_transaction():
    if st.session_state.edit_mode:
        st.header("Edit Transaction")
    else:
        st.header("Add New Transaction")

    col1, col2 = st.columns(2)

    # If in edit mode, pre-fill the form with transaction data
    if st.session_state.edit_mode and st.session_state.transaction_to_edit:
        transaction = st.session_state.transaction_to_edit

        with col1:
            # Initialize current_transaction_type if not set
            if st.session_state.current_transaction_type is None:
                st.session_state.current_transaction_type = transaction[
                    "transaction_type"
                ]

            transaction_type = st.selectbox(
                "Transaction Type",
                ["expense", "income"],
                index=0
                if st.session_state.current_transaction_type == "expense"
                else 1,
                key="edit_transaction_type",
                on_change=update_category_options,
            )
            # Update current_transaction_type when changed
            st.session_state.current_transaction_type = transaction_type

            date = st.date_input(
                "Date", datetime.strptime(transaction["date"], "%Y-%m-%d")
            )
            amount = st.number_input(
                "Amount",
                min_value=0.01,
                value=float(transaction["amount"]),
                format="%.2f",
            )

        with col2:
            # Get categories based on current transaction type
            if "categories" not in st.session_state:
                st.session_state.categories = get_categories(transaction_type)

            # Find the index of the current category in the list, default to 0 if not found
            category_index = 0
            if transaction["category"] in st.session_state.categories:
                category_index = st.session_state.categories.index(
                    transaction["category"]
                )

            category = st.selectbox(
                "Category", st.session_state.categories, index=category_index
            )
            description = st.text_input("Description", value=transaction["description"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Transaction"):
                date_str = date.strftime("%Y-%m-%d")
                update_transaction(
                    transaction["id"],
                    date_str,
                    amount,
                    category,
                    description or "",
                    transaction_type,
                )
                set_notification("Transaction updated successfully!", "success")
                st.session_state.edit_mode = False
                st.session_state.transaction_to_edit = None
                st.session_state.current_transaction_type = None
                if "categories" in st.session_state:
                    del st.session_state.categories
                st.rerun()

        with col2:
            if st.button("Cancel", key="cancel_edit"):
                st.session_state.edit_mode = False
                st.session_state.transaction_to_edit = None
                st.session_state.current_transaction_type = None
                if "categories" in st.session_state:
                    del st.session_state.categories
                st.rerun()
    else:
        with col1:
            transaction_type = st.selectbox("Transaction Type", ["expense", "income"])
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")

        with col2:
            # Get categories based on transaction type
            categories = get_categories(transaction_type)
            category = st.selectbox("Category", categories)
            description = st.text_input("Description")

        if st.button("Add Transaction"):
            date_str = date.strftime("%Y-%m-%d")
            add_transaction(date_str, amount, category, description, transaction_type)
            set_notification("Transaction added successfully!", "success")
            # Clear the form
            st.rerun()


def render_view_transactions():
    st.header("Transaction History")

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        start_date = st.date_input("Start Date", datetime.now().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    with col3:
        category_filter = st.selectbox("Category", ["All"] + get_categories())
    with col4:
        type_filter = st.selectbox("Type", ["All", "income", "expense"])

    # Convert to string format for SQLite query
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Get filtered transactions
    transactions = get_transactions(
        start_date_str,
        end_date_str,
        category_filter if category_filter != "All" else None,
        type_filter if type_filter != "All" else None,
    )

    if not transactions.empty:
        # Format the dataframe for display
        display_df = transactions.copy()
        display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%Y-%m-%d")
        display_df["amount"] = display_df.apply(lambda x: f"${x['amount']:.2f}", axis=1)

        # Add action buttons
        st.dataframe(
            display_df[
                ["id", "date", "description", "category", "transaction_type", "amount"]
            ],
            column_config={
                "id": "ID",
                "date": "Date",
                "description": "Description",
                "category": "Category",
                "transaction_type": "Type",
                "amount": "Amount",
            },
            use_container_width=True,
        )

        # Transaction actions (Edit/Delete)
        st.subheader("Transaction Actions")

        col1, col2 = st.columns(2)
        with col1:
            transaction_id = st.number_input(
                "Enter Transaction ID to Edit or Delete", min_value=1, step=1
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit Transaction"):
                transaction = get_transaction_by_id(transaction_id)
                if transaction:
                    st.session_state.edit_mode = True
                    st.session_state.transaction_to_edit = transaction
                    st.session_state.current_transaction_type = transaction[
                        "transaction_type"
                    ]
                    # Clear any existing categories to force refresh
                    if "categories" in st.session_state:
                        del st.session_state.categories
                    # Redirect to Add Transaction page
                    st.session_state.page = "Add Transaction"
                    st.rerun()
                else:
                    set_notification(
                        f"No transaction found with ID {transaction_id}", "error"
                    )

        with col2:
            if st.button("Delete Transaction"):
                transaction = get_transaction_by_id(transaction_id)
                if transaction:
                    delete_transaction(transaction_id)
                    set_notification(
                        f"Transaction {transaction_id} deleted successfully!", "success"
                    )
                    st.rerun()
                else:
                    set_notification(
                        f"No transaction found with ID {transaction_id}", "error"
                    )

        # Show total
        total = transactions["amount"].sum()
        st.info(f"Total: ${total:.2f}")
    else:
        st.info("No transactions found for the selected filters.")


def render_manage_categories():
    st.header("Manage Categories")

    # Display existing categories
    categories_df = pd.read_sql_query(
        "SELECT name, type FROM categories ORDER BY type, name", conn
    )

    st.subheader("Existing Categories")
    st.dataframe(categories_df, use_container_width=True)

    # Add new category
    st.subheader("Add New Category")

    col1, col2 = st.columns(2)

    with col1:
        new_category = st.text_input("Category Name")
    with col2:
        category_type = st.selectbox("Category Type", ["expense", "income"])

    if st.button("Add Category"):
        if new_category:
            success = add_category(new_category, category_type)
            if success:
                set_notification(
                    f"Added {new_category} as a {category_type} category.", "success"
                )
                st.rerun()
            else:
                set_notification("Category already exists!", "error")
        else:
            set_notification("Please enter a category name.", "error")


def main():
    # Set page configuration
    st.set_page_config(page_title="Personal Finance Tracker", layout="wide")
    init_session_state()

    # Load custom widgets
    load_widgets()

    # Display notification if any
    show_notification()

    # App title
    st.title("Personal Finance Tracker")

    # Sidebar navigation
    st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Add Transaction", "View Transactions", "Manage Categories"],
        index=[
            "Dashboard",
            "Add Transaction",
            "View Transactions",
            "Manage Categories",
        ].index(st.session_state.page),
        key="navigation",
        on_change=on_page_change,
    )

    # Use the session state page for rendering
    page = st.session_state.page

    # Render the appropriate page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Add Transaction":
        render_add_transaction()
    elif page == "View Transactions":
        render_view_transactions()
    elif page == "Manage Categories":
        render_manage_categories()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("Personal Finance Tracker v1.0")


if __name__ == "__main__":
    main()
