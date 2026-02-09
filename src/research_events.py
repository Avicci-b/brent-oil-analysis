"""
Script to research and compile historical events affecting Brent oil prices.
Focus on 2012-2022 period (past decade).
"""

import pandas as pd
from datetime import datetime
import requests
import json
from pathlib import Path

def research_events_manual():
    """
    Manual research based on known geopolitical and economic events.
    Returns a list of events with dates and descriptions.
    """
    
    events = [
        # 2012-2014: Middle East tensions, shale boom
        {
            "event_date": "2012-07-01",
            "event_name": "EU imposes oil embargo on Iran",
            "event_type": "Geopolitical/Sanctions",
            "description": "European Union imposes full oil embargo on Iran over nuclear program concerns",
            "expected_impact": "Price increase due to supply concerns",
            "region": "Middle East",
            "severity": "High"
        },
        {
            "event_date": "2014-06-20",
            "event_name": "ISIS captures Iraqi oil fields",
            "event_type": "Geopolitical/Conflict",
            "description": "ISIS militants capture key oil fields in northern Iraq, disrupting production",
            "expected_impact": "Price spike due to supply disruption fears",
            "region": "Middle East",
            "severity": "Medium"
        },
        {
            "event_date": "2014-11-27",
            "event_name": "OPEC maintains production despite price drop",
            "event_type": "OPEC Decision",
            "description": "OPEC decides to maintain production levels despite falling prices, targeting US shale producers",
            "expected_impact": "Price decrease due to oversupply concerns",
            "region": "Global",
            "severity": "High"
        },
        
        # 2015-2016: Iran nuclear deal, price collapse
        {
            "event_date": "2015-07-14",
            "event_name": "Iran nuclear deal signed",
            "event_type": "Geopolitical/Diplomatic",
            "description": "P5+1 countries sign Joint Comprehensive Plan of Action with Iran, lifting oil sanctions",
            "expected_impact": "Price decrease as Iranian oil returns to market",
            "region": "Middle East",
            "severity": "High"
        },
        {
            "event_date": "2016-02-16",
            "event_name": "Doha freeze agreement fails",
            "event_type": "OPEC Decision",
            "description": "OPEC and Russia fail to agree on production freeze at Doha meeting",
            "expected_impact": "Price volatility and uncertainty",
            "region": "Global",
            "severity": "Medium"
        },
        {
            "event_date": "2016-11-30",
            "event_name": "OPEC+ production cut agreement",
            "event_type": "OPEC Decision",
            "description": "OPEC and non-OPEC producers agree to cut production by 1.8 million barrels per day",
            "expected_impact": "Price increase due to coordinated supply reduction",
            "region": "Global",
            "severity": "High"
        },
        
        # 2017-2018: US shale growth, geopolitical tensions
        {
            "event_date": "2017-11-05",
            "event_name": "Saudi Arabia anti-corruption crackdown",
            "event_type": "Geopolitical/Political",
            "description": "Saudi Crown Prince arrests royals and businessmen in anti-corruption purge",
            "expected_impact": "Price volatility due to political uncertainty",
            "region": "Middle East",
            "severity": "Medium"
        },
        {
            "event_date": "2018-05-08",
            "event_name": "US withdraws from Iran nuclear deal",
            "event_type": "Geopolitical/Sanctions",
            "description": "US unilaterally withdraws from JCPOA and reimposes sanctions on Iran",
            "expected_impact": "Price increase due to expected supply reduction",
            "region": "Middle East",
            "severity": "High"
        },
        {
            "event_date": "2018-12-07",
            "event_name": "OPEC+ agrees to cut production",
            "event_type": "OPEC Decision",
            "description": "OPEC and allies agree to cut 1.2 million barrels per day to stabilize prices",
            "expected_impact": "Price increase due to supply reduction",
            "region": "Global",
            "severity": "High"
        },
        
        # 2019-2020: Pandemic, price war, unprecedented volatility
        {
            "event_date": "2019-09-14",
            "event_name": "Drone attacks on Saudi Aramco facilities",
            "event_type": "Geopolitical/Attack",
            "description": "Drone attacks on Abqaiq and Khurais oil facilities disrupt 5.7 million bpd production",
            "expected_impact": "Largest price spike in history due to supply shock",
            "region": "Middle East",
            "severity": "Very High"
        },
        {
            "event_date": "2020-03-06",
            "event_name": "OPEC+ price war begins",
            "event_type": "OPEC Decision",
            "description": "Russia rejects OPEC production cuts, leading to Saudi-Russia price war",
            "expected_impact": "Price collapse due to oversupply fears",
            "region": "Global",
            "severity": "Very High"
        },
        {
            "event_date": "2020-04-20",
            "event_name": "WTI crude futures go negative",
            "event_type": "Economic/Market",
            "description": "WTI May 2020 futures contract closes at -$37.63 due to storage capacity concerns",
            "expected_impact": "Extreme market volatility and panic selling",
            "region": "Global",
            "severity": "Very High"
        },
        {
            "event_date": "2020-04-12",
            "event_name": "OPEC+ historic production cut",
            "event_type": "OPEC Decision",
            "description": "OPEC+ agrees to cut 9.7 million bpd, largest reduction in history",
            "expected_impact": "Price stabilization after historic collapse",
            "region": "Global",
            "severity": "Very High"
        },
        
        # 2021-2022: Recovery, Ukraine conflict
        {
            "event_date": "2021-11-23",
            "event_name": "US announces strategic petroleum reserve release",
            "event_type": "Government Policy",
            "description": "US coordinates with other countries to release 50 million barrels from SPR",
            "expected_impact": "Temporary price decrease from increased supply",
            "region": "North America",
            "severity": "Medium"
        },
        {
            "event_date": "2022-02-24",
            "event_name": "Russia invades Ukraine",
            "event_type": "Geopolitical/Conflict",
            "description": "Full-scale Russian invasion of Ukraine begins",
            "expected_impact": "Massive price spike due to sanctions and supply fears",
            "region": "Europe",
            "severity": "Very High"
        },
        {
            "event_date": "2022-03-08",
            "event_name": "US bans Russian oil imports",
            "event_type": "Economic/Sanctions",
            "description": "US announces ban on Russian oil, gas, and energy imports",
            "expected_impact": "Further price increase and market dislocation",
            "region": "Global",
            "severity": "High"
        },
        {
            "event_date": "2022-06-02",
            "event_name": "EU agrees to partial Russian oil embargo",
            "event_type": "Economic/Sanctions",
            "description": "EU agrees to ban 90% of Russian oil imports by end of 2022",
            "expected_impact": "Structural market change and price support",
            "region": "Europe",
            "severity": "High"
        }
    ]
    
    return events

