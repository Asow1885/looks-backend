import pandas as pd
import tkinter as tk
import webbrowser
import os
import csv
from tkinter import messagebox
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Load port list
port_df = pd.read_csv("../data/live_ports_wiki.csv")
port_list = port_df["Port"].dropna().unique().tolist()

# App setup
root = tk.Tk()
root.title("Logistics + Map Viewer")
root.geometry("400x650")

map_path = os.path.abspath("../data/port_map.html")

# === Functions ===
def submit_shipment():
    origin = origin_entry.get()
    destination = destination_entry.get()
    cost = cost_entry.get()
    weight = weight_entry.get()

    try:
        with open("../data/shipments.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([origin, destination, cost, weight])
        messagebox.showinfo("Success", "✅ Shipment saved to CSV!")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Error saving: {str(e)}")

    reset_form()

def view_shipments():
    try:
        table = tk.Toplevel(root)
        table.title("Shipment History")

        with open("../data/shipments.csv", newline='') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                for j, value in enumerate(row):
                    tk.Label(table, text=value, relief="ridge", width=18).grid(row=i, column=j)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open shipment history: {str(e)}")

def reset_form():
    origin_entry.delete(0, tk.END)
    destination_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    cost_entry.delete(0, tk.END)
    distance_var.set("")
    rate_entry.delete(0, tk.END)
    rate_entry.insert(0, "0.25")
    selected_port.set(port_list[0])
    selected_dest_port.set(port_list[1])

def open_map():
    webbrowser.open(f"file://{map_path}")

def use_selected_port():
    origin_entry.delete(0, tk.END)
    origin_entry.insert(0, selected_port.get())
    update_distance()

def use_selected_dest_port():
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, selected_dest_port.get())
    update_distance()

def update_distance():
    origin_name = origin_entry.get()
    dest_name = destination_entry.get()
    if origin_name and dest_name:
        try:
            o = port_df[port_df["Port"] == origin_name].iloc[0]
            d = port_df[port_df["Port"] == dest_name].iloc[0]
            dist = haversine(o["Latitude"], o["Longitude"], d["Latitude"], d["Longitude"])
            distance_var.set(f"{dist:.2f} km")
            update_cost()
        except Exception as e:
            distance_var.set("N/A")
            print(f"Error calculating distance: {e}")

def update_cost():
    try:
        distance_str = distance_var.get().replace(" km", "")
        distance = float(distance_str)
        weight = float(weight_entry.get())
        rate = float(rate_entry.get())
        total_cost = distance * weight * rate
        cost_entry.delete(0, tk.END)
        cost_entry.insert(0, f"{total_cost:.2f}")
    except Exception as e:
        print("Couldn't calculate cost:", e)

# === UI Components ===
tk.Button(root, text="🌍 Open Port Map", command=open_map, bg='lightblue', font=("Helvetica", 12)).pack(pady=10)
tk.Button(root, text="📄 View Shipment History", command=view_shipments, bg="purple", fg="white").pack(pady=5)

tk.Label(root, text="📦 Enter Shipment Info", font=('Helvetica', 14, 'bold')).pack(pady=10)

# ORIGIN
tk.Label(root, text="Origin Port:").pack()
origin_entry = tk.Entry(root)
origin_entry.pack()

tk.Label(root, text="Select Port for Origin:").pack()
selected_port = tk.StringVar()
selected_port.set(port_list[0])
port_menu = tk.OptionMenu(root, selected_port, *port_list)
port_menu.pack()
tk.Button(root, text="Use Selected Port as Origin", command=use_selected_port, bg='orange').pack(pady=5)

# DESTINATION
tk.Label(root, text="Destination Port:").pack()
destination_entry = tk.Entry(root)
destination_entry.pack()

tk.Label(root, text="Select Port for Destination:").pack()
selected_dest_port = tk.StringVar()
selected_dest_port.set(port_list[1])
dest_port_menu = tk.OptionMenu(root, selected_dest_port, *port_list)
dest_port_menu.pack()
tk.Button(root, text="Use Selected Port as Destination", command=use_selected_dest_port, bg='orange').pack(pady=5)

# WEIGHT
tk.Label(root, text="Weight (kg):").pack()
weight_entry = tk.Entry(root)
weight_entry.pack()
weight_entry.bind("<KeyRelease>", lambda event: update_cost())

# RATE
tk.Label(root, text="Rate ($/km/kg):").pack()
rate_entry = tk.Entry(root)
rate_entry.insert(0, "0.25")
rate_entry.pack()
rate_entry.bind("<KeyRelease>", lambda event: update_cost())

# DISTANCE
tk.Label(root, text="Distance (km):").pack()
distance_var = tk.StringVar()
distance_label = tk.Label(root, textvariable=distance_var)
distance_label.pack()

# COST
tk.Label(root, text="Cost (USD):").pack()
cost_entry = tk.Entry(root)
cost_entry.pack()

# ACTION BUTTONS
tk.Button(root, text="Submit Shipment", command=submit_shipment, bg="green", fg="white").pack(pady=10)
tk.Button(root, text="Reset Form", command=reset_form, bg="gray", fg="white").pack(pady=5)

root.mainloop()


