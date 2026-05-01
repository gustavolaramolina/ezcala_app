"""Ezcala Cash Intelligence Dashboard - Streamlit Application

Modern interactive dashboard for cash flow analysis, payment matching,
customer risk scoring, and financial insights.

To run:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List

from modules import sync_agent, matching_agent, scoring_agent, insights_agent
from modules.data_cache import data_cache


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Ezcala Cash Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# CACHED DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data
def load_data():
    """Load invoices and payments from JSON files."""
    return sync_agent.sync()


@st.cache_data
def run_matching():
    """Execute payment-to-invoice matching algorithm."""
    return matching_agent.reconcile()


@st.cache_data
def compute_customer_scores():
    """Calculate risk scores for all customers."""
    return scoring_agent.compute_scores()


@st.cache_data
def generate_ai_insights():
    """Generate cash flow insights summary."""
    return insights_agent.generate_insights()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_date(date_str: str) -> datetime:
    """Parse YYYY-MM-DD date string to datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def calculate_days_overdue(due_date_str: str, reference_date: datetime = None) -> int:
    """Calculate days overdue from due date."""
    if reference_date is None:
        reference_date = datetime.today()
    due_date = parse_date(due_date_str)
    days = (reference_date - due_date).days
    return max(0, days)


def get_aging_bucket(days_overdue: int) -> str:
    """Categorize invoice into aging bucket."""
    if days_overdue <= 0:
        return "Current"
    elif days_overdue <= 30:
        return "1-30 days"
    elif days_overdue <= 60:
        return "31-60 days"
    elif days_overdue <= 90:
        return "61-90 days"
    else:
        return "90+ days"


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_ar_aging_chart(invoices: List[Dict]) -> go.Figure:
    """Create AR aging analysis bar chart."""
    # Calculate aging for each invoice
    aging_data = []
    for inv in invoices:
        days = calculate_days_overdue(inv["due_date"])
        bucket = get_aging_bucket(days)
        aging_data.append({
            "bucket": bucket,
            "amount": inv.get("balance", 0.0)
        })
    
    df = pd.DataFrame(aging_data)
    if df.empty:
        return go.Figure()
    
    # Group by bucket
    bucket_order = ["Current", "1-30 days", "31-60 days", "61-90 days", "90+ days"]
    grouped = df.groupby("bucket")["amount"].sum().reindex(bucket_order, fill_value=0).reset_index()
    
    # Create bar chart with color gradient
    fig = px.bar(
        grouped,
        x="bucket",
        y="amount",
        title="AR Aging Analysis",
        labels={"bucket": "Aging Bucket", "amount": "Outstanding Amount ($)"},
        color="amount",
        color_continuous_scale="Reds",
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Aging Bucket",
        yaxis_title="Outstanding Amount ($)",
    )
    
    return fig


def create_risk_score_chart(scores: Dict[str, float]) -> go.Figure:
    """Create customer risk score horizontal bar chart."""
    if not scores:
        return go.Figure()
    
    df = pd.DataFrame([
        {"customer": k, "score": v}
        for k, v in sorted(scores.items(), key=lambda x: x[1])
    ])
    
    # Color coding: red (low score/high risk), yellow (medium), green (high score/low risk)
    colors = ["red" if s < 50 else "orange" if s < 75 else "green" for s in df["score"]]
    
    fig = go.Figure(go.Bar(
        x=df["score"],
        y=df["customer"],
        orientation='h',
        marker=dict(color=colors),
        text=df["score"].round(1),
        textposition='outside',
    ))
    
    fig.update_layout(
        title="Customer Risk Scores (Lower = Higher Risk)",
        xaxis_title="Risk Score",
        yaxis_title="Customer",
        height=max(300, len(df) * 50),
        showlegend=False,
    )
    
    return fig


def create_match_confidence_chart(matches: List[Dict]) -> go.Figure:
    """Create match confidence distribution pie chart."""
    if not matches:
        return go.Figure()
    
    # Categorize matches by confidence
    high_conf = sum(1 for m in matches if m.get("confidence", 0) >= 0.9)
    low_conf = len(matches) - high_conf
    
    fig = go.Figure(data=[go.Pie(
        labels=["High Confidence (≥0.9)", "Low Confidence (<0.9)"],
        values=[high_conf, low_conf],
        hole=0.3,
        marker=dict(colors=["#2ecc71", "#e74c3c"]),
    )])
    
    fig.update_layout(
        title="Match Confidence Distribution",
        height=400,
    )
    
    return fig


