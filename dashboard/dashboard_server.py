from flask import Flask,render_template,redirect,request,jsonify
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from datetime import datetime
import numpy as np
import pickle
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

app = Flask(__name__)

def get_current_season():
    today = datetime.today()
    year = today.year
    seasons = {
       "Winter": (datetime(year, 12, 21), datetime(year + 1, 3, 20)),
        "Spring": (datetime(year, 3, 21), datetime(year, 6, 20)),
        "Monsoon": (datetime(year, 6, 21), datetime(year, 9, 22)),
        "Autumn": (datetime(year, 9, 23), datetime(year, 12, 20)),
    }
    for season, (start, end) in seasons.items():
        if start <= today <= end:
            return season
    return "Winter" if today.month == 12 else "Unknown"


def seasonal():
    df = pd.read_csv('medicinal_sales_tamil_nadu_100002.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    seasonal_revenue = df.groupby('Season').agg({'Revenue': 'sum'}).reset_index()
    fig = px.bar(seasonal_revenue, x='Season', y='Revenue',
                title='Total Revenue by Season',
                labels={'Season': 'Season', 'Revenue': 'Total Revenue'},
                color='Revenue', color_continuous_scale=px.colors.sequential.Plasma)
    fig.update_layout(xaxis_title='Season', yaxis_title='Total Revenue')
    plot_html2 = pio.to_html(fig, full_html=False)
    return plot_html2

def revenue():
    df = pd.read_csv('medicinal_sales_tamil_nadu_100002.csv')
    product_revenue = df.groupby('Product Name').agg({'Revenue': 'sum'}).reset_index()
    fig = px.bar(product_revenue, x='Product Name', y='Revenue',
                title='Revenue by Product',
                labels={'Product Name': 'Product Name', 'Revenue': 'Total Revenue'},
                color='Revenue')
    fig.update_layout(xaxis_title='Product Name', yaxis_title='Total Revenue')
    plot_html3 = pio.to_html(fig, full_html=False)
    return plot_html3

def dropdown_show(specific_pro):
    specific_product = specific_pro 
    df = pd.read_csv('medicinal_sales_tamil_nadu_100002.csv')
    product_data = df[df['Product Name'] == specific_product].copy()  # Use .copy() to create a copy of the slice
    product_data['Date'] = pd.to_datetime(product_data['Date'])
    product_data['Day of Week'] = product_data['Date'].dt.day_name()
    
    daily_sales_product = product_data.groupby('Day of Week').agg({'Quantity Sold': 'sum'}).reset_index()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_sales_product['Day of Week'] = pd.Categorical(daily_sales_product['Day of Week'], categories=days_order, ordered=True)
    daily_sales_product = daily_sales_product.sort_values('Day of Week')
    
    fig = px.bar(daily_sales_product, x='Day of Week', y='Quantity Sold',
                 title=f'Sales by Day of the Week for {specific_product}',
                 labels={'Day of Week': 'Day of the Week', 'Quantity Sold': 'Total Quantity Sold'},
                 color='Quantity Sold', color_continuous_scale=px.colors.sequential.Plasma)
    
    fig.update_layout(xaxis_title='Day of Week', yaxis_title='Total Quantity Sold')
    plot_html4 = pio.to_html(fig, full_html=False)
    
    return plot_html4

def check_monthly_customers():
    df = pd.read_csv('sales_data.csv', parse_dates=['Date'])
    results = []

    for customer, group in df.groupby('Customer Name'):
        group = group.sort_values('Date').reset_index(drop=True)
        group['YearMonth'] = group['Date'].dt.to_period('M')
        unique_months = group['YearMonth'].nunique()
        is_regular = (unique_months >= 6)
        most_frequent_product = group['Product Name'].mode().iloc[0] if not group['Product Name'].mode().empty else 'N/A'
        results.append({
            'Customer Name': customer,
            'Total Purchases': len(group),
            'Regular_Product': most_frequent_product,
            'Phone Number': group['Phonenumber'].iloc[0],
            'Is_Regular': is_regular
        })

    return pd.DataFrame(results)

@app.route('/')
def home():
    df = pd.read_csv('medicinal_sales_tamil_nadu_100002.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    total_sales = df.groupby('Product Name').agg({'Quantity Sold': 'sum'}).reset_index()
    top_10_sales = total_sales.sort_values(by='Quantity Sold', ascending=False).head(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_10_sales['Product Name'],
        y=top_10_sales['Quantity Sold'],
        marker_color='skyblue',
        name='Quantity Sold'
    ))
    top_product = top_10_sales.iloc[0]
    fig.add_trace(go.Bar(
        x=[top_product['Product Name']],
        y=[top_product['Quantity Sold']],
        marker_color='salmon',
        name='Top Selling Product'
    ))
    fig.update_layout(
        title='Top 10 Selling Products',
        xaxis_title='Product Name',
        yaxis_title='Total Quantity Sold',
        xaxis_tickangle=-45,
        barmode='group',
        showlegend=False
    )
    fig.add_annotation(
        x=top_product['Product Name'],
        y=top_product['Quantity Sold'] + 500,
        text=f'Top Product\n{top_product["Quantity Sold"]}',
        showarrow=True,
        arrowhead=2
    )
    plot_html = pio.to_html(fig, full_html=False)
    season_html  = seasonal()
    current_season = get_current_season()

    # -----------------------------------------
    results = check_monthly_customers()
    
    # Filter for regular customers
    regular_customers = results[results['Is_Regular'] == True][:7].sort_values(by='Total Purchases', ascending=False).reset_index(drop=True)
    regular_customers.index += 1

    # Render the template and pass the table data
    return render_template("index.html",plot_html=plot_html, season_html = season_html,season_data = current_season,tables=[regular_customers.to_html(classes='data')], titles=regular_customers.columns.values)

@app.route('/analyze_product', methods=['POST'])
def analyze_product():
    df = pd.read_csv('medicinal_sales_tamil_nadu_100002.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    total_sales = df.groupby('Product Name').agg({'Quantity Sold': 'sum'}).reset_index()
    top_10_sales = total_sales.sort_values(by='Quantity Sold', ascending=False).head(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_10_sales['Product Name'],
        y=top_10_sales['Quantity Sold'],
        marker_color='skyblue',
        name='Quantity Sold'
    ))
    top_product = top_10_sales.iloc[0]
    fig.add_trace(go.Bar(
        x=[top_product['Product Name']],
        y=[top_product['Quantity Sold']],
        marker_color='salmon',
        name='Top Selling Product'
    ))
    fig.update_layout(
        title='Top 10 Selling Products',
        xaxis_title='Product Name',
        yaxis_title='Total Quantity Sold',
        xaxis_tickangle=-45,
        barmode='group',
        showlegend=False
    )
    fig.add_annotation(
        x=top_product['Product Name'],
        y=top_product['Quantity Sold'] + 500,
        text=f'Top Product\n{top_product["Quantity Sold"]}',
        showarrow=True,
        arrowhead=2
    )
    plot_html = pio.to_html(fig, full_html=False)
    season_html  = seasonal()
    current_season = get_current_season()
    revenue_html = revenue()
    specific_product = request.form['product']
    dropdown_html = dropdown_show(specific_product)

    #-----------------------------------------------------
    results = check_monthly_customers()
    regular_customers = results[results['Is_Regular'] == True][:7].sort_values(by='Total Purchases', ascending=False).reset_index(drop=True)
    regular_customers.index += 1
    print("success")
    return render_template("index.html",plot_html=plot_html, season_html = season_html,season_data = current_season,dropdown_html = dropdown_html,tables=[regular_customers.to_html(classes='data')], titles=regular_customers.columns.values)


# ------------------------------------------------------------------------------------------------
def product_scope(product):
    df = pd.read_csv('medicinal_sales_tamil_nadu_100002.csv', parse_dates=['Date'])
    df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
    df['Quantity Sold'] = pd.to_numeric(df['Quantity Sold'], errors='coerce')
    df['Product Price'] = pd.to_numeric(df['Product Price'], errors='coerce')

    product_name = product
    df_product = df[df['Product Name'] == product_name]
    df_product = df_product.resample('ME', on='Date').sum()
    df_product['Month'] = df_product.index.month
    df_product['Quarter'] = df_product.index.quarter
    df_product['Year'] = df_product.index.year
    df_product['Day_of_Week'] = df_product.index.dayofweek
    features = ['Quantity Sold', 'Product Price', 'Month', 'Quarter', 'Year', 'Day_of_Week']
    X = df_product[features]
    y = df_product['Revenue']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    with open('xgboost_model.pkl', 'rb') as file:
        loaded_model = pickle.load(file)

    print("Model loaded from xgboost_model.pkl")
    loaded_y_pred = loaded_model.predict(X_test)
    loaded_y_pred = np.maximum(0, loaded_y_pred)
    loaded_rmse = np.sqrt(mean_squared_error(y_test, loaded_y_pred))
    print(f"Root Mean Squared Error (RMSE) using loaded model: {loaded_rmse:.2f}")
    end_date_actual = '2022-12-31'

    df_actual_up_to_2022 = df_product[df_product.index <= end_date_actual]

    start_date_predicted = df_product.index[-len(loaded_y_pred):].max()  # Last date in the test set
    df_loaded_predicted = X_test.copy()
    df_loaded_predicted['Predicted Revenue'] = loaded_y_pred
    df_loaded_predicted.index = pd.date_range(start=start_date_predicted, periods=len(loaded_y_pred), freq='ME')
    df_loaded_predicted = df_loaded_predicted.loc[df_loaded_predicted.index > end_date_actual]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_actual_up_to_2022.index,
                            y=df_actual_up_to_2022['Revenue'],
                            mode='lines+markers',
                            name='Actual Revenue',
                            line=dict(color='black'),
                            marker=dict(symbol='circle')))

    fig.add_trace(go.Scatter(x=df_loaded_predicted.index,
                            y=df_loaded_predicted['Predicted Revenue'],
                            mode='lines+markers',
                            name='Predicted Revenue (Loaded Model)',
                            line=dict(color='green', dash='dash'),
                            marker=dict(symbol='x')))

    # Update layout
    fig.update_layout(
        title=f'Revenue Prediction for {product_name} (Loaded Model)',
        xaxis_title='Date',
        yaxis_title='Revenue',
        yaxis=dict(range=[-df_product['Revenue'].max() * 0.5, df_product['Revenue'].max() * 1.5]),
        xaxis_rangeslider_visible=True,
        legend=dict(x=0.5, y=1, traceorder='normal', orientation='h'),
        plot_bgcolor='white'
        )

    # Add baseline for zero
    fig.add_shape(
        type="line",
        x0=df_product.index.min(),
        y0=0,
        x1=df_product.index.max(),
        y1=0,
        line=dict(color="gray", width=0.8, dash="dash")
    )

    # Generate HTML code for the plot
    plot_html = pio.to_html(fig, full_html=False)
    return plot_html

