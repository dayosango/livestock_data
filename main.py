"""

Generate the following:
- Animals
    - Birth and Death dates (with sites)
- Sites
    - And corresponding Locations
- Vehicles
    - Just registrations for now
- Journeys (and Batches)
    - Select random site
    - Shortlist moveable animals
    - Take random selection and move into batch
    - Create journey instance and assign vehicle before moving to appropriate site
    - Remove animals from batch

    
TODO:
- create ownership concept, so animals can be sold and transferred between keepers (and they can report movements)
- create a "size" variable for sites. So we can have small farms vs mega farms, high traffic low traffic etc.
    - size should also increase likelihood animals are moved to/from there
- animals should have to be at a slaughterhouse to have the slaughtered death event

"""

import pandas as pd
import random
from datetime import datetime, timedelta

# Creating the final dataframe (empty)
headers = ["animal_id", "sex", "species", "site_id", "site_type", "location_id", "easting", "northing", "date_of_birth", "date_of_death", "death_site_id", "reason_for_death", "batch_id", "date_added_to_batch", "date_removed_from_batch", "vehicle_reg", "journey_id", "journey_origin", "journey_destination", "journey_start_date", "journey_end_date"]
df = pd.DataFrame(columns=headers)

####################
###### CONFIG ######
####################

# How many of each animal?
animal_config = {
    "cow": 40,
    "pig": 75,
    "sheep": 100
}

# How many of each site?
site_config = {
    "farm": 5,
    "market": 2,
    "slaughterhouse": 2
}

# Number of vehicles and journeys
number_of_vehicles = 8
number_of_journeys = 50


# Dates config
birth_start_date = datetime(2010, 1, 1)  # Start date for births that will increase by 1-3 days randomly
death_start_date = datetime(2011, 1, 1)  # Start date for births that will increase by 1-3 days randomly



#######################
## Animal Generation ##
#######################

animals_df = pd.DataFrame(columns=["animal_id", "sex", "species"])

id = 1  # Starting ID
for animal_species in animal_config.keys():
    for _ in range(animal_config[animal_species]):
        new_row = {"animal_id": f"animal_{id}",
                   "sex": random.choice(["m", "f"]),
                   "species": animal_species}
        id += 1
        
        animals_df = animals_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(animals_df)


#######################
### Site Generation ###
#######################

sites_df = pd.DataFrame(columns=["site_id", "site_type", "location_id", "easting", "northing"])

id = 1  # Starting ID
for site_type in site_config.keys():
    for _ in range(site_config[site_type]):
        new_row = {"site_id": f"site_{id}",
                   "site_type": site_type, 
                   "location_id": f"loc_{id}", 
                   "easting": f"44{random.randint(100, 999)}", 
                   "northing": f"20{random.randint(100, 999)}"}
        id += 1
        
        sites_df = sites_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(sites_df)



##########################
### Vehicle Generation ###
##########################

# Hardcoded reg plates for now, there is another file called reg_gen that creates them
vehicles_dict = {"vehicle_reg": ["WB23964", "XW23940", "HL23445", "BG23024", "NP23422",
                                 "HK23967", "EI23649", "VR23403", "VM23859", "OW23921"]}
vehicles_df = pd.DataFrame(data=vehicles_dict)

# Appending to the main dataframe
df = df._append(vehicles_df, ignore_index=True)




########################
### Birth Generation ###
########################

births_df = pd.DataFrame(columns=["date_of_birth", "animal_id", "site_id"])
birth_date = birth_start_date

for animal_id in df["animal_id"][df["animal_id"].notnull()].unique():
    birth_date += timedelta(days=random.randint(1, 3))
    new_row = {"date_of_birth": birth_date,
            "animal_id": animal_id,
            "site_id": random.choice(df.loc[df['site_type'] == 'farm', 'site_id'].tolist())}
        
    births_df = births_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(births_df)




########################
### Death Generation ###
########################

# Generate deaths for 30% of animals
deaths_df = pd.DataFrame(columns=["date_of_death", "reason_for_death", "animal_id", "death_site_id"])
death_date = death_start_date

for animal_id in df["animal_id"][df["animal_id"].notnull()].unique():
    death_date += timedelta(days=random.randint(1, 3))
    if random.randint(1, 10) < 4:
        new_row = {"date_of_death": death_date,
               "reason_for_death": random.choice(["slaughter", "illness"]),
               "animal_id": animal_id,
               "death_site_id": random.choice(df.loc[df['site_type'] == 'slaughterhouse', 'site_id'].tolist())}
            
        deaths_df = deaths_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(deaths_df)






##########################
### Journey Generation ###
##########################

"""
1. Randomly select origin site and destination site
2. Select eligible animals from origin site
3. Put the animals in a batch
4. Create journey instance and assign variables
5. Remove animals from the batch post-journey
"""

# Resetting the index of the main dataframe
df = df.reset_index(drop=True)



### FUNCTIONS ###

# Select origin and destination sites
def select_origin():
    origin_site = random.choice(df["site_id"][df["site_id"].notnull()].unique())
    return origin_site