def create_payment_timeline_chart(payments: List[Dict]) -> go.Figure:
    """Create payment timeline line chart."""
    if not payments:
        return go.Figure()
    
    df = pd.DataFrame(payments)
    df["payment_date"] = pd.to_datetime(df["payment_date"])
    df = df.sort_values("payment_date")
    df["cumulative_amount"] = df["amount"].cumsum()
    
    fig = px.line(
        df,
        x="payment_date",
        y="cumulative_amount",
        title="Cumulative Payment Timeline",
        labels={"payment_date": "Payment Date", "cumulative_amount": "Cumulative Amount ($)"},
        markers=True,
    )
    
    fig.update_layout(height=400)
    
    return fig


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Title
    st.title("💰 Ezcala Cash Intelligence Dashboard")
    st.markdown("**Real-time cash flow analysis, payment matching, and customer risk insights**")
    
    # ========================================================================
    # SIDEBAR - Controls and Filters
    # ========================================================================
    
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Manual sync button
        if st.button("🔄 Sync Data", type="primary", use_container_width=True):
            # Clear all caches to reload data
            st.cache_data.clear()
            load_data()
            st.success("Data synced successfully!")
            st.rerun()
        
        st.divider()
        
        st.header("🔍 Filters")
        
        # Initialize session state for data
        if "data_loaded" not in st.session_state:
            st.session_state.data_loaded = False
        
        # Check if data is available
        has_data = len(data_cache.invoices) > 0
        
        if has_data:
            # Customer filter
            all_customers = sorted(set(
                inv["customer_id"] for inv in data_cache.invoices
            ))
            selected_customer = st.selectbox(
                "Customer",
                ["All"] + all_customers,
                key="customer_filter"
            )
            
            # Date range filter
            st.subheader("Date Range")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "From",
                    value=datetime(2025, 12, 1),
                    key="start_date"
                )
            with col2:
                end_date = st.date_input(
                    "To",
                    value=datetime.today(),
                    key="end_date"
                )
            
            # Confidence threshold filter
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.1,
                key="confidence_threshold"
            )
        else:
            st.info("👆 Click 'Sync Data' to load data and enable filters")
    
    # ========================================================================
    # MAIN CONTENT
    # ========================================================================
    
    # Load data if not loaded
    if not has_data:
        st.info("👈 Click **'Sync Data'** in the sidebar to load invoices and payments.")
        st.stop()
    
    # Load data and run agents
    data = load_data()
    matches = run_matching()
    scores = compute_customer_scores()
    insights = generate_ai_insights()
    
    # Apply customer filter
    if selected_customer != "All":
        filtered_invoices = [inv for inv in data_cache.invoices if inv["customer_id"] == selected_customer]
        filtered_payments = [pmt for pmt in data_cache.payments if pmt["customer_id"] == selected_customer]
        filtered_matches = [m for m in matches if any(
            inv["invoice_id"] == m["invoice_id"] and inv["customer_id"] == selected_customer
            for inv in data_cache.invoices
        )]
    else:
        filtered_invoices = data_cache.invoices
        filtered_payments = data_cache.payments
        filtered_matches = matches
    
    # ========================================================================
    # KPI METRICS
    # ========================================================================
    
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ar = sum(inv.get("balance", 0) for inv in filtered_invoices)
        st.metric(
            label="Total AR Outstanding",
            value=f"${total_ar:,.2f}",
            delta=None,
        )
    
    with col2:
        total_payments = sum(pmt["amount"] for pmt in filtered_payments)
        matched_amount = sum(m["amount_applied"] for m in filtered_matches)
        unmatched = total_payments - matched_amount
        st.metric(
            label="Unmatched Payments",
            value=f"${unmatched:,.2f}",
            delta=None,
        )
    
    with col3:
        if filtered_invoices:
            avg_overdue = sum(
                calculate_days_overdue(inv["due_date"]) for inv in filtered_invoices
            ) / len(filtered_invoices)
        else:
            avg_overdue = 0
        st.metric(
            label="Avg Days Overdue",
            value=f"{avg_overdue:.0f}",
            delta=None,
        )
    
    with col4:
        if total_payments > 0:
            collection_rate = (matched_amount / total_payments) * 100
        else:
            collection_rate = 0
        st.metric(
            label="Collection Effectiveness",
            value=f"{collection_rate:.1f}%",
            delta=None,
        )
    
    st.divider()
    
    # ========================================================================
    # TABS
    # ========================================================================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "🧾 Invoices",
        "💳 Payments",
        "🔗 Matches",
        "💡 Insights"
    ])
    
    # ------------------------------------------------------------------------
    # TAB 1: OVERVIEW
    # ------------------------------------------------------------------------
    
    with tab1:
        st.header("Dashboard Overview")
        
        # Charts in 2 columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                create_ar_aging_chart(filtered_invoices),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                create_match_confidence_chart(filtered_matches),
                use_container_width=True
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.plotly_chart(
                create_risk_score_chart(scores),
                use_container_width=True
            )
        
        with col4:
            st.plotly_chart(
                create_payment_timeline_chart(filtered_payments),
                use_container_width=True
            )
    
    # ------------------------------------------------------------------------
    # TAB 2: INVOICES
    # ------------------------------------------------------------------------
    
    with tab2:
        st.header("Invoice Details")
        
        if filtered_invoices:
            # Convert to DataFrame
            df_invoices = pd.DataFrame(filtered_invoices)
            
            # Add calculated columns
            df_invoices["days_overdue"] = df_invoices["due_date"].apply(calculate_days_overdue)
            df_invoices["aging_bucket"] = df_invoices["days_overdue"].apply(get_aging_bucket)
            
            # Format for display
            df_display = df_invoices[[
                "invoice_id", "customer_id", "invoice_date", "due_date",
                "amount", "balance", "days_overdue", "aging_bucket"
            ]].copy()
            
            # Display dataframe
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "invoice_id": "Invoice ID",
                    "customer_id": "Customer",
                    "invoice_date": st.column_config.DateColumn("Invoice Date", format="YYYY-MM-DD"),
                    "due_date": st.column_config.DateColumn("Due Date", format="YYYY-MM-DD"),
                    "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                    "balance": st.column_config.NumberColumn("Balance", format="$%.2f"),
                    "days_overdue": st.column_config.NumberColumn("Days Overdue"),
                    "aging_bucket": "Aging Bucket",
                }
            )
            
            # Summary stats
            st.subheader("Invoice Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Invoices", len(filtered_invoices))
            with col2:
                st.metric("Total Amount", f"${df_invoices['amount'].sum():,.2f}")
            with col3:
                st.metric("Outstanding Balance", f"${df_invoices['balance'].sum():,.2f}")
        else:
            st.info("No invoices to display")
    
    # ------------------------------------------------------------------------
    # TAB 3: PAYMENTS
    # ------------------------------------------------------------------------
    
    with tab3:
        st.header("Payment Details")
        
        if filtered_payments:
            df_payments = pd.DataFrame(filtered_payments)
            
            # Display dataframe
            st.dataframe(
                df_payments,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "payment_id": "Payment ID",
                    "customer_id": "Customer",
                    "payment_date": st.column_config.DateColumn("Payment Date", format="YYYY-MM-DD"),
                    "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                    "reference": "Reference",
                }
            )
            
            # Summary stats
            st.subheader("Payment Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Payments", len(filtered_payments))
            with col2:
                st.metric("Total Amount", f"${df_payments['amount'].sum():,.2f}")
            with col3:
                avg_payment = df_payments['amount'].mean()
                st.metric("Average Payment", f"${avg_payment:,.2f}")
        else:
            st.info("No payments to display")
    
    # ------------------------------------------------------------------------
    # TAB 4: MATCHES
    # ------------------------------------------------------------------------
    
    with tab4:
        st.header("Payment Matching Results")
        
        if filtered_matches:
            df_matches = pd.DataFrame(filtered_matches)
            
            # Filter by confidence threshold
            df_filtered = df_matches[df_matches["confidence"] >= confidence_threshold]
            
            st.info(f"Showing {len(df_filtered)} matches with confidence ≥ {confidence_threshold}")
            
            # Display dataframe
            st.dataframe(
                df_filtered,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "payment_id": "Payment ID",
                    "invoice_id": "Invoice ID",
                    "amount_applied": st.column_config.NumberColumn("Amount Applied", format="$%.2f"),
                    "confidence": st.column_config.ProgressColumn(
                        "Confidence",
                        min_value=0.0,
                        max_value=1.0,
                        format="%.2f"
                    ),
                }
            )
            
            # Summary stats
            st.subheader("Match Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Matches", len(df_matches))
            with col2:
                high_conf = len(df_matches[df_matches["confidence"] >= 0.9])
                st.metric("High Confidence", f"{high_conf} ({high_conf/len(df_matches)*100:.0f}%)")
            with col3:
                total_matched = df_matches["amount_applied"].sum()
                st.metric("Total Matched", f"${total_matched:,.2f}")
        else:
            st.info("No matches to display. Run matching algorithm first.")
    
    # ------------------------------------------------------------------------
    # TAB 5: INSIGHTS
    # ------------------------------------------------------------------------
    
    with tab5:
        st.header("AI-Generated Insights")
        
        # Display insights
        st.markdown("### Cash Flow Summary")
        st.info(insights)
        
        # Display customer scores
        if scores:
            st.markdown("### Customer Risk Scores")
            st.markdown("*Lower scores indicate higher collection priority*")
            
            df_scores = pd.DataFrame([
                {"Customer": k, "Risk Score": v, "Priority": "High" if v < 50 else "Medium" if v < 75 else "Low"}
                for k, v in sorted(scores.items(), key=lambda x: x[1])
            ])
            
            st.dataframe(
                df_scores,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Customer": "Customer ID",
                    "Risk Score": st.column_config.NumberColumn("Risk Score", format="%.2f"),
                    "Priority": st.column_config.TextColumn("Collection Priority"),
                }
            )


if __name__ == "__main__":
    main()
