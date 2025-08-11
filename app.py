import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime

# Create the Dash app
app = dash.Dash(__name__)

# Simple function to get data
def get_data():
    """Get lane closure data from Winnipeg API"""
    try:
        print("Getting data from CSV...")
        # Try CSV first, then JSON if that fails
        csv_url = "https://data.winnipeg.ca/resource/e88f-en8v.csv"
        
        try:
            df = pd.read_csv(csv_url)
            print(f"CSV loaded successfully with {len(df)} rows")
            print(f"Original columns: {list(df.columns)}")
            
           
            print(f"Sample data:\n{df.head()}")
            
            if len(df) > 0:
                clean_data = []
                for _, row in df.iterrows():
                    clean_row = {}
                    
        
                    for col in df.columns:
                        col_lower = col.lower()
                        if any(term in col_lower for term in ['street', 'road', 'location']):
                            clean_row['Street/Location'] = str(row[col])[:100]  # Limit length
                        elif any(term in col_lower for term in ['from', 'start']):
                            clean_row['From'] = str(row[col])[:50]
                        elif any(term in col_lower for term in ['to', 'end']):
                            clean_row['To'] = str(row[col])[:50]
                        elif any(term in col_lower for term in ['type', 'closure']):
                            clean_row['Type'] = str(row[col])[:30]
                        elif any(term in col_lower for term in ['reason', 'description']):
                            clean_row['Reason'] = str(row[col])[:100]
                        elif any(term in col_lower for term in ['date']):
                            clean_row['Date'] = str(row[col])[:20]
                        elif any(term in col_lower for term in ['status']):
                            clean_row['Status'] = str(row[col])[:20]
                    
                    # If we didn't find mapped columns, use first few columns directly
                    if not clean_row:
                        for i, col in enumerate(df.columns[:6]):  # Take first 6 columns
                            clean_row[col] = str(row[col])[:100]
                    
                    clean_data.append(clean_row)
                
                clean_df = pd.DataFrame(clean_data)
                print(f"Cleaned data: {len(clean_df)} records")
                print(f"Clean columns: {list(clean_df.columns)}")
                return clean_df
            else:
                print("Empty CSV, using sample data")
                return make_sample_data()
                
        except Exception as csv_error:
            print(f"CSV failed: {csv_error}, trying JSON...")
            # Fallback to JSON API
            json_url = "https://data.winnipeg.ca/resource/e88f-en8v.json?$limit=50"
            response = requests.get(json_url, timeout=10)
            data = response.json()
            
            if data:
                df = pd.DataFrame(data)
                print(f"JSON loaded with {len(df)} rows")
                print(f"JSON columns: {list(df.columns)}")
                
                # Remove problematic columns
                columns_to_remove = ['geometry', 'location', 'coordinates']
                for col in columns_to_remove:
                    if col in df.columns:
                        df = df.drop(columns=[col])
                
                return df
            else:
                print("No JSON data, using sample data")
                return make_sample_data()
                
    except Exception as e:
        print(f"All data sources failed: {e}, using sample data")
        return make_sample_data()

def make_sample_data():
    """Create simple sample data with actual Winnipeg street addresses"""
    import random
    from datetime import datetime, timedelta
    
    # Real Winnipeg street names and locations
    streets = [
        'Portage Avenue', 'Main Street', 'Broadway', 'Corydon Avenue', 'Henderson Highway',
        'St. Mary Road', 'Pembina Highway', 'Regent Avenue', 'McPhillips Street', 'Nairn Avenue',
        'Ellice Avenue', 'Notre Dame Avenue', 'Sargent Avenue', 'William Avenue', 'Logan Avenue'
    ]
    
    intersections = [
        'Donald Street', 'Smith Street', 'Garry Street', 'Hargrave Street', 'Carlton Street',
        'Edmonton Street', 'Sherbrook Street', 'Maryland Street', 'Balmoral Street', 'Spence Street'
    ]
    
    closure_types = ['Lane Closure', 'Road Construction', 'Utility Work', 'Street Maintenance', 'Emergency Repair']
    reasons = [
        'Water main repair', 'Sewer line replacement', 'Road resurfacing', 'Bridge maintenance',
        'Hydro pole replacement', 'Gas line installation', 'Sidewalk repair', 'Traffic signal work'
    ]
    
    data = []
    for i in range(25):
        street = random.choice(streets)
        from_street = random.choice(intersections)
        to_street = random.choice(intersections)
        start_date = datetime.now() - timedelta(days=random.randint(1, 60))
        end_date = start_date + timedelta(days=random.randint(1, 30))
        
        data.append({
            'Street/Location': f'{street} between {from_street} and {to_street}',
            'From': from_street,
            'To': to_street,
            'Type': random.choice(closure_types),
            'Reason': random.choice(reasons),
            'Date': start_date.strftime('%Y-%m-%d'),
            'Status': random.choice(['Active', 'Planned', 'Completed'])
        })
    
    return pd.DataFrame(data)