# Determine which animals are alive
def alive_animals():
    # for each animal determine if still alive
    all_animals = df["animal_id"].unique()
    dead_animals = df.loc[df["date_of_death"].notnull(), "animal_id"].unique()

    # Convert both Series to sets
    all_animals_set = set(all_animals)
    dead_animals_set = set(dead_animals)
    # Calculate the set difference
    alive_animals_set = all_animals_set - dead_animals_set
    # Convert the result set back to a Series
    return pd.Series(list(alive_animals_set)).dropna()


# Of the alive animals, determine which are at the provided site
def animals_at_site(site):
    # Find most recent journey end date
    alive_animals_df = df[df['animal_id'].isin(alive_animals())]

    # Convert 'journey_end_date' to datetime
    alive_animals_df.loc['journey_end_date'] = pd.to_datetime(alive_animals_df['journey_end_date'])

    # Sort DataFrame by 'animal_id' and 'journey_end_date'
    alive_animals_df_sorted = alive_animals_df.sort_values(by=['animal_id', 'journey_end_date'])
    # earliest_start_date = alive_animals_df_sorted['journey_end_date'].max()  TODO fix this?

    # Keep only the latest row for each unique value in 'animal_id'
    animals_latest_site = alive_animals_df_sorted.groupby('animal_id').tail(1)

    # Filter for the site we want
    filtered_animals_site = animals_latest_site[animals_latest_site["site_id"] == site]
    return filtered_animals_site["animal_id"]


# Select a random site of the selected type
def select_destination(chosen_type):
    possible_sites = df[df["site_type"] == chosen_type]
    return random.choice(possible_sites["site_id"].to_list())


# Create a batch for the animals to complete the journey within
def create_batch(batch_id, animals_to_be_moved, journey_start_date):
    batch_df = pd.DataFrame(columns=["batch_id", "animal_id", "date_added_to_batch"])

    for animal_id in animals_to_be_moved:
        new_row = {
            "batch_id": batch_id,
            "animal_id": animal_id,
            "date_added_to_batch": journey_start_date
        }

        batch_df = batch_df._append(new_row, ignore_index=True)
    
    return batch_df


# Create the journey and "move" the animals. Then remove them from the batch
def create_journey_remove_batch(journey_id, batch_id, animals_to_be_moved, journey_start_date, journey_end_date):
    journey_df = pd.DataFrame(columns=["journey_id", "journey_origin", "journey_destination", "journey_start_date", "journey_end_date", "vehicle_reg", "batch_id"])

    new_row = {
        "journey_id": journey_id,
        "journey_origin": origin_site,
        "journey_destination": destination_site,
        "journey_start_date": journey_start_date,
        "journey_end_date": journey_end_date,
        "vehicle_reg": random.choice(df.loc[df['vehicle_reg'].notnull(), 'vehicle_reg'].tolist()),
        "batch_id": batch_id
    }

    journey_df = journey_df._append(new_row, ignore_index=True)

    # Take animals out of batch
    remove_batch_df = pd.DataFrame(columns=["batch_id", "animal_id", "date_removed_from_batch"])

    for animal_id in animals_to_be_moved:
        new_row = {
            "batch_id": batch_id,
            "animal_id": animal_id,
            "date_removed_from_batch": journey_end_date
        }

        remove_batch_df = remove_batch_df._append(new_row, ignore_index=True)
    
    return journey_df, remove_batch_df



# Each iteration of this code creates 1 journey
journey_start_date = birth_start_date + timedelta(days=500)

for i in range(number_of_journeys):

    # Select origin site randomly
    origin_site = select_origin()

    # Shortlist animals eligible for journey
    candidate_animals = animals_at_site(origin_site)

    # while len(candidate_animals) < 1: TODO fix it so we cant do empty journeys
    #     origin_site = select_origin()
    #     candidate_animals = animals_at_site(origin_site)

    #     print(origin_site)
    #     print(candidate_animals)
    #     print(len(candidate_animals))

    # Take a selection of the animals available at the site
    animals_to_be_moved = candidate_animals.sample(frac=0.7, random_state=42)

    # Determine destination site based on journey purpose
    destination_types = list(site_config.keys())
    chosen_type = random.choice(destination_types)

    destination_site = select_destination(chosen_type)

    # allow 4-7 days to pass between each journey
    journey_start_date += timedelta(days=random.randint(4, 7))

    # put the chosen animals into a batch and assign start date
    batch_df = create_batch(i, animals_to_be_moved, journey_start_date)
    df = df._append(batch_df)


    # create the journey instance and assign origin, destination, start and end dates, batch, vehicle
    journey_end_date = journey_start_date + timedelta(days=random.randint(1, 3))

    journey_df, remove_batch_df = create_journey_remove_batch(i, i, animals_to_be_moved, journey_start_date, journey_end_date)
    df = df._append(journey_df)
    df = df._append(remove_batch_df)

    df = df.reset_index(drop=True)




file_name = "my_dataframe.csv"
df.to_csv(file_name, index=False)
print("dataframe written to csv")