def seasonal_scope1(prod):
    df = pd.read_csv('medicinal_sales_tamil_nadu_100002.csv')
    df['Date'] = pd.to_datetime(df['Date'])

    product_name = prod  # Replace with the specific product
    product_data = df[df['Product Name'] == product_name]
    product_data = product_data.groupby('Date').agg({'Quantity Sold': 'sum'}).reset_index()
    product_data.columns = ['ds', 'y']  # Prophet requires columns to be named 'ds' and 'y']

    product_data = product_data.fillna(method='ffill')

    with open('prophet_model1.pkl', 'rb') as file:
        model = pickle.load(file)

    future = model.make_future_dataframe(periods=365)  # Forecast for one year into the future
    forecast = model.predict(future)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=product_data['ds'], y=product_data['y'], mode='lines', name='Actual Sales', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='red')))

    fig.update_layout(title=f'Seasonal Sales Forecast for {product_name}', xaxis_title='Date', yaxis_title='Quantity Sold')
    plot_html = pio.to_html(fig, full_html=False)
    return plot_html

@app.route('/forecasting')
def forecasting():
    prod = 'Mirtazapine'
    future_scope = product_scope(prod)
    seasonal_scope = seasonal_scope1(prod)
    return render_template('forcasting.html',future_scope=future_scope,seasonal_scope=seasonal_scope)


@app.route('/analyze_product_selected', methods=['POST'])
def analyze_product_selected():
    prod = request.form['product']
    future_scope = product_scope(prod)
    seasonal_scope = seasonal_scope1(prod)
    return render_template('forcasting.html',future_scope=future_scope,seasonal_scope = seasonal_scope)

# smart dashboard


if "__main__" == __name__:
    app.run(debug=True, host='0.0.0.0',port=5003)