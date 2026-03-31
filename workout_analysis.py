import pandas as pd

# 1. Configuration
FILE_PATH = 'my_workouts.csv'

# 2. Load the data
df = pd.read_csv(FILE_PATH)

# Calculate Pace (min/km) for every activity so we can find the "best effort"
df['Pace_min_km'] = df['Duration_min'] / (df['Distance_km'] + 0.0001)

print("📊 ACTIVITY SUMMARY BY CATEGORY:")
print("-" * 40)

category_summary = df.groupby('Type').agg(
    Total_Distance_km=('Distance_km', 'sum'),
    Activity_Count=('Type', 'count')
).reset_index()

print(category_summary.to_string(index=False))
print(f"\nTotal overall distance: {df['Distance_km'].sum():.2f} km")

print("\n" + "=" * 50)
print("🏆 ADVANCED PERSONAL RECORDS")
print("=" * 50)

# Helper function to nicely print all stats for a specific workout
def print_workout_stats(workout, title):
    print(f"\n  {title}")
    print(f"    Name: {workout['Name']} | Date: {workout['Date']}")
    print(f"    Distance: {workout['Distance_km']:.2f} km | Duration: {workout['Duration_min']:.2f} min | Pace: {workout['Pace_min_km']:.2f} min/km")

# --- 🏃‍♂️ RUNNING RECORDS ---
runs = df[df['Type'] == 'Run']

if not runs.empty:
    print("\n🏃‍♂️ --- RUNNING ---")
    
    # Longest Distance 
    longest_dist_run = runs.loc[runs['Distance_km'].idxmax()]
    print_workout_stats(longest_dist_run, "🔸 Longest Distance:")
    
    # Milestone Records (5k, 10k, 20k, 40k)
    print("\n  🏅 Distance Milestones:")
    run_milestones = [5, 10, 20, 40]
    
    for milestone in run_milestones:
        qualifying_runs = runs[runs['Distance_km'] >= milestone]
        
        if not qualifying_runs.empty:
            best_run = qualifying_runs.loc[qualifying_runs['Pace_min_km'].idxmin()]
            milestone_time = best_run['Pace_min_km'] * milestone
            print(f"    - {milestone}km   Record: {milestone_time:.2f} min   Date : {best_run['Date']}")

# --- 🚴‍♂️ CYCLING RECORDS ---
rides = df[df['Type'] == 'Ride']

if not rides.empty:
    print("\n --- CYCLING ---")
    
    # Longest Distance 
    longest_dist_ride = rides.loc[rides['Distance_km'].idxmax()]
    print_workout_stats(longest_dist_ride, "🔸 Longest Distance:")
    
    # Milestone Records (20k, 50k, 100k)
    print("\n  🏅 Distance Milestones:")
    ride_milestones = [20, 50, 100]
    
    for milestone in ride_milestones:
        qualifying_rides = rides[rides['Distance_km'] >= milestone]
        
        if not qualifying_rides.empty:
            best_ride = qualifying_rides.loc[qualifying_rides['Pace_min_km'].idxmin()]
            milestone_time = best_ride['Pace_min_km'] * milestone
            print(f"    - {milestone}km    Record: {milestone_time:.2f} min    Date: '{best_ride['Date']}")

print("\n" + "=" * 50)