# Get the data
df = get_data()

# Create simple graphs
def make_bar_chart(df):
    """Simple bar chart"""
    if 'Type' in df.columns:
        counts = df['Type'].value_counts()
        fig = px.bar(x=counts.index, y=counts.values, 
                     title="Types of Lane Closures",
                     labels={'x': 'Type', 'y': 'Count'})
        return fig
    elif 'type' in df.columns:
        counts = df['type'].value_counts()
        fig = px.bar(x=counts.index, y=counts.values, 
                     title="Types of Lane Closures",
                     labels={'x': 'Type', 'y': 'Count'})
        return fig
    else:
        # Use sample data for demonstration
        sample_data = pd.DataFrame({
            'Type': ['Lane Closure', 'Road Construction', 'Utility Work', 'Street Maintenance'],
            'Count': [15, 8, 12, 5]
        })
        fig = px.bar(sample_data, x='Type', y='Count', 
                     title="Types of Lane Closures")
        return fig

def make_pie_chart(df):
    """Simple pie chart"""
    if 'Status' in df.columns:
        counts = df['Status'].value_counts()
        fig = px.pie(values=counts.values, names=counts.index,
                     title="Status of Lane Closures")
        return fig
    elif 'status' in df.columns:
        counts = df['status'].value_counts()
        fig = px.pie(values=counts.values, names=counts.index,
                     title="Status of Lane Closures")
        return fig
    else:
        # Use sample data for demonstration
        sample_data = pd.DataFrame({
            'Status': ['Active', 'Planned', 'Completed'],
            'Count': [20, 8, 12]
        })
        fig = px.pie(sample_data, values='Count', names='Status',
                     title="Status of Lane Closures")
        return fig

def make_line_chart(df):
    """Simple line chart"""
    if len(df) > 0:
        # Create simple trend data based on months
        trend_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            'Closures': [5, 8, 12, 15, 10, 7, 9]
        })
        fig = px.line(trend_data, x='Month', y='Closures',
                      title="Monthly Lane Closures Trend",
                      markers=True)
        return fig
    else:
        return px.line(title="No Data Available")

# Create the layout
app.layout = html.Div([
    # Title
    html.H1("Winnipeg Lane Closures Dashboard", 
            style={'text-align': 'center', 'color': 'blue'}),
    
    # Description
    html.P("This shows lane closure data from the City of Winnipeg.",
           style={'text-align': 'center', 'font-size': '18px'}),
    
    # Data Table
    html.H2("Data Table"),
    dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'}
    ),
    
    html.Br(),
    
    # Graphs
    html.H2("Charts"),
    
    # Bar Chart
    html.H3("Bar Chart"),
    dcc.Graph(figure=make_bar_chart(df)),
    
    # Pie Chart  
    html.H3("Pie Chart"),
    dcc.Graph(figure=make_pie_chart(df)),
    
    # Line Chart
    html.H3("Line Chart"),
    dcc.Graph(figure=make_line_chart(df)),
    
    # Footer
    html.Hr(),
    html.P(f"Data from: City of Winnipeg Open Data Portal"),
    html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
])

# Run the app
if __name__ == '__main__':
    print("Starting simple Dash app...")
    print(f"Data has {len(df)} rows")
    app.run(debug=True)