def create_event_dataframe():
    """Create DataFrame from researched events."""
    events = research_events_manual()
    df = pd.DataFrame(events)
    
    # Ensure date is datetime
    df['event_date'] = pd.to_datetime(df['event_date'])
    
    # Sort by date
    df = df.sort_values('event_date').reset_index(drop=True)
    
    return df

def save_events_to_csv(df, output_path="data/historical_events.csv"):
    """Save events DataFrame to CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} events to {output_path}")
    
    # Also save to processed folder for reference
    processed_path = Path("data/processed/historical_events.csv")
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    
    return output_path

def analyze_event_distribution(df):
    """Analyze event distribution by type, year, and severity."""
    print("\n=== Event Distribution Analysis ===")
    print(f"Total events: {len(df)}")
    
    # Events by year
    df['year'] = df['event_date'].dt.year
    yearly_counts = df['year'].value_counts().sort_index()
    print("\nEvents by year:")
    for year, count in yearly_counts.items():
        print(f"  {year}: {count}")
    
    # Events by type
    type_counts = df['event_type'].value_counts()
    print("\nEvents by type:")
    for event_type, count in type_counts.items():
        print(f"  {event_type}: {count}")
    
    # Events by severity
    severity_counts = df['severity'].value_counts()
    print("\nEvents by severity:")
    for severity, count in severity_counts.items():
        print(f"  {severity}: {count}")
    
    # Events by region
    region_counts = df['region'].value_counts()
    print("\nEvents by region:")
    for region, count in region_counts.items():
        print(f"  {region}: {count}")

def main():
    """Main function to research and save events."""
    print("Researching historical events affecting Brent oil prices...")
    
    # Create events DataFrame
    df = create_event_dataframe()
    
    # Display sample
    print("\nSample events:")
    print(df[['event_date', 'event_name', 'event_type', 'severity']].head())
    
    # Analyze distribution
    analyze_event_distribution(df)
    
    # Save to CSV
    output_path = save_events_to_csv(df)
    
    print(f"\n✅ Event research complete! Saved {len(df)} events.")
    print(f"📊 Event breakdown: {len(df[df['severity'] == 'Very High'])} very high impact, "
          f"{len(df[df['severity'] == 'High'])} high impact")
    
    return df

if __name__ == "__main__":
    df = main()